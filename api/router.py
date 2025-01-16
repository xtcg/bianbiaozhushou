#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/22 16:00
# @File    : router.py
# @Software: PyCharm
import asyncio
import json
import logging
from typing import Annotated, TypeVar

from fastapi import APIRouter, Path, Depends
from starlette.concurrency import run_in_threadpool

from api import schema
from api.config import DEFAULT_FILE_PATH, DEFAULT_CACHE_PATH
from api.utils import fetch_biz_file, upload_biz_file, get_temp_path
from core.docx_test import generate_abstract, generate_key_content_check, generate_bid_content_check, generate_outline


router = APIRouter(
    tags=["一期"]
)

BizID = TypeVar("BizID", bound=str)

logger = logging.getLogger(__name__)


@router.post(
    "/{bizId}/summary",
    summary="招标文件的摘要信息抽取",
    response_model=schema.TenderSummaryResponse,
)
async def generate_bid_doc_summary(
    bizId: Annotated[BizID, Path(title="业务ID", description="业务ID")],
    temp_path: Annotated[Path, Depends(get_temp_path("summary"))],
):
    logger.info(f"Start Summary for {bizId = }")
    tender_pdf_path, file_hash = await fetch_biz_file(bizId=bizId, biz_type="tender", temp_path=temp_path)
    cache_path = DEFAULT_CACHE_PATH.joinpath(file_hash)
    summary, summary_docx_path, comments_docx_path = await asyncio.wait_for(
        run_in_threadpool(
            generate_abstract, str(tender_pdf_path), temp_path=str(temp_path), cache_path=str(cache_path)
        ),
        timeout=10 * 60
    )
    summary_fileid = await upload_biz_file(bizId=bizId, biz_type="summary", file_path=summary_docx_path)
    comments_fileid = await upload_biz_file(bizId=bizId, biz_type="comment", file_path=comments_docx_path)
    # DEBUG
    with open(temp_path.joinpath("result.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return schema.TenderSummaryResponse(
        bizId=bizId,
        summary_fileid=summary_fileid,
        summary=summary,
        comments_fileid=comments_fileid,
    )


@router.post(
    "/{bizId}/outline",
    summary="投标文件大纲生成",
    response_model=schema.BidOutlineResponse,
)
async def generate_tender_doc_outline(
    bizId: Annotated[BizID, Path(title="业务ID", description="业务ID")],
    temp_path: Annotated[Path, Depends(get_temp_path("outline"))],
    # body: schema.BidOutlineBody
):
    logger.info(f"Start Outline for {bizId = }")
    tender_pdf_path, file_hash = await fetch_biz_file(bizId=bizId, biz_type="tender", temp_path=temp_path)
    cache_path = DEFAULT_CACHE_PATH.joinpath(file_hash)
    outline_docx_path = await asyncio.wait_for(
        run_in_threadpool(generate_outline, str(tender_pdf_path), temp_path=str(temp_path), cache_path=str(cache_path)),
        timeout=10 * 60
    )
    outline_fileid = await upload_biz_file(bizId=bizId, biz_type="outline", file_path=outline_docx_path)
    return schema.BidOutlineResponse(outline_fileid=outline_fileid, bizId=bizId)


@router.post(
    "/{bizId}/censor/key",
    summary="投标文件审查-关键信息审查",
    response_model=schema.BidKeyReviewResponse,
)
async def review_key_in_tender_doc(
    bizId: Annotated[BizID, Path(title="业务ID", description="业务ID")],
    body: schema.BidKeyReviewBody,
    temp_path: Annotated[Path, Depends(get_temp_path("censor_key"))],
):
    bid_pdf_path, file_hash = await fetch_biz_file(bizId, biz_type="bid", temp_path=temp_path)
    cache_path = DEFAULT_CACHE_PATH.joinpath(file_hash)
    results, censor_docx_path, comments_docx_path = await asyncio.wait_for(
        run_in_threadpool(
            generate_key_content_check,
            tender_list=[x.model_dump() for x in body.tender_summary],
            bid_pdf_path=str(bid_pdf_path),
            temp_path=str(temp_path),
            cache_path=str(cache_path)
        ),
        timeout=10 * 60
    )
    key_censor_fileid = await upload_biz_file(bizId, biz_type="censor_key", file_path=censor_docx_path)
    key_comment_fileid = await upload_biz_file(bizId, biz_type="censor_key", file_path=comments_docx_path)
    return schema.BidKeyReviewResponse(
        bizId=bizId,
        key_censor_fileid=key_censor_fileid,
        results=results,
        key_comment_fileid=key_comment_fileid
    )


@router.post(
    "/{bizId}/censor/requirement",
    summary="投标文件审查-符合招标文件要求审查",
    response_model=schema.BidReqReviewResponse,
)
async def review_requirement_in_tender_doc(
    bizId: Annotated[BizID, Path(title="业务ID", description="业务ID")],
    body: schema.BidReqReviewBody,
    temp_path: Annotated[Path, Depends(get_temp_path("censor_req"))],
):
    bid_pdf_path, file_hash = await fetch_biz_file(bizId, biz_type="bid", temp_path=temp_path)
    cache_path = DEFAULT_CACHE_PATH.joinpath(file_hash)
    results, censor_docx_path, comments_docx_path = await asyncio.wait_for(
        run_in_threadpool(
            generate_bid_content_check,
            tender_list=[x.model_dump() for x in body.tender_summary],
            bid_pdf_path=str(bid_pdf_path),
            temp_path=str(temp_path),
            cache_path=str(cache_path),
        ),
        timeout=10 * 60
    )
    requirement_censor_fileid = await upload_biz_file(bizId, biz_type="censor_req", file_path=censor_docx_path)
    requirement_comment_fileid = await upload_biz_file(bizId, biz_type="censor_req", file_path=comment_docx_path)
    return schema.BidReqReviewResponse(
        bizId=bizId,
        requirement_censor_fileid=requirement_censor_fileid,
        results=results,
        requirement_comment_fileid=requirement_comment_fileid
    )
