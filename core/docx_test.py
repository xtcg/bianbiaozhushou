from asgi_correlation_id import correlation_id
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as langchain_Document
import json
import sys, os
from api.config import BASEDIR
from core.retrieval import content_retrieve, rerank_content, JinaEmbeddings, section_retrieve, extract_dates_with_context, extract_keyword_content, extract_location_context, extract_money_context
from langchain_community.vectorstores import FAISS
from core.generate import generate_response, generate_respons_pair, generate_check_elements, generate_outline_sections, generate_outline_content, generate_outline_type
from core.json2docx import json2docx
from core.utils import parse_and_combine_content, parse_and_combine_content_review, parse_and_combine_content_review_bid, parse_eval_content, parse_section_info, set_request_id
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Dict, Any, Sequence, Union
from core.docx_parse import Docx, POTENTIAL_PATTERNS
from core.docx_comment import add_comment_to_elements_in_place
from core.docx_outline import Outline

key_review_outline = {
 "关键内容审查": 
        ['项目名称一致性', '项目名称符合性 ', '项目业主一致性', '项目业主符合性', '标段名称一致性', '标段名称符合性', '项目编号一致性', '项目编号符合性', '招标编号一致性', '招标编号符合性', '工期一致性', '工期符合性', '质量', '安全', '落款日期一致性', '落款日期符合性', '不相关地点', '不相关行业', '报价唯一', '人员要求']
}

abstract_outline =  {
"一、项目概况与招标范围":  ["项目名称", "项目业主", "项目背景","项目概况","其他需重点关注的技术要求",
                "建设地点", "质量标准","最高投标限价","投标文件递交", "投标文件截止时间", "招标范围"],
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

def generate_section_content(element: str, query_dict: dict, metadata: dict, all_documents: List[langchain_Document], db_all_documents: FAISS, rag1: List, all_doc):
    tender_element = {}
    seen = set()
    tender_element["section"] = element
    tender_element["reference"] = {}
    query = query_dict[element]
    section_results, page_involved = None, []
    tender_element["reference"]["content"] = []
    try:
        if query.get("front_page", False):
            tender_element["reference"]["content"] = [{'page': metadata[0]['first_index'], 'content': '\n'.join(metadata[0]['text'])}]
        else:
            if section_query:=query.get("section_query", False):
                section_results, page_involved = section_retrieve(section_query, all_documents, rag1)     

            section_docs, docs_filtered = content_retrieve(query, db_all_documents, 20, section_results, page_involved)

            if section_docs:
                try:
                    print(len(docs_filtered))
                    docs = rerank_content(query.get('query', element), docs_filtered, top_n=8)
                    rag_results = section_docs + docs
                except Exception as e:
                    print(element)
                    print(e)
            else:
                global_related = []
                global_retriever = db_all_documents.as_retriever(search_kwargs={'k': 8})
                global_related = global_retriever.invoke(query.get('query','.'))
                reranked_content = rerank_content(query.get('query', element), global_related, top_n=15)

                rag_results = docs_filtered + reranked_content
            right_threshold = query.get('context', 3100)
            mem = []
            all_doc_length = len(all_doc)
            # print(rag_results)
            for rr in rag_results:
                try:
                    pos = all_doc.index(rr.page_content)
                except:
                    print(rr.page_content)
                left = pos
                right = min(all_doc_length,pos+100+right_threshold-len(rr.page_content))
                flag = 0
                # print(rr,left,right)
                for i in range(len(mem)):
                    if  right <= mem[i][1] and left >= mem[i][0]:
                        flag = 1
                        break
                    elif (left - mem[i][1]) * (right - mem[i][0]) <= 0 and right > mem[i][1]:
                        l = mem[i][0]
                        r = (right-mem[i][1])//2+mem[i][1]
                        mem[i] = [l,r,mem[i][2]]
                        flag = 1
                        break
                if flag == 0:
                    mem.append([left,right, rr.metadata['page']])    

        
            for l,r,page in mem:
                tender_element["reference"]["content"].append({'page': page, 'content': all_doc[l:r]})
            if query.get("use_front_page", False):
                tender_element["reference"]["content"] = [{'page': metadata[0]['first_index'], 'content': '\n'.join(metadata[0]['text'])}] + tender_element["reference"]["content"]
        # length_list = [len(x) for x in tender_element["reference"]["content"]]
        tender_element["reference"]["content"][:] = tender_element["reference"]["content"][:16]
        content_page  = generate_response(element, tender_element["reference"]["content"], BASEDIR.joinpath('core/abstract/prompt.json'))
        # content_page = parse_and_combine_content(content_page)
        # content_page = 'a'
        tender_element["ai_result"] = content_page
        tender_element["reference"]["location"] = ', '.join([str(x['page']) for x in tender_element['reference']['content']])
    except Exception as e:
        print(e)
        tender_element["ai_result"] = ''
        tender_element["reference"]["location"] = ''
    return tender_element


def generate_abstract(docx_path: str, temp_path: Optional[str]=None, cache_path: Optional[str]=None):
    doc = Docx(docx_path, use_cache=True) 
    if temp_path or cache_path:
        doc.set_cached_dir(temp_path, cache_path)
    metadata = doc.get_rag()
    
    tender_element_list = []
    tender_element_dict = {}
    
    all_documents = []
    all_documents_split = []
    all_doc = ''
    for dp in metadata:
        cur = '\n'.join(dp['text'])
        if dp['type'] == '目录':continue
        all_doc += cur + '\n'
        for line, index in zip(dp['text'], dp['index']):
            all_documents_split.append(langchain_Document(page_content=line, metadata={"page": index}))
    
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=128,
            chunk_overlap=64,
            length_function=len,
        )
    
    all_documents = [
            document
            for data in all_documents_split
            for document in text_splitter.create_documents([data.page_content], [{"page": data.metadata['page']}])
        ]
    db_all_documents = FAISS.from_documents(documents=all_documents, embedding=JinaEmbeddings)
 
    with open(BASEDIR.joinpath('core/abstract/tender_query.json'), 'r', encoding='utf-8') as file:
        query_dict = json.load(file)
    with ThreadPoolExecutor(max_workers=1, initializer=set_request_id()) as executor:
        future_to_type = {executor.submit(generate_section_content, element, query_dict, metadata, all_documents, db_all_documents, doc.rag1, all_doc): element for element in query_dict.keys()} #["合同价格与支付"]}#
        for future in future_to_type:
            element = future_to_type[future]
            tender_element = future.result()
            tender_element_list.append(tender_element)
            tender_element_dict[element] = {"content": tender_element["ai_result"], "reference": f'对应批注id：'}
            # tender_element_dict[element] = {"content": tender_element["ai_result"], "reference": f'所在页码：{tender_element["reference"]["location"]}'}
    
  
    tender_element_list1 = []
    content = []
    location = ''
    ai_result = ''
    for i in tender_element_list:
        if i['section'].startswith('评分'):
            content += i['reference']['content']
            location += i['reference']['location']
            ai_result += i['ai_result'] + '\n'
    for i in tender_element_list:
        if i['section'].startswith('评分'):
            if i['section'].startswith('评分-商务'):
                tender_element_list1.append({"section": "摘要内容-评标办法",
                                             "reference":{
                                                 "content": content,
                                                 "location": location,
                                             },
                                             "ai_result": ai_result,
                                             })
        else:
            tender_element_list1.append(i)
    with open(os.path.join(doc.cached_dir,'rag_result.json'), 'w') as f:
        json.dump(tender_element_list, f, ensure_ascii=False, indent=4)
    tender_element_dict.pop("评分-商务")
    tender_element_dict.pop("评分-技术")
    tender_element_dict.pop("评分-报价")
    tender_element_dict["摘要内容-评标办法"] = {"content": ai_result, "reference": f'对应批注id：'}
    count = 1
    for info in tender_element_list1:
        comment_text = info['section']
        add_candidate = set()
        i = 0
        while len(add_candidate) < 1 and i < len(info['reference']['content']):
            add_candidate.add(info['reference']['content'][i]['page'])
            i += 1
        for index in add_candidate:
            tmp = index
            while doc.contents['check'][str(tmp)]['type'] == 'table':
                tmp += 1
            try:
                pos = doc.contents['check'][str(tmp)]['index']
         add_comment_to_elements_in_place(doc.doc,[doc.doc.paragraphs[pos]._element],'bianbiaozhushou',comment_text)
                tender_element_dict[info['section']]['reference'] += ' '+str(count)+','
                count += 1
            except Exception as e:
                print(e)
                continue
    doc.doc.save(os.path.join(doc.cached_dir,'comments.docx'))
    json2docx(abstract_outline, tender_element_dict['项目名称']["content"], tender_element_dict, os.path.join(doc.cached_dir,'file.docx') , "商务分析")
    return tender_element_list1, os.path.join(doc.cached_dir,'file.docx'), os.path.join(doc.cached_dir,'comments.docx')


def generate_key_content_check_section(element: str, query_dict: dict, bid_metadata: dict, all_bid_documents: List[langchain_Document], db_all_documents: FAISS, tender_dict: dict, rag1, all_doc):
    check_element = {}
    check_element['section'] = element
    check_element["bid_reference"] = {}
    check_element["tender_reference"] = {}
    element_query = query_dict[element]
    seen, bid_info = set(), list()
    try:
        if p:=element_query.get("location", False):
            bid_info = extract_location_context(bid_metadata, p)
        elif p:=element_query.get("money", False):
            bid_info = extract_money_context(bid_metadata, p)
        elif p:=element_query.get("date", False):
            bid_info = extract_dates_with_context(bid_metadata, p)
        elif keywords:=element_query.get("keywords", False):
            bid_info = extract_keyword_content(bid_metadata, keywords)
        else:
            section_results, page_involved = section_retrieve(element_query.get("bid_section_query", [element]), all_bid_documents, rag1)     
        
            section_docs, docs_filtered = content_retrieve(element_query, db_all_documents, 20, section_results, page_involved)

            if section_docs:    
                rag_results = rerank_content(element_query.get('query', element), section_docs, top_n=8)
            else:
                rag_results = rerank_content(element_query.get('query', element), docs_filtered, top_n=15)

            for rr in rag_results:

                bid_info.append({'page': rr.metadata['page'], 'content': rr.page_content})
        if element_query.get("tender_section", False) or element_query.get("tender_info", False):
            if tender_query:=element_query.get("tender_section", False):
                if isinstance(tender_query, list):
                    tender_info = [f"{j}: {tender_dict[j]}" for j in tender_query]
                    tender_info = "\n".join(tender_info)
                else:
                    tender_info = f"{tender_query}: {tender_dict[tender_query]}"
            elif info:=element_query.get("tender_info", False):
                tender_info = f"{element}: {info}"
        
            content = generate_respons_pair(element, bid_info, tender_info, BASEDIR.joinpath('core/review/prompt.json'))
            content = parse_and_combine_content_review(content)
            
        else:
            content = generate_response(element, bid_info, BASEDIR.joinpath('core/review/prompt.json'), check=False)
            content = parse_and_combine_content_review_bid(content)
        
        check_element["conclusion"] = content["conclusion"]
        check_element["ai_result"] = content["content"]
        check_element["tender_reference"]["location"] = content.get("tender_source", "")
        # check_element["bid_reference"]["location"] = content["page"]
        check_element["bid_reference"]["content"] = bid_info
    except Exception as e:
        print(e)
        check_element["conclusion"] = ''
        check_element["ai_result"] = ''
        check_element["tender_reference"]["location"] = ''
        # check_element["bid_reference"]["location"] = content["page"]
        check_element["bid_reference"]["content"] = []
    return check_element


def generate_key_content_check(tender_list: List[dict], bid_pdf_path: str, temp_path: Optional[str]=None, cache_path: Optional[str]=None):
    bid = Docx(bid_pdf_path)
    if temp_path or cache_path:
        bid.set_cached_dir(temp_path, cache_path)
    bid_metadata = bid.get_rag()
    with open(BASEDIR.joinpath('core/review/bid_query.json'), 'r', encoding='utf-8') as file:
        query_dict = json.load(file)

    check_element_list = []
    check_element_dict = {}

    tender_dict = {}
    for i in tender_list:
        tender_dict[i["section"]] = i["ai_result"]

    all_bid_documents = []
    all_bid_documents_split = []
    all_doc = ''
    for dp in bid_metadata:
        cur = '\n'.join(dp['text'])
        # if dp['type'] == '目录' :continue
        all_doc += cur + '\n'
        for line, index in zip(dp['text'], dp['index']):
            all_bid_documents_split.append(langchain_Document(page_content=line, metadata={"page": index}))


    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=128,
            chunk_overlap=64,
            length_function=len,
        )
    all_documents_splitted = [
            document
            for data in all_bid_documents_split
            for document in text_splitter.create_documents([data.page_content], [{"page": data.metadata['page']}])
        ]
    all_bid_documents.extend(all_documents_splitted)
    try:
        db_all_documents = FAISS.from_documents(documents=all_bid_documents, embedding=JinaEmbeddings)
    except Exception as e:
        print(e)
        db_all_documents = None

    with ThreadPoolExecutor(max_workers=1, initializer=set_request_id()) as executor:
            future_to_type = {executor.submit(generate_key_content_check_section, element, query_dict, bid_metadata, all_bid_documents, db_all_documents, tender_dict, bid.rag1, all_doc): element for element in query_dict.keys()}#["报价唯一"]}
            for future in future_to_type:
                element = future_to_type[future]
                check_element = future.result()
                check_element_list.append(check_element)
                check_element_dict[element] = {"content": check_element["ai_result"], "conclusion": check_element["conclusion"]}
                if len(check_element["tender_reference"]["location"]) > 0:
                    check_element_dict[element]['tender_source'] = f'招标文件信息：{check_element["tender_reference"]["location"]}'
                # , "reference": f'投标文件所在页码：{check_element["bid_reference"]["page"]}'
    with open(os.path.join(bid.cached_dir,"rag_result_key.jsonl"), 'w') as f:
        json.dump(check_element_list, f, ensure_ascii=False, indent=4)
    
    json2docx(key_review_outline, "", check_element_dict, os.path.join(bid.cached_dir,"key_content.docx") , "关键内容审查")
    for info in check_element_list:
        comment_text = info['section']
        add_candidate = set()
        i = 0
        while len(add_candidate) < 1 and i < len(info['bid_reference']['content']):
            add_candidate.add(info['bid_reference']['content'][i]['page'])
            i += 1
        for index in add_candidate:
            tmp = index
            while bid.contents['check'][str(tmp)]['type'] == 'table':
                tmp += 1
            try:
               pos = bid.contents['check'][str(tmp)]['index'] add_comment_to_elements_in_place(bid.doc,[bid.doc.paragraphs[pos]._element],'bianbiaozhushou',comment_text)
                check_element_dict[info['section']]['reference'] += ' '+str(count)+','
                count += 1
            except Exception as e:
                print(e)
                continue
    bid.doc.save(os.path.join(bid.cached_dir,'key_comment.docx'))
    return check_element_list, os.path.join(bid.cached_dir,"key_content.docx"), os.path.join(bid.cached_dir,"key_comment.docx")

def generate_bid_content_check(tender_list: List[dict], bid_pdf_path: str, temp_path: Optional[str]=None, cache_path: Optional[str]=None):
    bid = Docx(bid_pdf_path)
    if temp_path or cache_path:
        bid.set_cached_dir(temp_path, cache_path)
    bid_metadata = bid.get_rag()

    check_element_list = []
    check_element_dict = {}

    tender_dict = {}
    for i in tender_list:
        tender_dict[i["section"]] = i["ai_result"]

    all_bid_documents = []
    all_bid_documents_split = []

    for dp in bid_metadata:
        dp['text'] = '\n'.join(dp['text'])
        if len(dp['text']) < 512:
            all_bid_documents.append(langchain_Document(page_content=dp["text"], metadata={"page": dp["first_index"], 'raw': dp['text']}) )
        else:
            all_bid_documents_split.append(langchain_Document(page_content=dp["text"], metadata={"page": dp["first_index"], 'raw': dp['text']}) )

    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
        )
    all_documents_splitted = [
            document
            for data in all_bid_documents_split
            for document in text_splitter.create_documents([data.page_content], [{"page": data.metadata['page'], 'raw': data.metadata['raw']}])
        ]
    all_bid_documents.extend(all_documents_splitted)
    db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)

    content = generate_check_elements(tender_dict["审查内容-评标办法"])
    eval_dict = parse_eval_content(content)

    with ThreadPoolExecutor(max_workers=1, initializer=set_request_id()) as executor:
            future_to_type = {executor.submit(generate_key_content_check_section, element, eval_dict, bid_metadata, all_bid_documents, db_all_documents, tender_dict, bid.rag1): element for element in eval_dict.keys()}
            for future in future_to_type:
                element = future_to_type[future]
                check_element = future.result()
                check_element_list.append(check_element)
                check_element_dict[element] = {"content": check_element["ai_result"],  "conclusion": check_element["conclusion"]}
                # "reference": f'投标文件所在页码：{check_element["bid_reference"]["location"]}',
                if len(check_element["tender_reference"]["location"]) > 0:
                    check_element_dict[element]['tender_source'] = f'招标文件信息：{check_element["tender_reference"]["location"]}'
    
    with open(os.path.join(bid.cached_dir,'rag_result_bid.json'), 'w') as f:
        json.dump(check_element_list, f, ensure_ascii=False, indent=4)
    
    outline = {
        "响应招标文件内容审查": list(eval_dict.keys())
    }
    json2docx(outline, "", check_element_dict, os.path.join(bid.cached_dir,'bid_content.docx') , "响应招标文件内容审查")
    for info in check_element_list:
        comment_text = info['section']
        add_candidate = set()
        i = 0
        while len(add_candidate) < 1 and i < len(info['bid_reference']['content']):
            add_candidate.add(info['bid_reference']['content'][i]['page'])
            i += 1
        for index in add_candidate:
            tmp = index
            while bid.contents['check'][str(tmp)]['type'] == 'table':
                tmp += 1
            try:
               pos = bid.contents['check'][str(tmp)]['index'] add_comment_to_elements_in_place(bid.doc,[bid.doc.paragraphs[pos]._element],'bianbiaozhushou',comment_text)
                check_element_dict[info['section']]['reference'] += ' '+str(count)+','
                count += 1
            except Exception as e:
                print(e)
                continue
    bid.doc.save(os.path.join(bid.cached_dir,'bid_comment.docx'))
    return check_element_list, os.path.join(bid.cached_dir,'bid_content.docx'), os.path.join(doc.cached_dir,'bid_comment.docx')


def generate_outline(tender_pdf_path: str,  temp_path: Optional[str]=None, cache_path: Optional[str]=None):
    tender = Outline(tender_pdf_path, use_cache=False, temp_path = temp_path, hash_path = cache_path)
    
    ok, target = tender.find_target_in_catalogs()
    if not ok:
        return os.path.join(tender.cached_dir,'outline.docx')
    ok, split_index = tender.find_entry(target)
    if not ok :
        return os.path.join(tender.cached_dir,'outline.docx')
    
    if len(split_index) == 2:
        ok, split_index = tender.find_split(split_index)
        if not ok:
            split_index = tender.find_split1(split_index)
    
    split_index.sort()
    comments = tender.get_split_type(split_index)
    tender.add_comments(split_index, comments)
    return os.path.join(tender.cached_dir,'outline.docx')


    
    
# def generate_outline_section_content(element, db_after_documents, db_all_documents):

#     _, results = content_retrieve(element, db_after_documents, 20)
#     rag_results = rerank_content(element, results, top_n=5)
#     rag_info = [{"content": i.page_content, "page": i.metadata["page"]} for i in rag_results]
    
#     _, eval_results = content_retrieve(element, db_all_documents, 20)
#     eval_rag_results = rerank_content(element, eval_results, top_n=5)
#     eval_info = [{"content": j.page_content, "page": j.metadata["page"]} for j in eval_rag_results]

    
#     content = generate_outline_content(element, rag_info, eval_info)

#     return content



if __name__ == "__main__":
    # import time
    # t1 = time.time()
    # tender_list, _, _= generate_abstract("/home/ron/jiamin/bianbiaozhushou/data/test_docx/金华/【已脱敏】浙江金华招标文件.docx")
    # tender_list, _, _= generate_abstract("/home/ron/jiamin/bianbiaozhushou/data/test_docx/招标文件-大唐博罗公庄镇 150MW 复合型光伏发电项目.docx")
    generate_abstract("/home/bianbiaozhushou/data/test_docx/（招标文件）永嘉县乌牛交通枢纽互通连接线工程.docx")
    # generate_abstract("/home/ron/jiamin/bianbiaozhushou/data/test_docx/招标文件正文.docx")
    # generate_abstract("/home/ron/jiamin/bianbiaozhushou/data/test/(招标文件)贵州华电黔西南册亨岩架90MW风电项目风场区EPC总承包.docx")
    # generate_outline('/home/ron/jiamin/bianbiaozhushou/data/test_docx/（招标文件）八步仁义风电场项目EPC总承包工程招标文件（第一卷  商务部分）-2024.3.13发布版.docx')
    # generate_outline('/home/ron/jiamin/bianbiaozhushou/data/test_docx/（招标文件）大唐博罗公庄镇 150MW 复合型光伏发电项目.docx')
    # from concurrent.futures import ThreadPoolExecutor, as_completedcd
    # results = []
    # with ThreadPoolExecutor(max_workers=10) as executor:
    #     futures = [executor.submit(generate_outline, '/home/ron/jiamin/bianbiaozhushou/data/test/'+file) for file in os.listdir('/home/ron/jiamin/bianbiaozhushou/data/test')]
    #     for future in as_completed(futures):
    #         results.append(future.result())
    # generate_outline('/home/ron/jiamin/bianbiaozhushou/data/test/（招标文件）绍兴市越城区东湖街道高平、仁渎村千亩方永久基本农田连片整治设计、施工、采购、运营一体化项目招标文件.docx')
    # for file in os.listdir('/home/ron/jiamin/bianbiaozhushou/data/test_docx'):
    #     if file.endswith('docx'):
    #         generate_outline('/home/ron/jiamin/bianbiaozhushou/data/test_docx/'+file)
    # generate_outline("/home/ron/jiamin/bianbiaozhushou/data/test_docx/内蒙古库布齐沙漠鄂尔多斯中北部新能源基地700万千瓦光伏项目工程设计施工采购.docx")
    # generate_outline("/home/ron/jiamin/bianbiaozhushou/data/test_docx/00中核寒亭固堤街道300MW光伏发电乡村振兴示范基地项目光伏EPC总承包招标文件（发布稿） (1).docx")
    # with open('/home/ron/jiamin/bianbiaozhushou/data/【已脱敏】浙江金华招标文件/rag_result.json', 'r') as f:
    #     tender_list = json.load(f)
    # t2 = time.time()
    # print("t1", t2-t1)
    # # with open(f"/home/star/jiamin/bianbiaozhushou/code/data/【已脱敏】青青草原(招标文件)/rag_results.json", 'r', encoding='utf-8') as file:
    # #     tender_list = json.load(file)
    # generate_key_content_check(tender_list, '/home/ron/jiamin/bianbiaozhushou/data/test_docx/金华/【已脱敏】浙江金华投标文件.docx')
    # t3 = time.time()
    # print("t2", t3-t2)
    # generate_bid_content_check(tender_list, '/home/ron/jiamin/bianbiaozhushou/data/test_docx/金华/【已脱敏】浙江金华投标文件.docx')
    # with open('/home/ron/jiamin/bianbiaozhushou/data/00中核寒亭固堤街道300MW光伏发电乡村振兴示范基地项目光伏EPC总承包招标文件（发布稿） (1)/rag_result.json', 'r') as f:
    #     tender_list = json.load(f)
    # generate_key_content_check(tender_list, '/home/ron/jiamin/bianbiaozhushou/data/bid/中核光伏项目商务投标文件 (5).docx')
    # generate_bid_content_check(tender_list, '/home/ron/jiamin/bianbiaozhushou/data/bid/中核光伏项目商务投标文件 (5).docx')
    # for file in os.listdir('/home/ron/jiamin/bianbiaozhushou/data/test_docx'):
    #     if file != '(招标文件)贵州华电望谟蔗香望南一期150MW农业光伏电站项目EPC总承包.docx':
    #         continue
    #     if file.endswith('docx'):
    #         tender_list,_,_ = generate_abstract(os.path.join('/home/ron/jiamin/bianbiaozhushou/data/test_docx',file))
            # with open('/home/ron/jiamin/bianbiaozhushou/data/'+file.replace('.docx', '')+'/rag_result.json', 'r') as f:
            #     tender_list = json.load(f)
    #         generate_key_content_check(tender_list, os.path.join('/home/ron/jiamin/bianbiaozhushou/data/test_docx',file))
            # doc = Docx(os.path.join('/home/ron/jiamin/bianbiaozhushou/data/test_docx',file))
            # doc.get_rag()
            # try:
            #     generate_outline(os.path.join('/home/ron/jiamin/bianbiaozhushou/data/test_docx',file))
            # except Exception as e:
            #     print(e)
            #     print(file)
    # t4 = time.time()
    # print("t3", t4-t3)
    # docx2pdf.convert('/home/ron/jiamin/bianbiaozhushou/data/test_docx/提瓦特/提瓦特-招标文件脱敏稿.docx','/home/ron/jiamin/bianbiaozhushou/data/test_pdf/提瓦特/提瓦特-招标文件脱敏稿.pdf')
    
    # generate_outline('/home/ron/jiamin/bianbiaozhushou/data/test_docx/内蒙古库布齐沙漠鄂尔多斯中北部新能源基地700万千瓦光伏项目工程设计施工采购.docx')
    # generate_outline('/home/ron/jiamin/bianbiaozhushou/data/test_docx/招标文件-大唐博罗公庄镇 150MW 复合型光伏发电项目.docx')
    # generate_abstract('/home/ron/jiamin/bianbiaozhushou/data/test_docx/(招标文件)贵州华电望谟蔗香望南一期150MW农业光伏电站项目EPC总承包.docx')
    # generate_outline('/home/ron/jiamin/bianbiaozhushou/data/test_pdf/ZJZC-AJ2024-004“智慧黄浦江源”数字化管理系统建设项目（定稿）.docx')
    # doc = Docx('/home/ron/jiamin/bianbiaozhushou/data/test_docx/(招标文件)贵州华电望谟蔗香望南一期150MW农业光伏电站项目EPC总承包.docx')