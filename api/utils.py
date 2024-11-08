#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/24 09:57
# @File    : utils.py
# @Software: PyCharm
import hashlib
import logging
import mimetypes
from pathlib import Path
from typing import Tuple

import aiofile
import asgi_correlation_id
from httpx import AsyncClient, HTTPStatusError

from .config import FILE_HUB_URL, DEFAULT_FILE_PATH

logger = logging.getLogger(__name__)

_default_format = "[%(asctime)s] [%(levelname)7s] [%(correlation_id)s] [%(funcName)s - %(module)s:%(lineno)d] %(message)s"


def init_logging(_format=_default_format, set_request_id: bool = True, formatter_cls=logging.Formatter, debug=False):
    formatter = formatter_cls(_format)

    handlers = []
    if set_request_id:
        request_handler = logging.StreamHandler()
        request_handler.setFormatter(formatter)
        request_handler.addFilter(asgi_correlation_id.CorrelationIdFilter(uuid_length=32, default_value="-"))
        handlers.append(request_handler)

    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG,
        handlers=handlers,
        force=True
    )


FILE_HUB = AsyncClient(base_url=FILE_HUB_URL, timeout=360)


async def fetch_biz_file(bizId, biz_type, temp_path) -> Tuple[Path, str]:
    fetch_api = f"/api/bidding-assistant/thirdSystem/download/{bizId}/{biz_type}"
    response = await FILE_HUB.get(fetch_api)
    try:
        response.raise_for_status()
    except HTTPStatusError as e:
        logging.error(f"Error in Fetch File, {bizId = },{biz_type = }, {e = }")
    filename = f"{biz_type}.docx"
    filepath = temp_path.joinpath(filename)

    data = b""
    logger.info(f"Save {bizId}/{biz_type} to {filepath}")
    async with aiofile.AIOFile(filepath, "wb") as f:
        writer = aiofile.Writer(f)
        async for chunk in response.aiter_bytes(4096):
            await writer(chunk)
            data += chunk
    return filepath, hashlib.md5(data).hexdigest()


async def upload_biz_file(bizId, biz_type, file_path) -> str:
    file_path = Path(file_path)
    upload_api = f"/api/bidding-assistant/thirdSystem/upload/{bizId}/{biz_type}"
    async with aiofile.AIOFile(file_path, "rb") as f:
        file_data = await f.read()
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    response = await FILE_HUB.post(upload_api, files={'file': (file_path.name, file_data, content_type)})
    try:
        response.raise_for_status()
    except HTTPStatusError as e:
        logging.error(f"Error in Upload File, {bizId = },{biz_type = }, {e = }")
    data = response.json()
    try:
        file_id = data["data"]["fileId"]
    except Exception as e:
        logger.error(f"Failed to Upload file, response: {response.json()}")
        raise e
    return file_id


def get_temp_path(biz_type):
    def temp_path(bizId: str):
        _path = DEFAULT_FILE_PATH.joinpath(f"{bizId}/{biz_type}")
        if not _path.exists():
            _path.mkdir(parents=True, exist_ok=True)
        return _path

    return temp_path


if __name__ == '__main__':
    import asyncio
    # DEFAULT_FILE_PATH = '/home/ron/jiamin/bianbiaozhushou/data'
    logging.basicConfig(level=logging.INFO)
    bizId = "2f8c5f2fdb6d4273bf43f13d5019496c"
    biz_type = "outline"
    file_path = "/home/ron/jiamin/bianbiaozhushou/data/已脱敏浙江金华招标文件/outline_doc.docx"
    result = asyncio.run(upload_biz_file(bizId, biz_type, file_path))
    # result = asyncio.run(fetch_biz_file("456", "bid", DEFAULT_FILE_PATH))
    print(result)
