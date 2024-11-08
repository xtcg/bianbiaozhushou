import logging
import os
from functools import lru_cache
from pathlib import Path

import uvicorn
from fastapi import FastAPI
import numpy as np
from transformers import AutoTokenizer
import onnxruntime as ort

from embedding_app.schema import EmbeddingBody
# from utils.common import init_logging

# init_logging(debug=os.environ.get("debug") == "true")

app = FastAPI()

logger = logging.getLogger(__name__)

BASEDIR = Path(__file__).absolute().parent.parent


# @lru_cache(None)
def get_tokenizer():
    tokenizer_path = os.environ.get("TOKENIZER_PATH", BASEDIR.joinpath('embedding_model/jina-embeddings-v2-base-zh'))
    return AutoTokenizer.from_pretrained(tokenizer_path)


# @lru_cache(None)
def get_model_session():
    model_path = os.environ.get("MODEL_PATH", BASEDIR.joinpath('embedding_model/model_fp16.onnx'))
    sess_opt = ort.SessionOptions()
    sess_opt.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    sess_opt.enable_cpu_mem_arena = False
    sess_opt.enable_mem_pattern = False
    sess_opt.enable_mem_reuse = False
    # sess_opt.intra_op_num_threads = 1
    # sess_opt.inter_op_num_threads = 1
    return ort.InferenceSession(model_path, sess_options=sess_opt, providers=['CPUExecutionProvider'])


def mean_pooling(model_output, attention_mask):
    # This function can remain mostly unchanged, just made async
    # Convert necessary operations to their asynchronous counterparts if available
    token_embeddings = model_output
    input_mask_expanded = np.broadcast_to(np.expand_dims(attention_mask, axis=-1), token_embeddings.shape)
    return np.sum(token_embeddings * input_mask_expanded, 1) / np.clip(
        input_mask_expanded.sum(1), a_max=None, a_min=1e-9
    )


def run_onnx_session(session, input_feed):
    # loop = asyncio.get_running_loop()
    # # Run the synchronous session.run in a thread pool to avoid blocking the event loop
    # result = loop.run_in_executor(
    #     executor, lambda: session.run(output_names=["last_hidden_state"], input_feed=input_feed)
    # )
    # return result
    # return run_in_threadpool(session.run, output_names=["last_hidden_state"], input_feed=input_feed)
    return session.run(output_names=["last_hidden_state"], input_feed=input_feed)


@app.post('/api/v2/embed_onnx', )
def embed_onnx(
        body: EmbeddingBody,
):
    if not body.text:
        logger.info("请求中未包含文本！")
        return []
    logger.info("Start Tokenizer!")
    tokenizer = get_tokenizer()
    inputs = tokenizer(body.text, return_tensors="np", padding=True, truncation=True)

    logger.info("Start Embedding!")
    batch_size = body.batch_size
    if batch_size is None:
        batch_size = inputs['input_ids'].shape[0]
    total_batches = np.ceil(inputs['input_ids'].shape[0] / batch_size).astype(int)

    session = get_model_session()
    session.disable_fallback()
    outputs_list = []
    for i in range(total_batches):
        inputs_batch = {
            'input_ids': inputs['input_ids'][i * batch_size: (i + 1) * batch_size].astype(np.int64)
        }
        if 'attention_mask' in inputs:
            inputs_batch['attention_mask'] = inputs['attention_mask'][i * batch_size: (i + 1) * batch_size].astype(
                np.int64
            )
        outputs = run_onnx_session(session, inputs_batch)
        del session, inputs_batch
        outputs_list.append(outputs[0])
    final_output = np.concatenate(outputs_list, axis=0)

    logger.info("Mean Pooling!")
    embeddings = mean_pooling(final_output, inputs['attention_mask'])
    return embeddings.tolist()


if __name__ == '__main__':
    uvicorn.run(app, port=50086)
