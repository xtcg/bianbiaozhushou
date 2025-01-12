#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/21 16:56
# @File    : schema.py
# @Software: PyCharm
from typing import List, Literal

from pydantic import BaseModel, Field

from api.examples import summary_examples, review_examples


class Reference(BaseModel):
    location: str = Field(description="对应页码")
    # content: str = Field(description="对应内容")

class Reference1(BaseModel):
    content: List[dict] = Field(description="对应内容")

class SummaryEntry(BaseModel):
    section: str = Field(description="对应抽取点")
    ai_result: str = Field(description="模型输出内容")
    reference: Reference = Field(description="关联内容")


class TenderSummaryBody(BaseModel):
    tender_file: str = Field(description="招标文件的存储ID", examples=["tender_file"])


class ResponseBase(BaseModel):
    bizId: str = Field(description="业务ID", examples=["bizId"])
    status: Literal["success", "error"] = Field(default="success", description="请求处理状态")


class TenderSummaryResponse(ResponseBase):
    summary_fileid: str = Field(description="摘要docx文件ID", examples=["summary_file_id"])
    summary: List[SummaryEntry] = Field(description="摘要信息", examples=summary_examples)
    comments_fileid: str = Field(description="加入批注的摘要docx文件ID", examples=["comment_file_id"])


class BidOutlineBody(BaseModel):
    tender_summary: List[SummaryEntry] = Field(description="投标文件摘要信息", examples=summary_examples)


class BidOutlineResponse(ResponseBase):
    outline_fileid: str = Field(description="投标文件大纲ID", examples=["outline_fileid"])


class ReviewEntry(BaseModel):
    section: str = Field(description="对应抽取点", examples=["安全"])
    ai_result: str = Field(description="模型的结论分析", examples=["模型分析信息（安全）"])
    conclusion: str = Field(description="内容是否一致的结论")
    tender_reference: Reference = Field(description="招标文件关联内容", examples=[{"location": "招标文件第X章 安全 第X页"}])
    bid_reference: Reference1 = Field(description="投标文件关联内容", examples=[{"content": [{"page":4,"content":"info"}]}])


class BidKeyReviewBody(BaseModel):
    tender_summary: List[SummaryEntry] = Field(description="投标文件摘要信息", examples=summary_examples)


class BidKeyReviewResponse(ResponseBase):
    key_censor_fileid: str = Field(description="关键审查docx文件ID", examples=["key_censor_fileid"])
    results: List[ReviewEntry] = Field(description="关键信息审查结论", examples=review_examples)
    key_comment_fileid: str = Field(description="关键审查docx批注文件ID", examples=["key_comment_fileid"])

class BidReqReviewBody(BaseModel):
    tender_summary: List[SummaryEntry] = Field(description="投标文件摘要信息", examples=summary_examples)


class BidReqReviewResponse(ResponseBase):
    requirement_censor_fileid: str = Field(description="要求审查docx文件ID", examples=["requirement_censor_fileid"])
    results: List[ReviewEntry] = Field(description="要求审查结果（审查点根据招标文件确定）")
    requirement_comment_fileid: str = Field(description="要求审查docx批注文件ID", examples=["requirement_comment_fileid"])
