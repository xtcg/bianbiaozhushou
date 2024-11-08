from asgi_correlation_id import correlation_id
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as langchain_Document
import json
import sys, os
sys.path.append(os.path.abspath('/home/ron/jiamin/bianbiaozhushou'))
from api.config import BASEDIR
from core.retrieval import content_retrieve, rerank_content, JinaEmbeddings, section_retrieve, extract_dates_with_context, extract_keyword_content, extract_location_context, extract_money_context
from langchain_community.vectorstores import FAISS
from core.pdf_parser import parse_pdf_with_pages
from core.generate import generate_response, generate_respons_pair, generate_check_elements, generate_outline_sections, generate_outline_content
from core.json2docx import json2docx
from core.utils import parse_and_combine_content, parse_and_combine_content_review, parse_and_combine_content_review_bid, parse_eval_content, parse_section_info, set_request_id
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any, Sequence, Union

key_review_outline = {
    "关键内容审查":
        ['项目名称一致性', '项目名称符合性 ', '项目业主一致性', '项目业主符合性', '标段名称一致性', '标段名称符合性',
         '项目编号一致性', '项目编号符合性', '招标编号一致性', '招标编号符合性', '工期一致性', '工期符合性', '质量',
         '安全', '落款日期一致性', '落款日期符合性', '不相关地点', '不相关行业', '报价唯一', '人员要求']
}

abstract_outline = {
    "一、项目概况与招标范围": ["项目名称", "项目业主", "项目背景", "项目概况", "其他需重点关注的技术要求",
                              "建设地点", "质量标准", "最高投标限价", "投标文件递交", "投标文件截止时间", "招标范围"],
    "二、资信及业绩要求": ["资质要求", "业绩要求"],
    "三、主要人员资格要求、财务要求、信誉要求": ["人员、财务与信誉要求", "其他要求"],
    "四、踏勘现场": ["踏勘现场"],
    "五、最高投标限价": ["最高投标限价"],
    "六、评标方法": ["摘要内容-评标办法"],
    "七、合同价格与支付": ["合同价格与支付"],
    "八、罚则": ["罚则"],
    "九、其他合同条件": [],
    "十、投标报价": []
}

def generate_section_content(element: str, query_dict: dict, metadata: dict, all_documents: List[langchain_Document], db_all_documents: FAISS):
    tender_element = {}
    tender_element["section"] = element
    tender_element["reference"] = {}
    query = query_dict[element]
    section_results, page_involved = None, []
    if query.get("front_page", False):
        tender_element["reference"]["content"] = [metadata[0]]
    else:
        if section_query := query.get("section_query", False):
            section_results, page_involved = section_retrieve(section_query, all_documents)

        section_docs, docs_filtered = content_retrieve(
            query.get('query', element), db_all_documents, 20, section_results, page_involved
            )

        if section_docs:
            rag_results = rerank_content(query.get('query', element), section_docs, top_n=8)
        else:
            rag_results = rerank_content(query.get('query', element), docs_filtered, top_n=15)

        tender_element["reference"]["content"] = [{'page': rr.metadata['page'], 'content': rr.page_content} for rr in
                                                  rag_results]
        if query.get("use_front_page", False):
            tender_element["reference"]["content"] = [metadata[0]] + tender_element["reference"]["content"]

    content_page, content = generate_response(
        element, tender_element["reference"]["content"], BASEDIR.joinpath('core/abstract/prompt.json')
        )
    content_page = parse_and_combine_content(content_page)
    tender_element["ai_result"] = content
    tender_element["reference"]["location"] = content_page["page"]
    return tender_element


def generate_abstract(pdf_path: str, temp_path: Optional[str] = None, cache_path: Optional[str] = None):
    pdf_outpath = parse_pdf_with_pages(pdf_path, cache_path)
    tender_element_list = []
    tender_element_dict = {}
    if temp_path is None:
        temp_path = pdf_outpath
    with open(f"{temp_path}/file_hash.txt", 'w', encoding='utf-8') as pdf_file:
        request_id = correlation_id.get()
        pdf_file.write(pdf_outpath + "\n")
        pdf_file.write(request_id)

    with open(f"{pdf_outpath}/pdf_results.json", 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    all_documents = []
    for dp in metadata:
        all_documents.append(langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]}))

    with open(BASEDIR.joinpath('core/abstract/tender_query.json'), 'r', encoding='utf-8') as file:
        query_dict = json.load(file)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )
    all_documents_splitted = [
        document
        for data in all_documents
        for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
    ]
    db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)

    with ThreadPoolExecutor(max_workers=30, initializer=set_request_id()) as executor:
        future_to_type = {executor.submit(
            generate_section_content, element, query_dict, metadata, all_documents, db_all_documents
            ): element for element in query_dict.keys()}
        for future in future_to_type:
            element = future_to_type[future]
            tender_element = future.result()
            tender_element_list.append(tender_element)
            tender_element_dict[element] = {
                "content": tender_element["ai_result"],
                "reference": f'所在页码：{tender_element["reference"]["location"]}'
            }

    # print(element_dict)
    with open(f'{temp_path}/rag_results.json', 'w') as f:
        json.dump(tender_element_list, f, ensure_ascii=False, indent=4)

    json2docx(
        abstract_outline, tender_element_dict['项目名称']["content"], tender_element_dict, f"{temp_path}/file.docx",
        "商务分析"
        )

    return tender_element_list, f"{temp_path}/file.docx"


def generate_key_content_check_section(element: str, query_dict: dict, bid_metadata: dict, all_bid_documents: List[langchain_Document], db_all_documents: FAISS, tender_dict: dict):
    check_element = {}
    check_element['section'] = element
    check_element["bid_reference"] = {}
    check_element["tender_reference"] = {}
    element_query = query_dict[element]
    if p := element_query.get("location", False):
        bid_info = extract_location_context(bid_metadata, p)
    elif p := element_query.get("money", False):
        bid_info = extract_money_context(bid_metadata, p)
    elif p := element_query.get("date", False):
        bid_info = extract_dates_with_context(bid_metadata, p)
    elif keywords := element_query.get("keywords", False):
        bid_info = extract_keyword_content(bid_metadata, keywords)
    else:
        section_results, page_involved = section_retrieve(
            element_query.get("bid_section_query", element), all_bid_documents
            )

        section_docs, docs_filtered = content_retrieve(
            element_query.get('query', element), db_all_documents, 20, section_results, page_involved
            )

        if section_docs:
            bid_info = rerank_content(element_query.get('query', element), section_docs, top_n=8)
        else:
            bid_info = rerank_content(element_query.get('query', element), docs_filtered, top_n=15)

        bid_info = [{'page': rr.metadata['page'], 'content': rr.page_content} for rr in bid_info]

    if element_query.get("tender_section", False) or element_query.get("tender_info", False):
        if tender_query := element_query.get("tender_section", False):
            if isinstance(tender_query, list):
                tender_info = [f"{j}: {tender_dict[j]}" for j in tender_query]
                tender_info = "\n".join(tender_info)
            else:
                tender_info = f"{tender_query}: {tender_dict[tender_query]}"
        elif info := element_query.get("tender_info", False):
            tender_info = f"{element}: {info}"

        content = generate_respons_pair(element, bid_info, tender_info, BASEDIR.joinpath('core/review/prompt.json'))
        content = parse_and_combine_content_review(content)

    else:
        content = generate_response(element, bid_info, BASEDIR.joinpath('core/review/prompt.json'), check=False)
        content = parse_and_combine_content_review_bid(content)

    check_element["conclusion"] = content["conclusion"]
    check_element["ai_result"] = content["content"]
    check_element["tender_reference"]["location"] = content.get("tender_source", "")
    check_element["bid_reference"]["location"] = content["page"]
    check_element["bid_reference"]["content"] = bid_info
    return check_element


def generate_key_content_check(tender_list: List[dict], bid_pdf_path: str, temp_path: Optional[str]=None, cache_path: Optional[str]=None):
    bid_pdf_outpath = parse_pdf_with_pages(bid_pdf_path, cache_path)
    if temp_path is None:
        temp_path = bid_pdf_outpath
    with open(f"{temp_path}/file_hash.txt", 'w', encoding='utf-8') as pdf_file:
        pdf_file.write(bid_pdf_outpath)

    with open(f"{bid_pdf_outpath}/pdf_results.json", 'r', encoding='utf-8') as file:
        bid_metadata = json.load(file)
    with open(BASEDIR.joinpath('core/review/bid_query.json'), 'r', encoding='utf-8') as file:
        query_dict = json.load(file)

    check_element_list = []
    check_element_dict = {}

    tender_dict = {}
    for i in tender_list:
        tender_dict[i["section"]] = i["ai_result"]

    all_bid_documents = []
    for dp in bid_metadata:
        all_bid_documents.append(langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]}))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )
    all_documents_splitted = [
        document
        for data in all_bid_documents
        for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
    ]
    db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)

    with ThreadPoolExecutor(max_workers=10, initializer=set_request_id()) as executor:
        future_to_type = {executor.submit(
            generate_key_content_check_section, element, query_dict, bid_metadata, all_bid_documents, db_all_documents,
            tender_dict
            ): element for element in query_dict.keys()}
        for future in future_to_type:
            element = future_to_type[future]
            check_element = future.result()
            check_element_list.append(check_element)
            check_element_dict[element] = {
                "content": check_element["ai_result"],
                "reference": f'投标文件所在页码：{check_element["bid_reference"]["location"]}',
                "conclusion": check_element["conclusion"],
                "tender_source": f'招标文件信息：{check_element["tender_reference"]["location"]}'
            }

    # print(element_dict)
    with open(f'{temp_path}/rag_results_key.json', 'w') as f:
        json.dump(check_element_list, f, ensure_ascii=False, indent=4)

    json2docx(key_review_outline, "", check_element_dict, f"{temp_path}/key_content.docx", "关键内容审查")

    return check_element_list, f"{temp_path}/key_content.docx"


def generate_bid_content_check(tender_list: List[dict], bid_pdf_path: str, temp_path: Optional[str]=None, cache_path: Optional[str]=None):
    bid_pdf_outpath = parse_pdf_with_pages(bid_pdf_path, cache_path)
    with open(f"{bid_pdf_outpath}/pdf_results.json", 'r', encoding='utf-8') as file:
        bid_metadata = json.load(file)
    if temp_path is None:
        temp_path = bid_pdf_outpath
    with open(f"{temp_path}/file_hash.txt", 'w', encoding='utf-8') as pdf_file:
        pdf_file.write(bid_pdf_outpath)

    check_element_list = []
    check_element_dict = {}

    tender_dict = {}
    for i in tender_list:
        tender_dict[i["section"]] = i["ai_result"]

    all_bid_documents = []
    for dp in bid_metadata:
        all_bid_documents.append(langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]}))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )
    all_documents_splitted = [
        document
        for data in all_bid_documents
        for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
    ]
    db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)

    content = generate_check_elements(tender_dict["审查内容-评标办法"])
    eval_dict = parse_eval_content(content)

    with ThreadPoolExecutor(max_workers=10, initializer=set_request_id()) as executor:
        future_to_type = {executor.submit(
            generate_key_content_check_section, element, eval_dict, bid_metadata, all_bid_documents, db_all_documents,
            tender_dict
            ): element for element in eval_dict.keys()}
        for future in future_to_type:
            element = future_to_type[future]
            check_element = future.result()
            check_element_list.append(check_element)
            check_element_dict[element] = {
                "content": check_element["ai_result"],
                "reference": f'投标文件所在页码：{check_element["bid_reference"]["location"]}',
                "conclusion": check_element["conclusion"],
                "tender_source": f'招标文件信息：{check_element["tender_reference"]["location"]}'
            }

    # print(element_dict)
    with open(f'{temp_path}/rag_results_bid.json', 'w') as f:
        json.dump(check_element_list, f, ensure_ascii=False, indent=4)

    outline = {
        "响应招标文件内容审查": list(eval_dict.keys())
    }
    json2docx(outline, "", check_element_dict, f"{temp_path}/bid_content.docx", "响应招标文件内容审查")

    return check_element_list, f"{temp_path}/bid_content.docx"


def generate_outline(tender_pdf_path: str, temp_path: Optional[str] = None, cache_path: Optional[str] = None):
    outline = {}
    pdf_outpath = parse_pdf_with_pages(tender_pdf_path, cache_path)
    with open(f"{pdf_outpath}/pdf_results.json", 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    if temp_path is None:
        temp_path = pdf_outpath
    with open(f"{temp_path}/file_hash.txt", 'w', encoding='utf-8') as pdf_file:
        pdf_file.write(pdf_outpath)

    all_documents = []
    for dp in metadata:
        all_documents.append(langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]}))

    section_results, page_involved = section_retrieve(["章投标文件格式\n目录"], all_documents, following=1)

    page_involved_filtered = []
    section_results_filtered = []
    for i in section_results:
        if i.metadata["page"] not in ["封面", "目录", '1', '2', '3']:
            section_results_filtered.append(i.page_content)
            page_involved_filtered.append(i.metadata["page"])

    section_content = generate_outline_sections(section_results_filtered)
    sections = parse_section_info(section_content)

    after_section_documents = []
    section_documents = []
    for dp in metadata:
        section_documents.append(langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]}))
        if (dp["page"] > min(page_involved_filtered)) and (dp["page"] not in ["封面", "目录", '1', '2', '3']):
            after_section_documents.append(
                langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]})
                )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=100,
        length_function=len,
    )

    after_documents_splitted = [
        document
        for data in after_section_documents
        for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
    ]
    db_after_documents = FAISS.from_documents(documents=after_documents_splitted, embedding=JinaEmbeddings)

    all_documents_splitted = [
        document
        for data in section_documents
        for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
    ]
    db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)

    with ThreadPoolExecutor(max_workers=10, initializer=set_request_id()) as executor:
        future_to_type = {
            executor.submit(generate_outline_section_content, element, db_after_documents, db_all_documents): element
            for element in sections}
        for future in future_to_type:
            element = future_to_type[future]
            outline_element = future.result()
            outline[element] = outline_element

    json2docx(outline, "", {}, f"{temp_path}/outline.docx", "大纲")
    return f"{temp_path}/outline.docx"


def generate_outline_section_content(element, db_after_documents, db_all_documents):
    _, results = content_retrieve(element, db_after_documents, 20)
    rag_results = rerank_content(element, results, top_n=5)
    rag_info = [{"content": i.page_content, "page": i.metadata["page"]} for i in rag_results]

    _, eval_results = content_retrieve(element, db_all_documents, 20)
    eval_rag_results = rerank_content(element, eval_results, top_n=5)
    eval_info = [{"content": j.page_content, "page": j.metadata["page"]} for j in eval_rag_results]

    content = generate_outline_content(element, rag_info, eval_info)

    return content


if __name__ == "__main__":
    # import time
    # t1 = time.time()
    tender_list, _ = generate_abstract(
        "/home/star/jiamin/bianbiaozhushou/test_cases/bid_files/内蒙古库布齐沙漠鄂尔多斯中北部新能源基地700万千瓦光伏项目工程设计施工采购.pdf"
        )
    # t2 = time.time()
    # print("t1", t2-t1)
    # # with open(f"/home/star/jiamin/bianbiaozhushou/code/data/【已脱敏】青青草原(招标文件)/rag_results.json", 'r', encoding='utf-8') as file:
    # #     tender_list = json.load(file)
    generate_key_content_check(tender_list, '/home/star/jiamin/bianbiaozhushou/test_cases/bid-tender/【已脱敏】(004)青青草原(商务标).pdf')
    # t3 = time.time()
    # print("t2", t3-t2)
    generate_bid_content_check(tender_list, '/home/star/jiamin/bianbiaozhushou/test_cases/bid-tender/【已脱敏】(004)青青草原(商务标).pdf')
    # t4 = time.time()
    # print("t3", t4-t3)
    # docx2pdf.convert('/home/ron/jiamin/bianbiaozhushou/data/test_docx/提瓦特/提瓦特-招标文件脱敏稿.docx','/home/ron/jiamin/bianbiaozhushou/data/test_pdf/提瓦特/提瓦特-招标文件脱敏稿.pdf')
    # generate_outline("/home/star/jiamin/bianbiaozhushou/test_cases/bid_files/招标文件-大唐博罗公庄镇 150MW 复合型光伏发电项目.pdf")
