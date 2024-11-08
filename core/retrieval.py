from typing import Optional, List, Dict, Any, Sequence, Union
from langchain_core.documents import Document as langchain_Document
from langchain_core.embeddings import Embeddings
import json
from langchain_community.vectorstores import FAISS
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import numpy as np
import math
# import jieba
from core.utils import timer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os


# def default_preprocessing_func(text: str) -> List[str]:
#     return list(jieba.cut_for_search(text))


class RagEmbeddings(Embeddings):
    def __init__(self, url: str, cpu: Optional[bool] = False) -> None:
        super().__init__()
        self.url = url
        self.cpu = cpu
    
    def get_batch_embedding(self, batch_texts):
        payload = {"inputs": batch_texts}
        response = requests.post(self.url, json=payload)
        if response.status_code == 200:
            return np.array(response.json())
        else:
            raise ValueError(f"Error Code {response.status_code}, {response.text}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.cpu:
            payload = {"text": texts}
            response = requests.post(self.url, json=payload)
            if response.status_code == 200:
                return np.array(response.json())
            else:
                raise ValueError(f"Error Code {response.status_code}, {response.text}")
        else:
            length_per_batch = max([len(text) for text in texts])
            num_batch = min(512, 200000//length_per_batch)
            batches = math.ceil(len(texts) / num_batch)
            _results = [None] * batches
            with ThreadPoolExecutor(max_workers=8) as executor:
                future_map = {
                    executor.submit(self.get_batch_embedding, texts[i * num_batch: (i+ 1) * num_batch] ): i
                    for i in range(batches)
                }
                for future in as_completed(future_map):
                    index = future_map[future]
                    _results[index] = future.result()
            results = np.concatenate(_results, axis=0)
            return results
   
    def embed_query(self, text: str) -> List[float]:   
        return self.embed_documents([text])[0]


JinaEmbeddings = RagEmbeddings(url=os.environ.get("EMBEDDING_URL", "http://192.168.129.84:40068/embed"))
RERANKER_URL = os.environ.get("RERANKING_URL", "http://192.168.129.84:40062/rerank")

@timer
def section_retrieve(query: List, all_documents: List[langchain_Document], rag1: List, following: Optional[int]=3):
    ## all documents除去封面、目录页
    results = []
    pages_involved = []
    if isinstance(query[0],str):
        for doc_id, doc in enumerate(all_documents):
            if any(q in doc.page_content for q in query):
                number_pages = [dp.metadata['page'] for dp in all_documents[doc_id: (doc_id+following)]]
                results.append(langchain_Document(page_content=doc.page_content, metadata={'page': doc.metadata['page']}))
                pages_involved.extend(number_pages)
    else:
        for info in query:
            if int(info[0]) - 1 >= len(rag1):
                for doc_id, doc in enumerate(all_documents):
                    if any(q in doc.page_content for q in info[1:]):
                        number_pages = [dp.metadata['page'] for dp in all_documents[doc_id: (doc_id+following)]]
                        results.append(langchain_Document(page_content=doc.page_content, metadata={'page': doc.metadata['page']}))
                        pages_involved.extend(number_pages)
            else:
                results.extend([langchain_Document(page_content=line,metadata={'page':index, 'raw':'\n'.join(rag1[int(info[0]) - 1]['text'])}) for line, index in zip(rag1[int(info[0]) - 1]['text'],rag1[int(info[0]) - 1]['index'])])
                pages_involved.extend(rag1[int(info[0]) - 1]['index'])
    return results, pages_involved


def split_text_by_pattern(text):
    # 使用正则表达式以 "\nx.x" 分割，但不切分包含额外级别的 "\nx.x.x"
    # “(?<!\.\d)” 是一个负向后查找，确保不匹配 ".x" 后面跟着 ".x"
    pattern = re.compile(r'\n(\d+\.\d+)(?=[\u4e00-\u9fff])')
    parts = pattern.split(text)
    sections = {}
    current_section = '0.0'
    sections[current_section] = ""
    
    # 遍历分割后的文本片段
    for part in parts:
        # 检查是否匹配章节编号
        if re.match(r'\d+\.\d+$', part):
            current_section = part.strip()
            sections[current_section] = current_section
        else:
            # 添加文本到当前章节
            sections[current_section] += part.strip() + "\n"
    
    return list(sections.values())


@timer
def content_retrieve(query: dict, db_all_documents: FAISS, k_total: int, section_documents: Optional[List[langchain_Document]]=[], section_pages: Optional[List]=[]):
    section_docs = []
    sections_mentioned = []
    query_list = list()
    if section_documents:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=128,
            chunk_overlap=64,
            length_function=len,
        )
        section_splitted_sections = []
        for doc_section in section_documents:   
            for document in text_splitter.create_documents([doc_section.page_content], [{"page": doc_section.metadata['page']}]):
                section_splitted_sections.append(langchain_Document(page_content=document.page_content, metadata={'page': doc_section.metadata['page']}))
        db_by_section = FAISS.from_documents(documents=section_splitted_sections, embedding=JinaEmbeddings)
        section_retriever = db_by_section.as_retriever(search_kwargs={'k': k_total//2})
        section_docs = section_retriever.invoke(query.get('query','.'))
        for info in query.get('section_query',[]):
            if isinstance(info, str):
                query_list.append(info)
            else:
                for inf in info[1:]:
                    query_list.append(inf)
        for q in query_list:
            for dp in section_splitted_sections:
                if q in dp.page_content:
                    sections_mentioned.append(dp)
    else:
        section_documents = []
        global_retriever = db_all_documents.as_retriever(search_kwargs={'k': k_total})
        section_docs = global_retriever.invoke(query.get('query','.'))
    # print(sections_mentioned[:2])
    if query.get('latter', False) and len(sections_mentioned) >= 2 and sections_mentioned[0].metadata['page'] < sections_mentioned[1].metadata['page']:
        sections_mentioned[0], sections_mentioned[1] = sections_mentioned[1],sections_mentioned[0]
    # res = []
    # seen = set([i.page_content + str(i.metadata['page']) for i in sections_mentioned])
    # for i in section_docs:
    #     if i.page_content + str(i.metadata['page']) not in seen:
    #         res.append(i)
    #         seen.add(i.page_content + str(i.metadata['page']))
    return sections_mentioned, section_docs

@timer
def rerank_content(query: str, docs: List[langchain_Document], top_n: Optional[int]=10):
    
    payload = {"query": query, "texts": [doc.page_content[:512] for doc in docs]}
    response = requests.post(RERANKER_URL, json=payload)
    if response.status_code == 200:
        relevance = np.array(response.json())
    else:
        raise ValueError(f"Error Code {response.status_code}, {response.text}")
    
    text_selected = [docs[dp['index']] for dp in relevance[:top_n]]
    return text_selected


def extract_dates_with_context(documents: List[dict], pattern: Optional[str]='(\\d+年)?\\d+月\\d+日'):
    # 定义正则表达式，匹配 "x年x月x日" 或 "x月x日"
    date_pattern = re.compile(pattern)

    # 存储结果的列表
    results = []

    for i, doc in enumerate(documents):
        # page = doc['page']
        # content = doc['content']
        page = doc['first_index']
        content = '\n'.join(doc['text'])

        # 找到所有匹配的日期
        matches = list(date_pattern.finditer(content))

        for match in matches:
            start, end = match.span()

            # 尝试截取前后100个词的范围
            start_context = max(0, start - 100)
            end_context = min(len(content), end + 100)

            # 获取前后的内容
            context = content[start_context:end_context]

            # 如果前面的内容不足，尝试从前一个文档获取
            if start_context == 0 and i > 0:
                prev_content = ''.join(documents[i-1]['text'])
                needed = 100 - start  # 计算还需要多少字符
                extended_start = max(0, len(prev_content) - needed)
                context = prev_content[extended_start:] + context

            # 如果后面的内容不足，尝试从后一个文档获取
            if end_context == len(content) and i < len(documents) - 1:
                next_content = ''.join(documents[i+1]['text'])
                needed = 100 - (len(content) - end)  # 计算还需要多少字符
                extended_end = min(len(next_content), needed)
                context += next_content[:extended_end]

            # 将结果添加到列表中
            results.append({
                'page': page,
                'date': match.group(),
                'content': context
            })

    return results


def extract_keyword_content(documents: List[dict], keywords: List[str]):
    pattern_keywords = []
    for keyword in keywords:
        # 使用 \s* 来匹配任意数量的空白字符，包括换行符
        pattern = r'\s*'.join(map(re.escape, keyword))
        pattern_keywords.append(pattern)
    
    keyword_pattern = re.compile('|'.join(pattern_keywords))

    # 存储结果的列表
    results = []

    for i, doc in enumerate(documents):
        # page = doc['page']
        # content = doc['content']
        page = doc['first_index']
        content = '\n'.join(doc['text'])

        # 找到所有关键词的匹配项
        try:
            matches = list(keyword_pattern.finditer(content))
        except:
            print("!!!",content,keyword_pattern)
        for match in matches:
            start, end = match.span()

            # 尝试截取前后100个词的范围
            start_context = max(0, start - 100)
            end_context = min(len(content), end + 100)

            # 获取前后的内容
            context = content[start_context:end_context]

            # 如果前面的内容不足，尝试从前一个文档获取
            if start_context == 0 and i > 0:
                prev_content = ''.join(documents[i-1]['text'])
                needed = 100 - start  # 计算还需要多少字符
                extended_start = max(0, len(prev_content) - needed)
                context = prev_content[extended_start:] + context

            # 如果后面的内容不足，尝试从后一个文档获取
            if end_context == len(content) and i < len(documents) - 1:
                next_content = ''.join(documents[i+1]['text'])
                needed = 100 - (len(content) - end)  # 计算还需要多少字符
                extended_end = min(len(next_content), needed)
                context += next_content[:extended_end]

            # 将结果添加到列表中
            results.append({
                'page': page,
                # 'keyword': match.group().replace('\n', '\\n'),
                'content': context
            })

    return results


def extract_money_context(documents, pattern=r'\d{1,3}(?:,\d{3})*(?:\.\d+)?元'):
    # 定义正则表达式，匹配 "x元" 的模式，其中 x 是数字，可能包括逗号和小数点
    money_pattern = re.compile(pattern)
    # 存储结果的列表
    results = []

    for i, doc in enumerate(documents):
        # page = doc['page']
        # content = doc['content']
        page = doc['first_index']
        content = '\n'.join(doc['text'])

        # 找到所有关键词的匹配项
        matches = list(money_pattern.finditer(content))
        for match in matches:
            start, end = match.span()

            # 尝试截取前后100个词的范围
            start_context = max(0, start - 100)
            end_context = min(len(content), end + 100)

            # 获取前后的内容
            context = content[start_context:end_context]

            # 如果前面的内容不足，尝试从前一个文档获取
            if start_context == 0 and i > 0:
                prev_content = ''.join(documents[i-1]['text'])
                needed = 100 - start  # 计算还需要多少字符
                extended_start = max(0, len(prev_content) - needed)
                context = prev_content[extended_start:] + context

            # 如果后面的内容不足，尝试从后一个文档获取
            if end_context == len(content) and i < len(documents) - 1:
                next_content = ''.join(documents[i+1]['text'])
                needed = 100 - (len(content) - end)  # 计算还需要多少字符
                extended_end = min(len(next_content), needed)
                context += next_content[:extended_end]

            # 将结果添加到列表中
            results.append({
                'page': page,
                'keyword': match.group().replace('\n', '\\n'),
                'content': context
            })

    return results

def extract_location_context(documents, location_suffixes = ["省", "市", "镇", "县", "村", "地点", "地址"]):
    pattern = re.compile('|'.join([f'\\S*{re.escape(suffix)}\\S*' for suffix in location_suffixes]))

    # 存储结果的列表
    results = []

    for i, doc in enumerate(documents):
        # page = doc['page']
        # content = doc['content']
        page = doc['first_index']
        content = '\n'.join(doc['text'])

        # 找到所有关键词的匹配项
        matches = list(pattern.finditer(content))
        for match in matches:
            start, end = match.span()

            # 尝试截取前后100个词的范围
            start_context = max(0, start - 100)
            end_context = min(len(content), end + 100)

            # 获取前后的内容
            context = content[start_context:end_context]

            # 如果前面的内容不足，尝试从前一个文档获取
            if start_context == 0 and i > 0:
                prev_content = ''.join(documents[i-1]['text'])
                needed = 100 - start  # 计算还需要多少字符
                extended_start = max(0, len(prev_content) - needed)
                context = prev_content[extended_start:] + context

            # 如果后面的内容不足，尝试从后一个文档获取
            if end_context == len(content) and i < len(documents) - 1:
                next_content = ''.join(documents[i+1]['text'])
                needed = 100 - (len(content) - end)  # 计算还需要多少字符
                extended_end = min(len(next_content), needed)
                context += next_content[:extended_end]

            # 将结果添加到列表中
            results.append({
                'page': page,
                'keyword': match.group().replace('\n', '\\n'),
                'content': context
            })

    return results




if __name__=='__main__':
    # with open('/home/star/jiamin/bianbiaozhushou/code/data/招标文件-大唐博罗公庄镇 150MW 复合型光伏发电项目/pdf_results.json', 'r', encoding='utf-8') as file:
    #     metadata = json.load(file)
    
    # results = section_retrieve()
    # print(results)

    # keywords = ["地点"]
    
    # results = extract_money_context(metadata)
    # print(results)

    pdf_outpath = "/home/star/jiamin/bianbiaozhushou/core/data/招标文件-大唐博罗公庄镇 150MW 复合型光伏发电项目"

    with open(f"{pdf_outpath}/pdf_results.json", 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    
    all_documents = []
    for dp in metadata:
        all_documents.append(langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]}) )
    
    section_results, page_involved = section_retrieve(["投标办法\n"], all_documents, following=1)

    page_involved_filtered = []
    section_results_filtered = []
    for i in section_results:
        if i.metadata["page"] not in ["封面", "目录", '1', '2', '3']:
            section_results_filtered.append(i.page_content)
            page_involved_filtered.append(i.metadata["page"])

    section_documents = []
    for dp in metadata:
        section_documents.append(langchain_Document(page_content=dp["content"], metadata={"page": dp["page"]}))


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=100,
        length_function=len,
    )
    all_documents_splitted = [
            document
            for data in section_documents
            for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
        ]
    db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)


    _, a = content_retrieve("投标保证金", db_all_documents, 20, None, page_involved)

    rag_results = rerank_content("投标保证金", a, top_n=5)
    print(rag_results)

    # with open('abstract/tender_query.json', 'r', encoding='utf-8') as file:
    #     query_dict = json.load(file)
    
    # element = ""
    # query = query_dict[element]
    # section_results, page_involved = None, []
    # if section_query:=query.get("section_query", False):
    #     section_results, page_involved = section_retrieve(section_query, all_documents)     

    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=500,
    #     chunk_overlap=100,
    #     length_function=len,
    # )
    # all_documents_splitted = [
    #         document
    #         for data in all_documents
    #         for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
    #     ]
    # db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)
    # section_docs, docs_filtered = content_retrieve(query.get('query', element), db_all_documents, 20, section_results, page_involved)

    # if section_docs:
    #     rag_results = rerank_content(query.get('query', element), section_docs, top_n=8)
    # else:
    #     rag_results = rerank_content(query.get('query', element), docs_filtered, top_n=15)
    
    # print([{'page': rr.metadata['page'], 'content': rr.page_content} for rr in rag_results])    




    
    



















    







