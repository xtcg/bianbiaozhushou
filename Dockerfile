FROM registry.baidubce.com/paddlepaddle/paddle:2.6.1-gpu-cuda12.0-cudnn8.9-trt8.6

# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /models

COPY models/ch_PP-OCRv4_det_infer ch_PP-OCRv4_det_infer
COPY models/ch_ppocr_mobile_v2.0_cls_infer ch_ppocr_mobile_v2.0_cls_infer
COPY models/ch_PP-OCRv4_rec_infer ch_PP-OCRv4_rec_infer

WORKDIR /code
COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple



