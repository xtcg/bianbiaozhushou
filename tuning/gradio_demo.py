import json
import hashlib
import os
import sys
import traceback
import shutil
from pathlib import Path
from openai import OpenAI
import gradio as gr
from langchain_core.documents import Document as LangchainDocument
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.docx_parse import Docx
from core.retrieval import (
    JinaEmbeddings, section_retrieve, rerank_content, content_retrieve,
    extract_dates_with_context, extract_keyword_content, extract_location_context, extract_money_context
)

from core.pdf_parser import parse_pdf_with_pages
api_key = "EMPTY"
api_base =  "http://172.19.0.1:40079/v1"
client = OpenAI(api_key=api_key, base_url=api_base)
# def parse_pdf_with_pages():
#     pass


with open('core/abstract/prompt.json', 'r', encoding='utf-8') as f:
    prompt_abs = json.load(f)
CHECKPOINTS = list(prompt_abs.keys())

with open('core/review/prompt.json', 'r', encoding='utf-8') as f:
    prompt_rev = json.load(f)
INSPECTPOINTS = list(prompt_rev.keys())


def obtain_binary_id(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_content_check(inspect_point):
    with open(f'core/review/bid_query.json', 'r', encoding='utf-8') as f:
        query_check = json.load(f)
    inspect_point_query = query_check[inspect_point]

    section_query = inspect_point_query.get("bid_section_query", "")
    content_query = inspect_point_query.get("bid_query", "")
    if inspect_point_query.get("location", False):
        keywords = inspect_point_query["location"]
    elif inspect_point_query.get("money", False):
        keywords = inspect_point_query["money"]
    elif inspect_point_query.get("date", False):
        keywords = inspect_point_query["date"]
    else:
        keywords = inspect_point_query.get("keywords", "")

    with open(f'core/review/prompt.json', 'r', encoding='utf-8') as f:
        prompt = json.load(f)
    return section_query, content_query, keywords, prompt[inspect_point]["sysprompt"], prompt[inspect_point][
        "userprompt"]


def load_content(check_point):
    with open(f'core/abstract/tender_query.json', 'r', encoding='utf-8') as f:
        query_abs = json.load(f)
    check_point_query = query_abs[check_point]
    if check := check_point_query.get("query_need", False):
        check_point_query = query_abs[check]
    else:
        section_query = check_point_query.get('section_query', '封面')
        content_query = check_point_query.get('query', check_point)

    check_point_prompt = prompt_abs[check_point]
    with open(f'core/abstract/prompt_check.json', 'r', encoding='utf-8') as f:
        prompt_check = json.load(f)
    return section_query, content_query, check_point_prompt["sysprompt"], check_point_prompt["userprompt"], \
        prompt_check["system"], prompt_check["user"]


def preview_content(filename, page=None, search_query=None):
    file_path = f'tuning/files/{filename}'
    hashid = obtain_binary_id(file_path)
    cache_path = Path(f'cache/{hashid}/')
    if not cache_path.joinpath('pdf_results.json').exists():
        _ = parse_pdf_with_pages(file_path, cache_path)

    with open(cache_path.joinpath('pdf_results.json'), 'r', encoding='utf-8') as f:
        fullcontents = json.load(f)
    if page:
        page_content = fullcontents[int(page)]
        return page_content["content"]
    elif search_query:
        search_res = []
        for i in fullcontents:
            if search_query.strip() in i["content"].strip():
                search_res.append(i["content"])
        return '\n---------------------page--break----------------------\n'.join(search_res)
    else:
        return ""


def rag_content(filename, check_point, content_query):
    file_path = f'tuning/files/{filename}'
    hashid = obtain_binary_id(file_path)
    cache_path = Path(f'cache/{hashid}/')
    if not cache_path.joinpath('pdf_results.json').exists():
        _ = parse_pdf_with_pages(file_path, cache_path)
    with open(f'cache/{hashid}/pdf_results.json', 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    doc = Docx(file_path=file_path,use_cache=True)
    doc.set_cached_dir(cache_path)
    metadata1 = doc.get_rag()
    all_documents = []
    all_doc = ''
    for dp in metadata1:
        cur = '\n'.join(dp['text'])
        if dp['type'] == '目录':continue
        all_doc += cur + '\n'
        for line, index in zip(dp['text'], dp['index']):
            all_documents.append(LangchainDocument(page_content=line, metadata={"page": index}))
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=128,
        chunk_overlap=64,
        length_function=len,
    )
    all_documents_splitted = [
        document
        for data in all_documents
        for document in text_splitter.create_documents([data.page_content], [{'page': data.metadata['page']}])
    ]
    db_all_documents = FAISS.from_documents(documents=all_documents_splitted, embedding=JinaEmbeddings)
    with open(f'core/abstract/tender_query.json', 'r', encoding='utf-8') as f:
        query_check = json.load(f)
    query = query_check[check_point]
    section_results, page_involved = None, []
    if section_query:=query.get("section_query", False):
        section_results, page_involved = section_retrieve(section_query, all_documents, doc.rag1)
    section_docs, docs_filtered = content_retrieve(query, db_all_documents, 20, section_results, page_involved)

    if section_docs:
            try:
                docs = rerank_content(query.get('query', check_point), docs_filtered, top_n=8)
                rag_results = section_docs + docs
            except:
                print(check_point)
    else:
        global_related = []
        global_retriever = db_all_documents.as_retriever(search_kwargs={'k': 8})
        global_related = global_retriever.invoke(query.get('query','.'))
        reranked_content = rerank_content(query.get('query', check_point), global_related, top_n=15)

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
    res = []
    for l,r,page in mem:
        res.append({'content': all_doc[l:r]})
    if query.get("use_front_page", False):
        res = [{ 'content': '\n'.join(metadata[0]['text'])}] + res
    return json.dumps(res, ensure_ascii=False, indent=4)


def rag_content_check(filename, section_query, content_query, keywords, inspect_point):
    section_query = eval(section_query) if section_query else section_query
    keywords = eval(keywords) if keywords else keywords
    file_path = f'tuning/files/{filename}'
    hashid = obtain_binary_id(file_path)
    cache_path = Path(f'cache/{hashid}/')
    if not cache_path.joinpath('pdf_results.json').exists():
        _ = parse_pdf_with_pages(file_path, cache_path)
    with open(f'cache/{hashid}/pdf_results.json', 'r', encoding='utf-8') as f:
        bid_metadata = json.load(f)
    bid = Docx(file_path)
    metadata = bid.get_rag()
    all_bid_documents = []
    for dp in metadata:
        cur = '\n'.join(dp['text'])
        if dp['type'] == '目录' :continue
        all_bid_documents.append(LangchainDocument(page_content=cur, metadata={"page": dp["first_index"], 'raw': dp['text']}))

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

    with open(f'core/review/bid_query.json', 'r', encoding='utf-8') as f:
        query_check = json.load(f)
    element_query = query_check[inspect_point]
    if element_query.get("location", False):
        bid_info = extract_location_context(metadata, keywords)
    elif element_query.get("money", False):
        bid_info = extract_money_context(metadata, keywords)
    elif element_query.get("date", False):
        bid_info = extract_dates_with_context(metadata, keywords)
    elif keywords := element_query.get("keywords", False):
        bid_info = extract_keyword_content(metadata, keywords)
    else:
        section_results, page_involved = section_retrieve(element_query.get("bid_section_query", [inspect_point]), all_bid_documents, bid.rag1)

        section_docs, docs_filtered = content_retrieve(
            content_query, db_all_documents, 20, section_results, page_involved
        )

        if section_docs:
            bid_info = rerank_content(content_query, section_docs, top_n=8)
        else:
            bid_info = rerank_content(content_query, docs_filtered, top_n=15)

        bid_info = [{'content': rr.page_content} for rr in bid_info]

    return json.dumps(bid_info, ensure_ascii=False, indent=4)


def generate_first_step(rag_results, system_prompt, user_prompt):
    message = [
        {"role": "system", "content": system_prompt.format(info=rag_results)[:4500]},
        {"role": "user", "content": user_prompt}
    ]
    print(message)
    print('a')
    model = 'qwen72b-chat-int4'
    # return 'a'
    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=3000,
            temperature=0.8,
            top_p=1,
            stop=["<|im_end|>", "<|endoftext|>", "<|im_start|>"]
        )

        response = ""
        for chunk in stream:
            if not chunk.choices:
                continue
            chunk_response = chunk.choices[0].delta.content
            if chunk_response:
                response += chunk_response
            yield response
        return response

    except Exception as e:
        print(traceback.format_exc())
        raise


def generate_check_step(response, system_prompt, user_prompt):
    message = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt.format(response=response)}
    ]
    model = 'qwen72b-chat-int4'

    stream = client.chat.completions.create(
        model=model, messages=message,
        stream=True,
        max_tokens=3000,
        temperature=0.8,
        top_p=1,
        stop=["<|im_end|>", "<|endoftext|>", "<|im_start|>"]
    )

    response2 = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        chunk_response = chunk.choices[0].delta.content
        if chunk_response:
            response2 += chunk_response
        yield response2
    return response2


def generate_content_check(bid_info, tender_info, system_prompt, user_prompt):
    if tender_info:
        message = [
            {"role": "system", "content": system_prompt.format(bid_info=bid_info)[:2000]},
            {"role": "user", "content": user_prompt.format(tender_info=tender_info)}
        ]
    else:
        message = [
            {"role": "system", "content": system_prompt.format(info=bid_info)[:4500]},
            {"role": "user", "content": user_prompt}
        ]
    print(message)
    model = 'qwen72b-chat-int4'
    return 'a'
    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=3000,
            temperature=0.8,
            top_p=1,
            stop=["<|im_end|>", "<|endoftext|>", "<|im_start|>"]
        )

        response = ""
        for chunk in stream:
            if not chunk.choices:
                continue
            chunk_response = chunk.choices[0].delta.content
            if chunk_response:
                response += chunk_response
            yield response
        return response

    except Exception as e:
        print(traceback.format_exc())
        raise


def save_current_results(sysprompt1, userprompt1, sysprompt2, userprompt2, section_query, content_query, check_point):
    # query_path = "core/abstract/tender_query.json"
    # with open(query_path, 'r', encoding='utf-8') as f:
    #     full_query = json.load(f)
    # full_query[check_point]["section_query"] = eval(section_query)
    # if content_query != check_point:
    #     full_query[check_point]["query"] = content_query
    # with open(query_path, 'w') as f:
    #     json.dump(full_query, f, ensure_ascii=False, indent=4)

    prompt_path = "core/abstract/prompt.json"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        full_prompts = json.load(f)
    full_prompts[check_point]["sysprompt"] = sysprompt1
    full_prompts[check_point]["userprompt"] = userprompt1
    with open(prompt_path, 'w') as f:
        json.dump(full_prompts, f, ensure_ascii=False, indent=4)

    prompt_check_path = "core/abstract/prompt_check.json"
    with open(prompt_check_path, 'r', encoding='utf-8') as f:
        check_prompt = json.load(f)
    change = 0
    if check_prompt["system"] != sysprompt2:
        check_prompt["system"] = sysprompt2
        print("Check sysprompt changed !")
        change += 1
    if check_prompt["user"] != userprompt2:
        check_prompt["user"] = userprompt2
        print("Check userprompt changed !")
        change += 1
    if change:
        with open(prompt_check_path, 'w') as f:
            json.dump(check_prompt, f, ensure_ascii=False, indent=4)
    gr.Info("Changes Saved !")


def save_current_results_check(sysprompt, userprompt, section_query, content_query, keywords, inspect_point):
    query_path = "core/review/bid_query.json"
    with open(query_path, 'r', encoding='utf-8') as f:
        full_query = json.load(f)

    element_query = full_query[inspect_point]
    if element_query.get("location", False):
        full_query[inspect_point]["location"] = keywords
    elif element_query.get("money", False):
        full_query[inspect_point]["money"] = keywords
    elif element_query.get("date", False):
        full_query[inspect_point]["date"] = keywords
    elif element_query.get("keywords", False):
        full_query[inspect_point]["keywords"] = eval(keywords)
    else:
        full_query[inspect_point]["bid_section_query"] = eval(section_query)
        full_query[inspect_point]["bid_query"] = content_query
    with open(query_path, 'w') as f:
        json.dump(full_query, f, ensure_ascii=False, indent=4)

    prompt_path = "core/review/prompt.json"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        full_prompts = json.load(f)
    full_prompts[inspect_point]["sysprompt"] = sysprompt
    full_prompts[inspect_point]["userprompt"] = userprompt
    with open(prompt_path, 'w') as f:
        json.dump(full_prompts, f, ensure_ascii=False, indent=4)

    gr.Info("Changes Saved !")

def save_uploaded_file(file):
    # 目标文件路径，可以根据需要修改
    save_path = f"tuning/files/{file.name.split('/')[-1]}"
    print(file)
    print(save_path)
    # 将上传的文件保存到指定路径
    with open(file.name,'rb') as file:
        with open(save_path, "wb") as out_file:
        # shutil.copyfileobj(file, out_file)
            out_file.write(file.read())

    return f"{file} 上传成功", gr.update(choices = [p for p in os.listdir('tuning/files/') if p.endswith('.docx')]), gr.update(choices = [p for p in os.listdir('tuning/files/') if p.endswith('.docx')]), gr.update(choices = [p for p in os.listdir('tuning/files/') if p.endswith('.docx')])

def delete_selected_file(file):
    # 目标文件路径，可以根据需要修改
    file_path = f"tuning/files/{file}"
    # print(file)
    # print(save_path)
    # 将上传的文件保存到指定路径
    if os.path.isfile(file_path):
        os.remove(file_path)

    return f"{file} 已删除", gr.update(choices = [p for p in os.listdir('tuning/files/') if p.endswith('.docx')]), gr.update(choices = [p for p in os.listdir('tuning/files/') if p.endswith('.docx')]), gr.update(choices = [p for p in os.listdir('tuning/files/') if p.endswith('.docx')])


def create_app():
    file_list = [p for p in os.listdir('tuning/files/') if p.endswith('.docx')]    
    with gr.Blocks(theme=gr.themes.Monochrome(), title="demo") as demo:
        with gr.Tab(label = '上传文件'):
            gr.Markdown(value="# 上传文件")
            with gr.Column():
                docx_file = gr.File(file_types=[".docx"], label="请上传「docx」格式招标文件", show_label=True, 
                                    height=150)
                button_1 = gr.Button(value='upload')
                html = gr.Textbox(value= '',label="文件处理状态")
                file_delete = gr.Dropdown(choices=file_list, label="调试文件列表", allow_custom_value=True)
                button_2 = gr.Button(value='delete')
        
        with gr.Tab(label="摘要检索"):

            gr.Markdown(value="# 智能编标助手 - 摘要检索")
            with gr.Row(equal_height=False):
                with gr.Column():
                    filename = gr.Dropdown(choices=file_list, label="调试文件列表", allow_custom_value=True)
                    with gr.Row():
                        page = gr.Textbox(lines=1, placeholder="绝对页码 首页为0", label="页码", interactive=True)
                        search_query = gr.Textbox(
                            lines=1, placeholder="根据关键词查找解析内容", label="关键词", interactive=True
                        )
                    look_button = gr.Button(value='查看')
                    content_page = gr.Textbox(placeholder="页码内容", label="对应页码解析内容")
                    
                with gr.Column():
                    check_point = gr.Dropdown(choices=CHECKPOINTS, label="摘要点")
                    load_button = gr.Button(value='加载')
                    rag_section_query = gr.Textbox(placeholder="章节索引", label="章节索引", interactive=True)
                    rag_content_query = gr.Textbox(placeholder="内容索引", label="内容索引", interactive=True)
                    rag_button = gr.Button(value='检索')
                    rag_results = gr.Textbox(placeholder="RAG结果", label="RAG结果")
        
        with gr.Tab(label="摘要生成"):
            gr.Markdown(value="# 智能编标助手 - 摘要生成")
            with gr.Row(equal_height=False):
                with gr.Column():
                    sys_prompt1 = gr.Textbox(
                        placeholder="System Prompt 1", label="System Prompt 1", interactive=True, lines=10
                    )
                    user_prompt1 = gr.Textbox(
                        placeholder="User Prompt 1", label="User Prompt 1", interactive=True, lines=10
                    )
                    generation_button_1 = gr.Button(value='测试')
                    generation_results = gr.Textbox(placeholder="初步生成结果", lines=5, label="Response 1")

                with gr.Column():
                    sys_prompt2 = gr.Textbox(
                        placeholder="System Prompt 2", label="System Prompt 2", interactive=True, lines=10
                    )
                    user_prompt2 = gr.Textbox(
                        placeholder="User Prompt 2", label="User Prompt 2", interactive=True, lines=10
                    )
                    generation_button_2 = gr.Button(value='测试')
                    final_generation_results = gr.Textbox(placeholder="最终生成结果", label="Response 2", lines=5)

            with gr.Row():
                submit_button = gr.Button(value='提交修改')
                clear_button = gr.Button(value='清除')

        
        load_button.click(
            fn=load_content, inputs=[check_point],
            outputs=[rag_section_query, rag_content_query, sys_prompt1, user_prompt1, sys_prompt2, user_prompt2]
        )
        look_button.click(fn=preview_content, inputs=[filename, page, search_query], outputs=[content_page])
        rag_button.click(fn=rag_content, inputs=[filename, check_point, rag_content_query], outputs=[rag_results])
        generation_button_1.click(
            fn=generate_first_step, inputs=[rag_results, sys_prompt1, user_prompt1], outputs=[generation_results]
        )
        generation_button_2.click(
            fn=generate_check_step, inputs=[generation_results, sys_prompt2, user_prompt2],
            outputs=[final_generation_results]
        )
        clear_button.click(
            fn=lambda: (None, None, None, None, None, None, None, None, None, None, None, None, None, None),
            outputs=[filename, page, search_query, check_point, content_page, rag_content_query, rag_section_query,
                     rag_results, sys_prompt1, user_prompt1, sys_prompt2, user_prompt2, generation_results,
                     final_generation_results]
        )
        submit_button.click(
            fn=save_current_results, inputs=[sys_prompt1, user_prompt1, sys_prompt2, user_prompt2, rag_section_query,
                                             rag_content_query, check_point]
        )

        with gr.Tab(label="审查内容检索"):
            gr.Markdown(value="# 智能编标助手 - 审查内容检索")
            with gr.Row(equal_height=False):
                with gr.Column():
                    filename2 = gr.Dropdown(choices=file_list, label="调试文件列表")
                    with gr.Row():
                        page2 = gr.Textbox(lines=1, placeholder="绝对页码 首页为0", label="页码", interactive=True)
                        search_query2 = gr.Textbox(
                            lines=1, placeholder="根据关键词查找解析内容", label="关键词", interactive=True
                        )
                    look_button2 = gr.Button(value='查看')
                    content_page2 = gr.Textbox(placeholder="页码内容", label="对应页码解析内容")

                with gr.Column():
                    inspect_point = gr.Dropdown(choices=INSPECTPOINTS, label="审查点")
                    load_button2 = gr.Button(value='加载')
                    rag_section_query2 = gr.Textbox(placeholder="章节索引", label="章节索引", interactive=True)
                    rag_content_query2 = gr.Textbox(placeholder="内容索引", label="内容索引", interactive=True)
                    rag_keywords2 = gr.Textbox(placeholder="关键词", label="关键词", interactive=True)
                    rag_button2 = gr.Button(value='检索')
                    rag_results2 = gr.Textbox(placeholder="RAG结果", label="RAG结果", lines=4)

        with gr.Tab(label="审查结论生成"):
            gr.Markdown(value="# 智能编标助手 - 审查结论生成")
            with gr.Row(equal_height=False):
                with gr.Column():
                    tender_conclusion = gr.Textbox(placeholder="招标文件内容", label="招标文件内容", lines=2)
                    sys_prompt12 = gr.Textbox(
                        placeholder="System Prompt", label="System Prompt", interactive=True, lines=10
                    )
                    user_prompt12 = gr.Textbox(
                        placeholder="User Prompt", label="User Prompt", interactive=True, lines=10
                    )
                    generation_button_12 = gr.Button(value='测试')
                    generation_results2 = gr.Textbox(placeholder="生成结果", lines=5, label="Response")

            with gr.Row():
                submit_button2 = gr.Button(value='提交修改')
                clear_button2 = gr.Button(value='清除')
        button_1.click(fn = save_uploaded_file, inputs=[docx_file], outputs=[html, filename, filename2, file_delete])
        button_2.click(fn = delete_selected_file, inputs=[file_delete], outputs=[html, filename, filename2, file_delete])
        look_button2.click(fn=preview_content, inputs=[filename2, page2, search_query2], outputs=[content_page2])
        clear_button2.click(
            fn=lambda: (None, None, None, None, None, None, None, None, None, None, None, None, None),
            outputs=[filename2, page2, search_query2, inspect_point, tender_conclusion, content_page2,
                     rag_content_query2, rag_section_query2, rag_keywords2, rag_results2, sys_prompt12, user_prompt12,
                     generation_results2]
        )
        load_button2.click(
            fn=load_content_check, inputs=[inspect_point],
            outputs=[rag_section_query2, rag_content_query2, rag_keywords2, sys_prompt12, user_prompt12]
        )
        rag_button2.click(
            fn=rag_content_check,
            inputs=[filename2, rag_section_query2, rag_content_query2, rag_keywords2, inspect_point],
            outputs=[rag_results2]
        )
        generation_button_12.click(
            fn=generate_content_check, inputs=[rag_results2, tender_conclusion, sys_prompt12, user_prompt12],
            outputs=[generation_results2]
        )
        submit_button2.click(
            fn=save_current_results_check,
            inputs=[sys_prompt12, user_prompt12, rag_section_query2, rag_content_query2, rag_keywords2, inspect_point]
        )

    return demo


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    demo = create_app()
    # gr.close_all()
    demo.queue(max_size=20).launch(max_threads=5,server_port=8080, server_name="0.0.0.0", root_path="/bianbiaozhushou")