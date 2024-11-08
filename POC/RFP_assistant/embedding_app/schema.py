#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/3/20 11:09
# @File    : schema.py
# @Software: PyCharm
from typing import List, Optional

from pydantic import BaseModel, Field


class EmbeddingBody(BaseModel):
    text: List[str]
    batch_size: Optional[int] = Field(default=None)
