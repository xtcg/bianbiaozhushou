#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/21 16:56
# @File    : app.py
# @Software: PyCharm
import os

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api import router
from api.utils import init_logging

init_logging(debug=os.environ.get("DEBUG") == "true")

app = FastAPI(
    title="编标助手算法服务",
    version="0.0.1",
    description="""
+ 为了方便追踪请求，可以在请求头中加入x-request-id(格式:UUID)
""",

)
app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的域名列表
    allow_credentials=True,  # 允许在跨域请求中使用凭证（如Cookie）
    allow_methods=["*"],  # 允许的请求方法列表，这里使用通配符表示支持所有方法
    allow_headers=["*"],  # 允许的请求头列表，这里使用通配符表示支持所有头部字段
    # Indicate which headers can be exposed as part of the response to a browser
    expose_headers=["X-Request-Id"],
)

app.include_router(router.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)
