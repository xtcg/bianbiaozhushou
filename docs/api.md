---
title: 编标助手算法服务 v0.0.1
language_tabs:
  - shell: Shell
  - http: HTTP
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 3

---

<!-- Generator: Widdershins v4.0.1 -->

<h1 id="-">编标助手算法服务 v0.0.1</h1>

> Scroll down for code samples, example requests and responses. Select a language for code samples from the tabs above or the mobile navigation menu.

+ 为了方便追踪请求，可以在请求头中加入x-request-id(格式:UUID)

<h1 id="---">一期</h1>

## 招标文件的摘要信息抽取

<a id="opIdgenerate_bid_doc_summary__bizId__summary_post"></a>

> Code samples

```shell
curl --request POST \
  --url https://example.com/{bizId}/summary \
  --header 'Accept: application/json'
```

```http
POST /{bizId}/summary HTTP/1.1
Accept: application/json
Host: example.com

```

`POST /{bizId}/summary`

<h3 id="招标文件的摘要信息抽取-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|bizId|path|string|true|业务ID|

> Example responses

> 200 Response

```json
{
  "bizId": "bizId",
  "status": "success",
  "summary_fileid": "summary_file_id",
  "summary": [
    {
      "ai_result": "模型抽取信息（项目名称）",
      "reference": {
        "location": "第X章 项目名称 第X页"
      },
      "section": "项目名称"
    },
    {
      "ai_result": "模型抽取信息（项目业主）",
      "reference": {
        "location": "第X章 项目业主 第X页"
      },
      "section": "项目业主"
    },
    {
      "ai_result": "模型抽取信息（项目概况）",
      "reference": {
        "location": "第X章 项目概况 第X页"
      },
      "section": "项目概况"
    },
    {
      "ai_result": "模型抽取信息（建设地点）",
      "reference": {
        "location": "第X章 建设地点 第X页"
      },
      "section": "建设地点"
    },
    {
      "ai_result": "模型抽取信息（计划工期）",
      "reference": {
        "location": "第X章 计划工期 第X页"
      },
      "section": "计划工期"
    },
    {
      "ai_result": "模型抽取信息（质量标准）",
      "reference": {
        "location": "第X章 质量标准 第X页"
      },
      "section": "质量标准"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（投标文件递交）",
      "reference": {
        "location": "第X章 投标文件递交 第X页"
      },
      "section": "投标文件递交"
    },
    {
      "ai_result": "模型抽取信息（招标范围）",
      "reference": {
        "location": "第X章 招标范围 第X页"
      },
      "section": "招标范围"
    },
    {
      "ai_result": "模型抽取信息（资质要求）",
      "reference": {
        "location": "第X章 资质要求 第X页"
      },
      "section": "资质要求"
    },
    {
      "ai_result": "模型抽取信息（业绩要求）",
      "reference": {
        "location": "第X章 业绩要求 第X页"
      },
      "section": "业绩要求"
    },
    {
      "ai_result": "模型抽取信息（人员、财务与信誉要求）",
      "reference": {
        "location": "第X章 人员、财务与信誉要求 第X页"
      },
      "section": "人员、财务与信誉要求"
    },
    {
      "ai_result": "模型抽取信息（其他要求）",
      "reference": {
        "location": "第X章 其他要求 第X页"
      },
      "section": "其他要求"
    },
    {
      "ai_result": "模型抽取信息（踏勘现场）",
      "reference": {
        "location": "第X章 踏勘现场 第X页"
      },
      "section": "踏勘现场"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（摘要内容-评标办法）",
      "reference": {
        "location": "第X章 摘要内容-评标办法 第X页"
      },
      "section": "摘要内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（审查内容-评标办法）",
      "reference": {
        "location": "第X章 审查内容-评标办法 第X页"
      },
      "section": "审查内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（罚则）",
      "reference": {
        "location": "第X章 罚则 第X页"
      },
      "section": "罚则"
    },
    {
      "ai_result": "模型抽取信息（标段名称）",
      "reference": {
        "location": "第X章 标段名称 第X页"
      },
      "section": "标段名称"
    },
    {
      "ai_result": "模型抽取信息（招标编号）",
      "reference": {
        "location": "第X章 招标编号 第X页"
      },
      "section": "招标编号"
    },
    {
      "ai_result": "模型抽取信息（项目编号）",
      "reference": {
        "location": "第X章 项目编号 第X页"
      },
      "section": "项目编号"
    },
    {
      "ai_result": "模型抽取信息（招标文件获取时间）",
      "reference": {
        "location": "第X章 招标文件获取时间 第X页"
      },
      "section": "招标文件获取时间"
    },
    {
      "ai_result": "模型抽取信息（投标文件截止时间）",
      "reference": {
        "location": "第X章 投标文件截止时间 第X页"
      },
      "section": "投标文件截止时间"
    },
    {
      "ai_result": "模型抽取信息（相关行业）",
      "reference": {
        "location": "第X章 相关行业 第X页"
      },
      "section": "相关行业"
    },
    {
      "ai_result": "模型抽取信息（安全）",
      "reference": {
        "location": "第X章 安全 第X页"
      },
      "section": "安全"
    },
    {
      "ai_result": "模型抽取信息（人员数量要求）",
      "reference": {
        "location": "第X章 人员数量要求 第X页"
      },
      "section": "人员数量要求"
    }
  ]
}
```

<h3 id="招标文件的摘要信息抽取-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[TenderSummaryResponse](#schematendersummaryresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## 投标文件大纲生成

<a id="opIdgenerate_tender_doc_outline__bizId__outline_post"></a>

> Code samples

```shell
curl --request POST \
  --url https://example.com/{bizId}/outline \
  --header 'Accept: application/json'
```

```http
POST /{bizId}/outline HTTP/1.1
Accept: application/json
Host: example.com

```

`POST /{bizId}/outline`

<h3 id="投标文件大纲生成-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|bizId|path|string|true|业务ID|

> Example responses

> 200 Response

```json
{
  "bizId": "bizId",
  "status": "success",
  "outline_fileid": "outline_fileid"
}
```

<h3 id="投标文件大纲生成-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[BidOutlineResponse](#schemabidoutlineresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## 投标文件审查-关键信息审查

<a id="opIdreview_key_in_tender_doc__bizId__censor_key_post"></a>

> Code samples

```shell
curl --request POST \
  --url https://example.com/{bizId}/censor/key \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{"tender_summary":[{"ai_result":"模型抽取信息（项目名称）","reference":{"location":"第X章 项目名称 第X页"},"section":"项目名称"},{"ai_result":"模型抽取信息（项目业主）","reference":{"location":"第X章 项目业主 第X页"},"section":"项目业主"},{"ai_result":"模型抽取信息（项目概况）","reference":{"location":"第X章 项目概况 第X页"},"section":"项目概况"},{"ai_result":"模型抽取信息（建设地点）","reference":{"location":"第X章 建设地点 第X页"},"section":"建设地点"},{"ai_result":"模型抽取信息（计划工期）","reference":{"location":"第X章 计划工期 第X页"},"section":"计划工期"},{"ai_result":"模型抽取信息（质量标准）","reference":{"location":"第X章 质量标准 第X页"},"section":"质量标准"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（投标文件递交）","reference":{"location":"第X章 投标文件递交 第X页"},"section":"投标文件递交"},{"ai_result":"模型抽取信息（招标范围）","reference":{"location":"第X章 招标范围 第X页"},"section":"招标范围"},{"ai_result":"模型抽取信息（资质要求）","reference":{"location":"第X章 资质要求 第X页"},"section":"资质要求"},{"ai_result":"模型抽取信息（业绩要求）","reference":{"location":"第X章 业绩要求 第X页"},"section":"业绩要求"},{"ai_result":"模型抽取信息（人员、财务与信誉要求）","reference":{"location":"第X章 人员、财务与信誉要求 第X页"},"section":"人员、财务与信誉要求"},{"ai_result":"模型抽取信息（其他要求）","reference":{"location":"第X章 其他要求 第X页"},"section":"其他要求"},{"ai_result":"模型抽取信息（踏勘现场）","reference":{"location":"第X章 踏勘现场 第X页"},"section":"踏勘现场"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（摘要内容-评标办法）","reference":{"location":"第X章 摘要内容-评标办法 第X页"},"section":"摘要内容-评标办法"},{"ai_result":"模型抽取信息（审查内容-评标办法）","reference":{"location":"第X章 审查内容-评标办法 第X页"},"section":"审查内容-评标办法"},{"ai_result":"模型抽取信息（罚则）","reference":{"location":"第X章 罚则 第X页"},"section":"罚则"},{"ai_result":"模型抽取信息（标段名称）","reference":{"location":"第X章 标段名称 第X页"},"section":"标段名称"},{"ai_result":"模型抽取信息（招标编号）","reference":{"location":"第X章 招标编号 第X页"},"section":"招标编号"},{"ai_result":"模型抽取信息（项目编号）","reference":{"location":"第X章 项目编号 第X页"},"section":"项目编号"},{"ai_result":"模型抽取信息（招标文件获取时间）","reference":{"location":"第X章 招标文件获取时间 第X页"},"section":"招标文件获取时间"},{"ai_result":"模型抽取信息（投标文件截止时间）","reference":{"location":"第X章 投标文件截止时间 第X页"},"section":"投标文件截止时间"},{"ai_result":"模型抽取信息（相关行业）","reference":{"location":"第X章 相关行业 第X页"},"section":"相关行业"},{"ai_result":"模型抽取信息（安全）","reference":{"location":"第X章 安全 第X页"},"section":"安全"},{"ai_result":"模型抽取信息（人员数量要求）","reference":{"location":"第X章 人员数量要求 第X页"},"section":"人员数量要求"}]}'
```

```http
POST /{bizId}/censor/key HTTP/1.1
Content-Type: application/json
Accept: application/json
Host: example.com
Content-Length: 2340

{"tender_summary":[{"ai_result":"模型抽取信息（项目名称）","reference":{"location":"第X章 项目名称 第X页"},"section":"项目名称"},{"ai_result":"模型抽取信息（项目业主）","reference":{"location":"第X章 项目业主 第X页"},"section":"项目业主"},{"ai_result":"模型抽取信息（项目概况）","reference":{"location":"第X章 项目概况 第X页"},"section":"项目概况"},{"ai_result":"模型抽取信息（建设地点）","reference":{"location":"第X章 建设地点 第X页"},"section":"建设地点"},{"ai_result":"模型抽取信息（计划工期）","reference":{"location":"第X章 计划工期 第X页"},"section":"计划工期"},{"ai_result":"模型抽取信息（质量标准）","reference":{"location":"第X章 质量标准 第X页"},"section":"质量标准"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（投标文件递交）","reference":{"location":"第X章 投标文件递交 第X页"},"section":"投标文件递交"},{"ai_result":"模型抽取信息（招标范围）","reference":{"location":"第X章 招标范围 第X页"},"section":"招标范围"},{"ai_result":"模型抽取信息（资质要求）","reference":{"location":"第X章 资质要求 第X页"},"section":"资质要求"},{"ai_result":"模型抽取信息（业绩要求）","reference":{"location":"第X章 业绩要求 第X页"},"section":"业绩要求"},{"ai_result":"模型抽取信息（人员、财务与信誉要求）","reference":{"location":"第X章 人员、财务与信誉要求 第X页"},"section":"人员、财务与信誉要求"},{"ai_result":"模型抽取信息（其他要求）","reference":{"location":"第X章 其他要求 第X页"},"section":"其他要求"},{"ai_result":"模型抽取信息（踏勘现场）","reference":{"location":"第X章 踏勘现场 第X页"},"section":"踏勘现场"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（摘要内容-评标办法）","reference":{"location":"第X章 摘要内容-评标办法 第X页"},"section":"摘要内容-评标办法"},{"ai_result":"模型抽取信息（审查内容-评标办法）","reference":{"location":"第X章 审查内容-评标办法 第X页"},"section":"审查内容-评标办法"},{"ai_result":"模型抽取信息（罚则）","reference":{"location":"第X章 罚则 第X页"},"section":"罚则"},{"ai_result":"模型抽取信息（标段名称）","reference":{"location":"第X章 标段名称 第X页"},"section":"标段名称"},{"ai_result":"模型抽取信息（招标编号）","reference":{"location":"第X章 招标编号 第X页"},"section":"招标编号"},{"ai_result":"模型抽取信息（项目编号）","reference":{"location":"第X章 项目编号 第X页"},"section":"项目编号"},{"ai_result":"模型抽取信息（招标文件获取时间）","reference":{"location":"第X章 招标文件获取时间 第X页"},"section":"招标文件获取时间"},{"ai_result":"模型抽取信息（投标文件截止时间）","reference":{"location":"第X章 投标文件截止时间 第X页"},"section":"投标文件截止时间"},{"ai_result":"模型抽取信息（相关行业）","reference":{"location":"第X章 相关行业 第X页"},"section":"相关行业"},{"ai_result":"模型抽取信息（安全）","reference":{"location":"第X章 安全 第X页"},"section":"安全"},{"ai_result":"模型抽取信息（人员数量要求）","reference":{"location":"第X章 人员数量要求 第X页"},"section":"人员数量要求"}]}
```

`POST /{bizId}/censor/key`

> Body parameter

```json
{
  "tender_summary": [
    {
      "ai_result": "模型抽取信息（项目名称）",
      "reference": {
        "location": "第X章 项目名称 第X页"
      },
      "section": "项目名称"
    },
    {
      "ai_result": "模型抽取信息（项目业主）",
      "reference": {
        "location": "第X章 项目业主 第X页"
      },
      "section": "项目业主"
    },
    {
      "ai_result": "模型抽取信息（项目概况）",
      "reference": {
        "location": "第X章 项目概况 第X页"
      },
      "section": "项目概况"
    },
    {
      "ai_result": "模型抽取信息（建设地点）",
      "reference": {
        "location": "第X章 建设地点 第X页"
      },
      "section": "建设地点"
    },
    {
      "ai_result": "模型抽取信息（计划工期）",
      "reference": {
        "location": "第X章 计划工期 第X页"
      },
      "section": "计划工期"
    },
    {
      "ai_result": "模型抽取信息（质量标准）",
      "reference": {
        "location": "第X章 质量标准 第X页"
      },
      "section": "质量标准"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（投标文件递交）",
      "reference": {
        "location": "第X章 投标文件递交 第X页"
      },
      "section": "投标文件递交"
    },
    {
      "ai_result": "模型抽取信息（招标范围）",
      "reference": {
        "location": "第X章 招标范围 第X页"
      },
      "section": "招标范围"
    },
    {
      "ai_result": "模型抽取信息（资质要求）",
      "reference": {
        "location": "第X章 资质要求 第X页"
      },
      "section": "资质要求"
    },
    {
      "ai_result": "模型抽取信息（业绩要求）",
      "reference": {
        "location": "第X章 业绩要求 第X页"
      },
      "section": "业绩要求"
    },
    {
      "ai_result": "模型抽取信息（人员、财务与信誉要求）",
      "reference": {
        "location": "第X章 人员、财务与信誉要求 第X页"
      },
      "section": "人员、财务与信誉要求"
    },
    {
      "ai_result": "模型抽取信息（其他要求）",
      "reference": {
        "location": "第X章 其他要求 第X页"
      },
      "section": "其他要求"
    },
    {
      "ai_result": "模型抽取信息（踏勘现场）",
      "reference": {
        "location": "第X章 踏勘现场 第X页"
      },
      "section": "踏勘现场"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（摘要内容-评标办法）",
      "reference": {
        "location": "第X章 摘要内容-评标办法 第X页"
      },
      "section": "摘要内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（审查内容-评标办法）",
      "reference": {
        "location": "第X章 审查内容-评标办法 第X页"
      },
      "section": "审查内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（罚则）",
      "reference": {
        "location": "第X章 罚则 第X页"
      },
      "section": "罚则"
    },
    {
      "ai_result": "模型抽取信息（标段名称）",
      "reference": {
        "location": "第X章 标段名称 第X页"
      },
      "section": "标段名称"
    },
    {
      "ai_result": "模型抽取信息（招标编号）",
      "reference": {
        "location": "第X章 招标编号 第X页"
      },
      "section": "招标编号"
    },
    {
      "ai_result": "模型抽取信息（项目编号）",
      "reference": {
        "location": "第X章 项目编号 第X页"
      },
      "section": "项目编号"
    },
    {
      "ai_result": "模型抽取信息（招标文件获取时间）",
      "reference": {
        "location": "第X章 招标文件获取时间 第X页"
      },
      "section": "招标文件获取时间"
    },
    {
      "ai_result": "模型抽取信息（投标文件截止时间）",
      "reference": {
        "location": "第X章 投标文件截止时间 第X页"
      },
      "section": "投标文件截止时间"
    },
    {
      "ai_result": "模型抽取信息（相关行业）",
      "reference": {
        "location": "第X章 相关行业 第X页"
      },
      "section": "相关行业"
    },
    {
      "ai_result": "模型抽取信息（安全）",
      "reference": {
        "location": "第X章 安全 第X页"
      },
      "section": "安全"
    },
    {
      "ai_result": "模型抽取信息（人员数量要求）",
      "reference": {
        "location": "第X章 人员数量要求 第X页"
      },
      "section": "人员数量要求"
    }
  ]
}
```

<h3 id="投标文件审查-关键信息审查-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|bizId|path|string|true|业务ID|
|body|body|[BidKeyReviewBody](#schemabidkeyreviewbody)|true|none|
|» tender_summary|body|[[SummaryEntry](#schemasummaryentry)]|true|投标文件摘要信息|
|»» SummaryEntry|body|[SummaryEntry](#schemasummaryentry)|false|none|
|»»» section|body|string|true|对应抽取点|
|»»» ai_result|body|string|true|模型输出内容|
|»»» reference|body|[Reference](#schemareference)|true|关联内容|
|»»»» location|body|string|true|对应页码|

> Example responses

> 200 Response

```json
{
  "bizId": "bizId",
  "status": "success",
  "key_censor_fileid": "key_censor_fileid",
  "results": [
    {
      "ai_result": "模型分析信息（项目名称一致性）",
      "bid_reference": {
        "location": "投标文件第X章 项目名称一致性 第X页"
      },
      "conclusion": "符合",
      "section": "项目名称一致性",
      "tender_reference": {
        "location": "招标文件第X章 项目名称一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目名称符合性）",
      "bid_reference": {
        "location": "投标文件第X章 项目名称符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目名称符合性",
      "tender_reference": {
        "location": "招标文件第X章 项目名称符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目业主一致性）",
      "bid_reference": {
        "location": "投标文件第X章 项目业主一致性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目业主一致性",
      "tender_reference": {
        "location": "招标文件第X章 项目业主一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目业主符合性）",
      "bid_reference": {
        "location": "投标文件第X章 项目业主符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目业主符合性",
      "tender_reference": {
        "location": "招标文件第X章 项目业主符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（标段名称一致性）",
      "bid_reference": {
        "location": "投标文件第X章 标段名称一致性 第X页"
      },
      "conclusion": "符合",
      "section": "标段名称一致性",
      "tender_reference": {
        "location": "招标文件第X章 标段名称一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（标段名称符合性）",
      "bid_reference": {
        "location": "投标文件第X章 标段名称符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "标段名称符合性",
      "tender_reference": {
        "location": "招标文件第X章 标段名称符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目编号一致性）",
      "bid_reference": {
        "location": "投标文件第X章 项目编号一致性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目编号一致性",
      "tender_reference": {
        "location": "招标文件第X章 项目编号一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目编号符合性）",
      "bid_reference": {
        "location": "投标文件第X章 项目编号符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目编号符合性",
      "tender_reference": {
        "location": "招标文件第X章 项目编号符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（招标编号一致性）",
      "bid_reference": {
        "location": "投标文件第X章 招标编号一致性 第X页"
      },
      "conclusion": "不符合",
      "section": "招标编号一致性",
      "tender_reference": {
        "location": "招标文件第X章 招标编号一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（招标编号符合性）",
      "bid_reference": {
        "location": "投标文件第X章 招标编号符合性 第X页"
      },
      "conclusion": "符合",
      "section": "招标编号符合性",
      "tender_reference": {
        "location": "招标文件第X章 招标编号符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（工期一致性）",
      "bid_reference": {
        "location": "投标文件第X章 工期一致性 第X页"
      },
      "conclusion": "符合",
      "section": "工期一致性",
      "tender_reference": {
        "location": "招标文件第X章 工期一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（工期符合性）",
      "bid_reference": {
        "location": "投标文件第X章 工期符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "工期符合性",
      "tender_reference": {
        "location": "招标文件第X章 工期符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（质量）",
      "bid_reference": {
        "location": "投标文件第X章 质量 第X页"
      },
      "conclusion": "符合",
      "section": "质量",
      "tender_reference": {
        "location": "招标文件第X章 质量 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（安全）",
      "bid_reference": {
        "location": "投标文件第X章 安全 第X页"
      },
      "conclusion": "不符合",
      "section": "安全",
      "tender_reference": {
        "location": "招标文件第X章 安全 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（落款日期一致性）",
      "bid_reference": {
        "location": "投标文件第X章 落款日期一致性 第X页"
      },
      "conclusion": "符合",
      "section": "落款日期一致性",
      "tender_reference": {
        "location": "招标文件第X章 落款日期一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（落款日期符合性）",
      "bid_reference": {
        "location": "投标文件第X章 落款日期符合性 第X页"
      },
      "conclusion": "符合",
      "section": "落款日期符合性",
      "tender_reference": {
        "location": "招标文件第X章 落款日期符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（不相关地点）",
      "bid_reference": {
        "location": "投标文件第X章 不相关地点 第X页"
      },
      "conclusion": "符合",
      "section": "不相关地点",
      "tender_reference": {
        "location": "招标文件第X章 不相关地点 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（不相关行业）",
      "bid_reference": {
        "location": "投标文件第X章 不相关行业 第X页"
      },
      "conclusion": "不符合",
      "section": "不相关行业",
      "tender_reference": {
        "location": "招标文件第X章 不相关行业 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（报价唯一）",
      "bid_reference": {
        "location": "投标文件第X章 报价唯一 第X页"
      },
      "conclusion": "符合",
      "section": "报价唯一",
      "tender_reference": {
        "location": "招标文件第X章 报价唯一 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（人员要求）",
      "bid_reference": {
        "location": "投标文件第X章 人员要求 第X页"
      },
      "conclusion": "符合",
      "section": "人员要求",
      "tender_reference": {
        "location": "招标文件第X章 人员要求 第X页"
      }
    }
  ]
}
```

<h3 id="投标文件审查-关键信息审查-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[BidKeyReviewResponse](#schemabidkeyreviewresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

## 投标文件审查-符合招标文件要求审查

<a id="opIdreview_requirement_in_tender_doc__bizId__censor_requirement_post"></a>

> Code samples

```shell
curl --request POST \
  --url https://example.com/{bizId}/censor/requirement \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{"tender_summary":[{"ai_result":"模型抽取信息（项目名称）","reference":{"location":"第X章 项目名称 第X页"},"section":"项目名称"},{"ai_result":"模型抽取信息（项目业主）","reference":{"location":"第X章 项目业主 第X页"},"section":"项目业主"},{"ai_result":"模型抽取信息（项目概况）","reference":{"location":"第X章 项目概况 第X页"},"section":"项目概况"},{"ai_result":"模型抽取信息（建设地点）","reference":{"location":"第X章 建设地点 第X页"},"section":"建设地点"},{"ai_result":"模型抽取信息（计划工期）","reference":{"location":"第X章 计划工期 第X页"},"section":"计划工期"},{"ai_result":"模型抽取信息（质量标准）","reference":{"location":"第X章 质量标准 第X页"},"section":"质量标准"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（投标文件递交）","reference":{"location":"第X章 投标文件递交 第X页"},"section":"投标文件递交"},{"ai_result":"模型抽取信息（招标范围）","reference":{"location":"第X章 招标范围 第X页"},"section":"招标范围"},{"ai_result":"模型抽取信息（资质要求）","reference":{"location":"第X章 资质要求 第X页"},"section":"资质要求"},{"ai_result":"模型抽取信息（业绩要求）","reference":{"location":"第X章 业绩要求 第X页"},"section":"业绩要求"},{"ai_result":"模型抽取信息（人员、财务与信誉要求）","reference":{"location":"第X章 人员、财务与信誉要求 第X页"},"section":"人员、财务与信誉要求"},{"ai_result":"模型抽取信息（其他要求）","reference":{"location":"第X章 其他要求 第X页"},"section":"其他要求"},{"ai_result":"模型抽取信息（踏勘现场）","reference":{"location":"第X章 踏勘现场 第X页"},"section":"踏勘现场"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（摘要内容-评标办法）","reference":{"location":"第X章 摘要内容-评标办法 第X页"},"section":"摘要内容-评标办法"},{"ai_result":"模型抽取信息（审查内容-评标办法）","reference":{"location":"第X章 审查内容-评标办法 第X页"},"section":"审查内容-评标办法"},{"ai_result":"模型抽取信息（罚则）","reference":{"location":"第X章 罚则 第X页"},"section":"罚则"},{"ai_result":"模型抽取信息（标段名称）","reference":{"location":"第X章 标段名称 第X页"},"section":"标段名称"},{"ai_result":"模型抽取信息（招标编号）","reference":{"location":"第X章 招标编号 第X页"},"section":"招标编号"},{"ai_result":"模型抽取信息（项目编号）","reference":{"location":"第X章 项目编号 第X页"},"section":"项目编号"},{"ai_result":"模型抽取信息（招标文件获取时间）","reference":{"location":"第X章 招标文件获取时间 第X页"},"section":"招标文件获取时间"},{"ai_result":"模型抽取信息（投标文件截止时间）","reference":{"location":"第X章 投标文件截止时间 第X页"},"section":"投标文件截止时间"},{"ai_result":"模型抽取信息（相关行业）","reference":{"location":"第X章 相关行业 第X页"},"section":"相关行业"},{"ai_result":"模型抽取信息（安全）","reference":{"location":"第X章 安全 第X页"},"section":"安全"},{"ai_result":"模型抽取信息（人员数量要求）","reference":{"location":"第X章 人员数量要求 第X页"},"section":"人员数量要求"}]}'
```

```http
POST /{bizId}/censor/requirement HTTP/1.1
Content-Type: application/json
Accept: application/json
Host: example.com
Content-Length: 2340

{"tender_summary":[{"ai_result":"模型抽取信息（项目名称）","reference":{"location":"第X章 项目名称 第X页"},"section":"项目名称"},{"ai_result":"模型抽取信息（项目业主）","reference":{"location":"第X章 项目业主 第X页"},"section":"项目业主"},{"ai_result":"模型抽取信息（项目概况）","reference":{"location":"第X章 项目概况 第X页"},"section":"项目概况"},{"ai_result":"模型抽取信息（建设地点）","reference":{"location":"第X章 建设地点 第X页"},"section":"建设地点"},{"ai_result":"模型抽取信息（计划工期）","reference":{"location":"第X章 计划工期 第X页"},"section":"计划工期"},{"ai_result":"模型抽取信息（质量标准）","reference":{"location":"第X章 质量标准 第X页"},"section":"质量标准"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（投标文件递交）","reference":{"location":"第X章 投标文件递交 第X页"},"section":"投标文件递交"},{"ai_result":"模型抽取信息（招标范围）","reference":{"location":"第X章 招标范围 第X页"},"section":"招标范围"},{"ai_result":"模型抽取信息（资质要求）","reference":{"location":"第X章 资质要求 第X页"},"section":"资质要求"},{"ai_result":"模型抽取信息（业绩要求）","reference":{"location":"第X章 业绩要求 第X页"},"section":"业绩要求"},{"ai_result":"模型抽取信息（人员、财务与信誉要求）","reference":{"location":"第X章 人员、财务与信誉要求 第X页"},"section":"人员、财务与信誉要求"},{"ai_result":"模型抽取信息（其他要求）","reference":{"location":"第X章 其他要求 第X页"},"section":"其他要求"},{"ai_result":"模型抽取信息（踏勘现场）","reference":{"location":"第X章 踏勘现场 第X页"},"section":"踏勘现场"},{"ai_result":"模型抽取信息（最高投标限价）","reference":{"location":"第X章 最高投标限价 第X页"},"section":"最高投标限价"},{"ai_result":"模型抽取信息（摘要内容-评标办法）","reference":{"location":"第X章 摘要内容-评标办法 第X页"},"section":"摘要内容-评标办法"},{"ai_result":"模型抽取信息（审查内容-评标办法）","reference":{"location":"第X章 审查内容-评标办法 第X页"},"section":"审查内容-评标办法"},{"ai_result":"模型抽取信息（罚则）","reference":{"location":"第X章 罚则 第X页"},"section":"罚则"},{"ai_result":"模型抽取信息（标段名称）","reference":{"location":"第X章 标段名称 第X页"},"section":"标段名称"},{"ai_result":"模型抽取信息（招标编号）","reference":{"location":"第X章 招标编号 第X页"},"section":"招标编号"},{"ai_result":"模型抽取信息（项目编号）","reference":{"location":"第X章 项目编号 第X页"},"section":"项目编号"},{"ai_result":"模型抽取信息（招标文件获取时间）","reference":{"location":"第X章 招标文件获取时间 第X页"},"section":"招标文件获取时间"},{"ai_result":"模型抽取信息（投标文件截止时间）","reference":{"location":"第X章 投标文件截止时间 第X页"},"section":"投标文件截止时间"},{"ai_result":"模型抽取信息（相关行业）","reference":{"location":"第X章 相关行业 第X页"},"section":"相关行业"},{"ai_result":"模型抽取信息（安全）","reference":{"location":"第X章 安全 第X页"},"section":"安全"},{"ai_result":"模型抽取信息（人员数量要求）","reference":{"location":"第X章 人员数量要求 第X页"},"section":"人员数量要求"}]}
```

`POST /{bizId}/censor/requirement`

> Body parameter

```json
{
  "tender_summary": [
    {
      "ai_result": "模型抽取信息（项目名称）",
      "reference": {
        "location": "第X章 项目名称 第X页"
      },
      "section": "项目名称"
    },
    {
      "ai_result": "模型抽取信息（项目业主）",
      "reference": {
        "location": "第X章 项目业主 第X页"
      },
      "section": "项目业主"
    },
    {
      "ai_result": "模型抽取信息（项目概况）",
      "reference": {
        "location": "第X章 项目概况 第X页"
      },
      "section": "项目概况"
    },
    {
      "ai_result": "模型抽取信息（建设地点）",
      "reference": {
        "location": "第X章 建设地点 第X页"
      },
      "section": "建设地点"
    },
    {
      "ai_result": "模型抽取信息（计划工期）",
      "reference": {
        "location": "第X章 计划工期 第X页"
      },
      "section": "计划工期"
    },
    {
      "ai_result": "模型抽取信息（质量标准）",
      "reference": {
        "location": "第X章 质量标准 第X页"
      },
      "section": "质量标准"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（投标文件递交）",
      "reference": {
        "location": "第X章 投标文件递交 第X页"
      },
      "section": "投标文件递交"
    },
    {
      "ai_result": "模型抽取信息（招标范围）",
      "reference": {
        "location": "第X章 招标范围 第X页"
      },
      "section": "招标范围"
    },
    {
      "ai_result": "模型抽取信息（资质要求）",
      "reference": {
        "location": "第X章 资质要求 第X页"
      },
      "section": "资质要求"
    },
    {
      "ai_result": "模型抽取信息（业绩要求）",
      "reference": {
        "location": "第X章 业绩要求 第X页"
      },
      "section": "业绩要求"
    },
    {
      "ai_result": "模型抽取信息（人员、财务与信誉要求）",
      "reference": {
        "location": "第X章 人员、财务与信誉要求 第X页"
      },
      "section": "人员、财务与信誉要求"
    },
    {
      "ai_result": "模型抽取信息（其他要求）",
      "reference": {
        "location": "第X章 其他要求 第X页"
      },
      "section": "其他要求"
    },
    {
      "ai_result": "模型抽取信息（踏勘现场）",
      "reference": {
        "location": "第X章 踏勘现场 第X页"
      },
      "section": "踏勘现场"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（摘要内容-评标办法）",
      "reference": {
        "location": "第X章 摘要内容-评标办法 第X页"
      },
      "section": "摘要内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（审查内容-评标办法）",
      "reference": {
        "location": "第X章 审查内容-评标办法 第X页"
      },
      "section": "审查内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（罚则）",
      "reference": {
        "location": "第X章 罚则 第X页"
      },
      "section": "罚则"
    },
    {
      "ai_result": "模型抽取信息（标段名称）",
      "reference": {
        "location": "第X章 标段名称 第X页"
      },
      "section": "标段名称"
    },
    {
      "ai_result": "模型抽取信息（招标编号）",
      "reference": {
        "location": "第X章 招标编号 第X页"
      },
      "section": "招标编号"
    },
    {
      "ai_result": "模型抽取信息（项目编号）",
      "reference": {
        "location": "第X章 项目编号 第X页"
      },
      "section": "项目编号"
    },
    {
      "ai_result": "模型抽取信息（招标文件获取时间）",
      "reference": {
        "location": "第X章 招标文件获取时间 第X页"
      },
      "section": "招标文件获取时间"
    },
    {
      "ai_result": "模型抽取信息（投标文件截止时间）",
      "reference": {
        "location": "第X章 投标文件截止时间 第X页"
      },
      "section": "投标文件截止时间"
    },
    {
      "ai_result": "模型抽取信息（相关行业）",
      "reference": {
        "location": "第X章 相关行业 第X页"
      },
      "section": "相关行业"
    },
    {
      "ai_result": "模型抽取信息（安全）",
      "reference": {
        "location": "第X章 安全 第X页"
      },
      "section": "安全"
    },
    {
      "ai_result": "模型抽取信息（人员数量要求）",
      "reference": {
        "location": "第X章 人员数量要求 第X页"
      },
      "section": "人员数量要求"
    }
  ]
}
```

<h3 id="投标文件审查-符合招标文件要求审查-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|bizId|path|string|true|业务ID|
|body|body|[BidReqReviewBody](#schemabidreqreviewbody)|true|none|
|» tender_summary|body|[[SummaryEntry](#schemasummaryentry)]|true|投标文件摘要信息|
|»» SummaryEntry|body|[SummaryEntry](#schemasummaryentry)|false|none|
|»»» section|body|string|true|对应抽取点|
|»»» ai_result|body|string|true|模型输出内容|
|»»» reference|body|[Reference](#schemareference)|true|关联内容|
|»»»» location|body|string|true|对应页码|

> Example responses

> 200 Response

```json
{
  "bizId": "bizId",
  "status": "success",
  "requirement_censor_fileid": "requirement_censor_fileid",
  "results": [
    {
      "section": "安全",
      "ai_result": "模型分析信息（安全）",
      "conclusion": "符合",
      "tender_reference": {
        "location": "招标文件第X章 安全 第X页"
      },
      "bid_reference": {
        "location": "投标文件第X章 安全 第X页"
      }
    }
  ]
}
```

<h3 id="投标文件审查-符合招标文件要求审查-responses">Responses</h3>

|Status|Meaning|Description|Schema|
|---|---|---|---|
|200|[OK](https://tools.ietf.org/html/rfc7231#section-6.3.1)|Successful Response|[BidReqReviewResponse](#schemabidreqreviewresponse)|
|422|[Unprocessable Entity](https://tools.ietf.org/html/rfc2518#section-10.3)|Validation Error|[HTTPValidationError](#schemahttpvalidationerror)|

<aside class="success">
This operation does not require authentication
</aside>

# Schemas

<h2 id="tocS_BidKeyReviewBody">BidKeyReviewBody</h2>
<!-- backwards compatibility -->
<a id="schemabidkeyreviewbody"></a>
<a id="schema_BidKeyReviewBody"></a>
<a id="tocSbidkeyreviewbody"></a>
<a id="tocsbidkeyreviewbody"></a>

```json
{
  "tender_summary": [
    {
      "ai_result": "模型抽取信息（项目名称）",
      "reference": {
        "location": "第X章 项目名称 第X页"
      },
      "section": "项目名称"
    },
    {
      "ai_result": "模型抽取信息（项目业主）",
      "reference": {
        "location": "第X章 项目业主 第X页"
      },
      "section": "项目业主"
    },
    {
      "ai_result": "模型抽取信息（项目概况）",
      "reference": {
        "location": "第X章 项目概况 第X页"
      },
      "section": "项目概况"
    },
    {
      "ai_result": "模型抽取信息（建设地点）",
      "reference": {
        "location": "第X章 建设地点 第X页"
      },
      "section": "建设地点"
    },
    {
      "ai_result": "模型抽取信息（计划工期）",
      "reference": {
        "location": "第X章 计划工期 第X页"
      },
      "section": "计划工期"
    },
    {
      "ai_result": "模型抽取信息（质量标准）",
      "reference": {
        "location": "第X章 质量标准 第X页"
      },
      "section": "质量标准"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（投标文件递交）",
      "reference": {
        "location": "第X章 投标文件递交 第X页"
      },
      "section": "投标文件递交"
    },
    {
      "ai_result": "模型抽取信息（招标范围）",
      "reference": {
        "location": "第X章 招标范围 第X页"
      },
      "section": "招标范围"
    },
    {
      "ai_result": "模型抽取信息（资质要求）",
      "reference": {
        "location": "第X章 资质要求 第X页"
      },
      "section": "资质要求"
    },
    {
      "ai_result": "模型抽取信息（业绩要求）",
      "reference": {
        "location": "第X章 业绩要求 第X页"
      },
      "section": "业绩要求"
    },
    {
      "ai_result": "模型抽取信息（人员、财务与信誉要求）",
      "reference": {
        "location": "第X章 人员、财务与信誉要求 第X页"
      },
      "section": "人员、财务与信誉要求"
    },
    {
      "ai_result": "模型抽取信息（其他要求）",
      "reference": {
        "location": "第X章 其他要求 第X页"
      },
      "section": "其他要求"
    },
    {
      "ai_result": "模型抽取信息（踏勘现场）",
      "reference": {
        "location": "第X章 踏勘现场 第X页"
      },
      "section": "踏勘现场"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（摘要内容-评标办法）",
      "reference": {
        "location": "第X章 摘要内容-评标办法 第X页"
      },
      "section": "摘要内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（审查内容-评标办法）",
      "reference": {
        "location": "第X章 审查内容-评标办法 第X页"
      },
      "section": "审查内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（罚则）",
      "reference": {
        "location": "第X章 罚则 第X页"
      },
      "section": "罚则"
    },
    {
      "ai_result": "模型抽取信息（标段名称）",
      "reference": {
        "location": "第X章 标段名称 第X页"
      },
      "section": "标段名称"
    },
    {
      "ai_result": "模型抽取信息（招标编号）",
      "reference": {
        "location": "第X章 招标编号 第X页"
      },
      "section": "招标编号"
    },
    {
      "ai_result": "模型抽取信息（项目编号）",
      "reference": {
        "location": "第X章 项目编号 第X页"
      },
      "section": "项目编号"
    },
    {
      "ai_result": "模型抽取信息（招标文件获取时间）",
      "reference": {
        "location": "第X章 招标文件获取时间 第X页"
      },
      "section": "招标文件获取时间"
    },
    {
      "ai_result": "模型抽取信息（投标文件截止时间）",
      "reference": {
        "location": "第X章 投标文件截止时间 第X页"
      },
      "section": "投标文件截止时间"
    },
    {
      "ai_result": "模型抽取信息（相关行业）",
      "reference": {
        "location": "第X章 相关行业 第X页"
      },
      "section": "相关行业"
    },
    {
      "ai_result": "模型抽取信息（安全）",
      "reference": {
        "location": "第X章 安全 第X页"
      },
      "section": "安全"
    },
    {
      "ai_result": "模型抽取信息（人员数量要求）",
      "reference": {
        "location": "第X章 人员数量要求 第X页"
      },
      "section": "人员数量要求"
    }
  ]
}

```

BidKeyReviewBody

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tender_summary|[[SummaryEntry](#schemasummaryentry)]|true|none|投标文件摘要信息|

<h2 id="tocS_BidKeyReviewResponse">BidKeyReviewResponse</h2>
<!-- backwards compatibility -->
<a id="schemabidkeyreviewresponse"></a>
<a id="schema_BidKeyReviewResponse"></a>
<a id="tocSbidkeyreviewresponse"></a>
<a id="tocsbidkeyreviewresponse"></a>

```json
{
  "bizId": "bizId",
  "status": "success",
  "key_censor_fileid": "key_censor_fileid",
  "results": [
    {
      "ai_result": "模型分析信息（项目名称一致性）",
      "bid_reference": {
        "location": "投标文件第X章 项目名称一致性 第X页"
      },
      "conclusion": "符合",
      "section": "项目名称一致性",
      "tender_reference": {
        "location": "招标文件第X章 项目名称一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目名称符合性）",
      "bid_reference": {
        "location": "投标文件第X章 项目名称符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目名称符合性",
      "tender_reference": {
        "location": "招标文件第X章 项目名称符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目业主一致性）",
      "bid_reference": {
        "location": "投标文件第X章 项目业主一致性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目业主一致性",
      "tender_reference": {
        "location": "招标文件第X章 项目业主一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目业主符合性）",
      "bid_reference": {
        "location": "投标文件第X章 项目业主符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目业主符合性",
      "tender_reference": {
        "location": "招标文件第X章 项目业主符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（标段名称一致性）",
      "bid_reference": {
        "location": "投标文件第X章 标段名称一致性 第X页"
      },
      "conclusion": "符合",
      "section": "标段名称一致性",
      "tender_reference": {
        "location": "招标文件第X章 标段名称一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（标段名称符合性）",
      "bid_reference": {
        "location": "投标文件第X章 标段名称符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "标段名称符合性",
      "tender_reference": {
        "location": "招标文件第X章 标段名称符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目编号一致性）",
      "bid_reference": {
        "location": "投标文件第X章 项目编号一致性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目编号一致性",
      "tender_reference": {
        "location": "招标文件第X章 项目编号一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（项目编号符合性）",
      "bid_reference": {
        "location": "投标文件第X章 项目编号符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "项目编号符合性",
      "tender_reference": {
        "location": "招标文件第X章 项目编号符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（招标编号一致性）",
      "bid_reference": {
        "location": "投标文件第X章 招标编号一致性 第X页"
      },
      "conclusion": "不符合",
      "section": "招标编号一致性",
      "tender_reference": {
        "location": "招标文件第X章 招标编号一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（招标编号符合性）",
      "bid_reference": {
        "location": "投标文件第X章 招标编号符合性 第X页"
      },
      "conclusion": "符合",
      "section": "招标编号符合性",
      "tender_reference": {
        "location": "招标文件第X章 招标编号符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（工期一致性）",
      "bid_reference": {
        "location": "投标文件第X章 工期一致性 第X页"
      },
      "conclusion": "符合",
      "section": "工期一致性",
      "tender_reference": {
        "location": "招标文件第X章 工期一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（工期符合性）",
      "bid_reference": {
        "location": "投标文件第X章 工期符合性 第X页"
      },
      "conclusion": "不符合",
      "section": "工期符合性",
      "tender_reference": {
        "location": "招标文件第X章 工期符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（质量）",
      "bid_reference": {
        "location": "投标文件第X章 质量 第X页"
      },
      "conclusion": "符合",
      "section": "质量",
      "tender_reference": {
        "location": "招标文件第X章 质量 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（安全）",
      "bid_reference": {
        "location": "投标文件第X章 安全 第X页"
      },
      "conclusion": "不符合",
      "section": "安全",
      "tender_reference": {
        "location": "招标文件第X章 安全 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（落款日期一致性）",
      "bid_reference": {
        "location": "投标文件第X章 落款日期一致性 第X页"
      },
      "conclusion": "符合",
      "section": "落款日期一致性",
      "tender_reference": {
        "location": "招标文件第X章 落款日期一致性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（落款日期符合性）",
      "bid_reference": {
        "location": "投标文件第X章 落款日期符合性 第X页"
      },
      "conclusion": "符合",
      "section": "落款日期符合性",
      "tender_reference": {
        "location": "招标文件第X章 落款日期符合性 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（不相关地点）",
      "bid_reference": {
        "location": "投标文件第X章 不相关地点 第X页"
      },
      "conclusion": "符合",
      "section": "不相关地点",
      "tender_reference": {
        "location": "招标文件第X章 不相关地点 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（不相关行业）",
      "bid_reference": {
        "location": "投标文件第X章 不相关行业 第X页"
      },
      "conclusion": "不符合",
      "section": "不相关行业",
      "tender_reference": {
        "location": "招标文件第X章 不相关行业 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（报价唯一）",
      "bid_reference": {
        "location": "投标文件第X章 报价唯一 第X页"
      },
      "conclusion": "符合",
      "section": "报价唯一",
      "tender_reference": {
        "location": "招标文件第X章 报价唯一 第X页"
      }
    },
    {
      "ai_result": "模型分析信息（人员要求）",
      "bid_reference": {
        "location": "投标文件第X章 人员要求 第X页"
      },
      "conclusion": "符合",
      "section": "人员要求",
      "tender_reference": {
        "location": "招标文件第X章 人员要求 第X页"
      }
    }
  ]
}

```

BidKeyReviewResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|bizId|string|true|none|业务ID|
|status|string|false|none|请求处理状态|
|key_censor_fileid|string|true|none|关键审查docx文件ID|
|results|[[ReviewEntry](#schemareviewentry)]|true|none|关键信息审查结论|

#### Enumerated Values

|Property|Value|
|---|---|
|status|success|
|status|error|

<h2 id="tocS_BidOutlineResponse">BidOutlineResponse</h2>
<!-- backwards compatibility -->
<a id="schemabidoutlineresponse"></a>
<a id="schema_BidOutlineResponse"></a>
<a id="tocSbidoutlineresponse"></a>
<a id="tocsbidoutlineresponse"></a>

```json
{
  "bizId": "bizId",
  "status": "success",
  "outline_fileid": "outline_fileid"
}

```

BidOutlineResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|bizId|string|true|none|业务ID|
|status|string|false|none|请求处理状态|
|outline_fileid|string|true|none|投标文件大纲ID|

#### Enumerated Values

|Property|Value|
|---|---|
|status|success|
|status|error|

<h2 id="tocS_BidReqReviewBody">BidReqReviewBody</h2>
<!-- backwards compatibility -->
<a id="schemabidreqreviewbody"></a>
<a id="schema_BidReqReviewBody"></a>
<a id="tocSbidreqreviewbody"></a>
<a id="tocsbidreqreviewbody"></a>

```json
{
  "tender_summary": [
    {
      "ai_result": "模型抽取信息（项目名称）",
      "reference": {
        "location": "第X章 项目名称 第X页"
      },
      "section": "项目名称"
    },
    {
      "ai_result": "模型抽取信息（项目业主）",
      "reference": {
        "location": "第X章 项目业主 第X页"
      },
      "section": "项目业主"
    },
    {
      "ai_result": "模型抽取信息（项目概况）",
      "reference": {
        "location": "第X章 项目概况 第X页"
      },
      "section": "项目概况"
    },
    {
      "ai_result": "模型抽取信息（建设地点）",
      "reference": {
        "location": "第X章 建设地点 第X页"
      },
      "section": "建设地点"
    },
    {
      "ai_result": "模型抽取信息（计划工期）",
      "reference": {
        "location": "第X章 计划工期 第X页"
      },
      "section": "计划工期"
    },
    {
      "ai_result": "模型抽取信息（质量标准）",
      "reference": {
        "location": "第X章 质量标准 第X页"
      },
      "section": "质量标准"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（投标文件递交）",
      "reference": {
        "location": "第X章 投标文件递交 第X页"
      },
      "section": "投标文件递交"
    },
    {
      "ai_result": "模型抽取信息（招标范围）",
      "reference": {
        "location": "第X章 招标范围 第X页"
      },
      "section": "招标范围"
    },
    {
      "ai_result": "模型抽取信息（资质要求）",
      "reference": {
        "location": "第X章 资质要求 第X页"
      },
      "section": "资质要求"
    },
    {
      "ai_result": "模型抽取信息（业绩要求）",
      "reference": {
        "location": "第X章 业绩要求 第X页"
      },
      "section": "业绩要求"
    },
    {
      "ai_result": "模型抽取信息（人员、财务与信誉要求）",
      "reference": {
        "location": "第X章 人员、财务与信誉要求 第X页"
      },
      "section": "人员、财务与信誉要求"
    },
    {
      "ai_result": "模型抽取信息（其他要求）",
      "reference": {
        "location": "第X章 其他要求 第X页"
      },
      "section": "其他要求"
    },
    {
      "ai_result": "模型抽取信息（踏勘现场）",
      "reference": {
        "location": "第X章 踏勘现场 第X页"
      },
      "section": "踏勘现场"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（摘要内容-评标办法）",
      "reference": {
        "location": "第X章 摘要内容-评标办法 第X页"
      },
      "section": "摘要内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（审查内容-评标办法）",
      "reference": {
        "location": "第X章 审查内容-评标办法 第X页"
      },
      "section": "审查内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（罚则）",
      "reference": {
        "location": "第X章 罚则 第X页"
      },
      "section": "罚则"
    },
    {
      "ai_result": "模型抽取信息（标段名称）",
      "reference": {
        "location": "第X章 标段名称 第X页"
      },
      "section": "标段名称"
    },
    {
      "ai_result": "模型抽取信息（招标编号）",
      "reference": {
        "location": "第X章 招标编号 第X页"
      },
      "section": "招标编号"
    },
    {
      "ai_result": "模型抽取信息（项目编号）",
      "reference": {
        "location": "第X章 项目编号 第X页"
      },
      "section": "项目编号"
    },
    {
      "ai_result": "模型抽取信息（招标文件获取时间）",
      "reference": {
        "location": "第X章 招标文件获取时间 第X页"
      },
      "section": "招标文件获取时间"
    },
    {
      "ai_result": "模型抽取信息（投标文件截止时间）",
      "reference": {
        "location": "第X章 投标文件截止时间 第X页"
      },
      "section": "投标文件截止时间"
    },
    {
      "ai_result": "模型抽取信息（相关行业）",
      "reference": {
        "location": "第X章 相关行业 第X页"
      },
      "section": "相关行业"
    },
    {
      "ai_result": "模型抽取信息（安全）",
      "reference": {
        "location": "第X章 安全 第X页"
      },
      "section": "安全"
    },
    {
      "ai_result": "模型抽取信息（人员数量要求）",
      "reference": {
        "location": "第X章 人员数量要求 第X页"
      },
      "section": "人员数量要求"
    }
  ]
}

```

BidReqReviewBody

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tender_summary|[[SummaryEntry](#schemasummaryentry)]|true|none|投标文件摘要信息|

<h2 id="tocS_BidReqReviewResponse">BidReqReviewResponse</h2>
<!-- backwards compatibility -->
<a id="schemabidreqreviewresponse"></a>
<a id="schema_BidReqReviewResponse"></a>
<a id="tocSbidreqreviewresponse"></a>
<a id="tocsbidreqreviewresponse"></a>

```json
{
  "bizId": "bizId",
  "status": "success",
  "requirement_censor_fileid": "requirement_censor_fileid",
  "results": [
    {
      "section": "安全",
      "ai_result": "模型分析信息（安全）",
      "conclusion": "符合",
      "tender_reference": {
        "location": "招标文件第X章 安全 第X页"
      },
      "bid_reference": {
        "location": "投标文件第X章 安全 第X页"
      }
    }
  ]
}

```

BidReqReviewResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|bizId|string|true|none|业务ID|
|status|string|false|none|请求处理状态|
|requirement_censor_fileid|string|true|none|要求审查docx文件ID|
|results|[[ReviewEntry](#schemareviewentry)]|true|none|要求审查结果（审查点根据招标文件确定）|

#### Enumerated Values

|Property|Value|
|---|---|
|status|success|
|status|error|

<h2 id="tocS_HTTPValidationError">HTTPValidationError</h2>
<!-- backwards compatibility -->
<a id="schemahttpvalidationerror"></a>
<a id="schema_HTTPValidationError"></a>
<a id="tocShttpvalidationerror"></a>
<a id="tocshttpvalidationerror"></a>

```json
{
  "detail": [
    {
      "loc": [
        "string"
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}

```

HTTPValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|detail|[[ValidationError](#schemavalidationerror)]|false|none|none|

<h2 id="tocS_Reference">Reference</h2>
<!-- backwards compatibility -->
<a id="schemareference"></a>
<a id="schema_Reference"></a>
<a id="tocSreference"></a>
<a id="tocsreference"></a>

```json
{
  "location": "string"
}

```

Reference

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|location|string|true|none|对应页码|

<h2 id="tocS_ReviewEntry">ReviewEntry</h2>
<!-- backwards compatibility -->
<a id="schemareviewentry"></a>
<a id="schema_ReviewEntry"></a>
<a id="tocSreviewentry"></a>
<a id="tocsreviewentry"></a>

```json
{
  "section": "安全",
  "ai_result": "模型分析信息（安全）",
  "conclusion": "符合",
  "tender_reference": {
    "location": "招标文件第X章 安全 第X页"
  },
  "bid_reference": {
    "location": "投标文件第X章 安全 第X页"
  }
}

```

ReviewEntry

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|section|string|true|none|对应抽取点|
|ai_result|string|true|none|模型的结论分析|
|conclusion|string|false|none|内容是否一致的结论|
|tender_reference|[Reference](#schemareference)|true|none|招标文件关联内容|
|bid_reference|[Reference](#schemareference)|true|none|投标文件关联内容|

#### Enumerated Values

|Property|Value|
|---|---|
|conclusion|符合|
|conclusion|不符合|

<h2 id="tocS_SummaryEntry">SummaryEntry</h2>
<!-- backwards compatibility -->
<a id="schemasummaryentry"></a>
<a id="schema_SummaryEntry"></a>
<a id="tocSsummaryentry"></a>
<a id="tocssummaryentry"></a>

```json
{
  "section": "string",
  "ai_result": "string",
  "reference": {
    "location": "string"
  }
}

```

SummaryEntry

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|section|string|true|none|对应抽取点|
|ai_result|string|true|none|模型输出内容|
|reference|[Reference](#schemareference)|true|none|关联内容|

<h2 id="tocS_TenderSummaryResponse">TenderSummaryResponse</h2>
<!-- backwards compatibility -->
<a id="schematendersummaryresponse"></a>
<a id="schema_TenderSummaryResponse"></a>
<a id="tocStendersummaryresponse"></a>
<a id="tocstendersummaryresponse"></a>

```json
{
  "bizId": "bizId",
  "status": "success",
  "summary_fileid": "summary_file_id",
  "summary": [
    {
      "ai_result": "模型抽取信息（项目名称）",
      "reference": {
        "location": "第X章 项目名称 第X页"
      },
      "section": "项目名称"
    },
    {
      "ai_result": "模型抽取信息（项目业主）",
      "reference": {
        "location": "第X章 项目业主 第X页"
      },
      "section": "项目业主"
    },
    {
      "ai_result": "模型抽取信息（项目概况）",
      "reference": {
        "location": "第X章 项目概况 第X页"
      },
      "section": "项目概况"
    },
    {
      "ai_result": "模型抽取信息（建设地点）",
      "reference": {
        "location": "第X章 建设地点 第X页"
      },
      "section": "建设地点"
    },
    {
      "ai_result": "模型抽取信息（计划工期）",
      "reference": {
        "location": "第X章 计划工期 第X页"
      },
      "section": "计划工期"
    },
    {
      "ai_result": "模型抽取信息（质量标准）",
      "reference": {
        "location": "第X章 质量标准 第X页"
      },
      "section": "质量标准"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（投标文件递交）",
      "reference": {
        "location": "第X章 投标文件递交 第X页"
      },
      "section": "投标文件递交"
    },
    {
      "ai_result": "模型抽取信息（招标范围）",
      "reference": {
        "location": "第X章 招标范围 第X页"
      },
      "section": "招标范围"
    },
    {
      "ai_result": "模型抽取信息（资质要求）",
      "reference": {
        "location": "第X章 资质要求 第X页"
      },
      "section": "资质要求"
    },
    {
      "ai_result": "模型抽取信息（业绩要求）",
      "reference": {
        "location": "第X章 业绩要求 第X页"
      },
      "section": "业绩要求"
    },
    {
      "ai_result": "模型抽取信息（人员、财务与信誉要求）",
      "reference": {
        "location": "第X章 人员、财务与信誉要求 第X页"
      },
      "section": "人员、财务与信誉要求"
    },
    {
      "ai_result": "模型抽取信息（其他要求）",
      "reference": {
        "location": "第X章 其他要求 第X页"
      },
      "section": "其他要求"
    },
    {
      "ai_result": "模型抽取信息（踏勘现场）",
      "reference": {
        "location": "第X章 踏勘现场 第X页"
      },
      "section": "踏勘现场"
    },
    {
      "ai_result": "模型抽取信息（最高投标限价）",
      "reference": {
        "location": "第X章 最高投标限价 第X页"
      },
      "section": "最高投标限价"
    },
    {
      "ai_result": "模型抽取信息（摘要内容-评标办法）",
      "reference": {
        "location": "第X章 摘要内容-评标办法 第X页"
      },
      "section": "摘要内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（审查内容-评标办法）",
      "reference": {
        "location": "第X章 审查内容-评标办法 第X页"
      },
      "section": "审查内容-评标办法"
    },
    {
      "ai_result": "模型抽取信息（罚则）",
      "reference": {
        "location": "第X章 罚则 第X页"
      },
      "section": "罚则"
    },
    {
      "ai_result": "模型抽取信息（标段名称）",
      "reference": {
        "location": "第X章 标段名称 第X页"
      },
      "section": "标段名称"
    },
    {
      "ai_result": "模型抽取信息（招标编号）",
      "reference": {
        "location": "第X章 招标编号 第X页"
      },
      "section": "招标编号"
    },
    {
      "ai_result": "模型抽取信息（项目编号）",
      "reference": {
        "location": "第X章 项目编号 第X页"
      },
      "section": "项目编号"
    },
    {
      "ai_result": "模型抽取信息（招标文件获取时间）",
      "reference": {
        "location": "第X章 招标文件获取时间 第X页"
      },
      "section": "招标文件获取时间"
    },
    {
      "ai_result": "模型抽取信息（投标文件截止时间）",
      "reference": {
        "location": "第X章 投标文件截止时间 第X页"
      },
      "section": "投标文件截止时间"
    },
    {
      "ai_result": "模型抽取信息（相关行业）",
      "reference": {
        "location": "第X章 相关行业 第X页"
      },
      "section": "相关行业"
    },
    {
      "ai_result": "模型抽取信息（安全）",
      "reference": {
        "location": "第X章 安全 第X页"
      },
      "section": "安全"
    },
    {
      "ai_result": "模型抽取信息（人员数量要求）",
      "reference": {
        "location": "第X章 人员数量要求 第X页"
      },
      "section": "人员数量要求"
    }
  ]
}

```

TenderSummaryResponse

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|bizId|string|true|none|业务ID|
|status|string|false|none|请求处理状态|
|summary_fileid|string|true|none|摘要docx文件ID|
|summary|[[SummaryEntry](#schemasummaryentry)]|true|none|摘要信息|

#### Enumerated Values

|Property|Value|
|---|---|
|status|success|
|status|error|

<h2 id="tocS_ValidationError">ValidationError</h2>
<!-- backwards compatibility -->
<a id="schemavalidationerror"></a>
<a id="schema_ValidationError"></a>
<a id="tocSvalidationerror"></a>
<a id="tocsvalidationerror"></a>

```json
{
  "loc": [
    "string"
  ],
  "msg": "string",
  "type": "string"
}

```

ValidationError

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|loc|[anyOf]|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|msg|string|true|none|none|
|type|string|true|none|none|

