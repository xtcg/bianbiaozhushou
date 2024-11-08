#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/24 14:25
# @File    : examples.py
# @Software: PyCharm
import random

summary_keys = ['项目名称', '项目业主', '项目概况', '建设地点', '计划工期', '质量标准', '最高投标限价', '投标文件递交',
                '招标范围', '资质要求', '业绩要求', '人员、财务与信誉要求', '其他要求', '踏勘现场', '最高投标限价',
                '摘要内容-评标办法', '审查内容-评标办法', '罚则', '标段名称', '招标编号', '项目编号',
                '招标文件获取时间', '投标文件截止时间', '相关行业', '安全', '人员数量要求']

summary_examples = [
    [
        {"section": x, "ai_result": f"模型抽取信息（{x}）", "reference": {"location": f"第X章 {x} 第X页"}}
        for x in summary_keys
    ]
]

review_keys = ['项目名称一致性', '项目名称符合性', '项目业主一致性', '项目业主符合性', '标段名称一致性',
               '标段名称符合性', '项目编号一致性', '项目编号符合性', '招标编号一致性', '招标编号符合性', '工期一致性',
               '工期符合性', '质量', '安全', '落款日期一致性', '落款日期符合性', '不相关地点', '不相关行业', '报价唯一',
               '人员要求']

review_examples = [
    
        {
            "section": x,
            "ai_result": f"模型分析信息（{x}）",
            "conclusion": random.choice(["符合", "不符合"]),
            "tender_reference": {"location": ""},
            "bid_reference": {"content":[{"page":4,"content":"info"}]},
        } for x in review_keys
    
]
