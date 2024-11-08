FROM python:3.11-slim

WORKDIR /model
COPY jina-embeddings-v2-base-zh jina-embeddings-v2-base-zh
ENV TOKENIZER_PATH=/model/jina-embeddings-v2-base-zh
COPY model_fp16.onnx model_fp16.onnx
ENV MODEL_PATH=/model/model_fp16.onnx

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

WORKDIR /code

