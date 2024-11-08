import gradio as gr
import io
import sys
import os
from main import key_element_review, document_element_review
import json

state_file_path = "./state.log"

if os.path.exists(state_file_path):
    os.remove(state_file_path)


def watch_file_and_update():
    try:
        with open(state_file_path, 'r') as file:
            return file.read()
    except:
        return None

def generate_review(tender_file, bid_file):
    if os.path.exists(state_file_path):
        os.remove(state_file_path)

    key_content_review_document = "./关键内容审查.docx"
    tender_response_review_document = "./响应招标文件要求审查.docx"

    types = [
    "项目名称",
    # "项目业主", "标段名称",
    "工期", "质量", "安全", 
    # "文中落款日期"
    ]
    
    outline = {
    "关键内容审查": 
        ["项目名称","工期", "质量", "安全"]
        }

    zhaobiao_metadata, db_toubiao_sections, text_splitter, query_dict = key_element_review(types, tender_file, bid_file, outline=outline)
    yield key_content_review_document, None
    document_element_review(zhaobiao_metadata, db_toubiao_sections, text_splitter, query_dict)
    yield key_content_review_document, tender_response_review_document

    return key_content_review_document, tender_response_review_document


def create_app():
    with gr.Blocks(theme=gr.themes.Monochrome(), title="Aiwaves - BidMaster") as demo:
        gr.Markdown(value="# 智能编标助手 - 内容审查")
        with gr.Row(equal_height=False):
            with gr.Column():
                tender_file = gr.File(file_types=[".docx"], label="请上传「招标」文件", show_label=True, height=50)
                bid_file = gr.File(file_types=[".docx"], label="请上传「投标」文件", show_label=True, height=50)
                with gr.Row():
                    clear_button = gr.ClearButton(components=[tender_file, bid_file], value="清除")
                    submit_button = gr.Button(value="提交")

            state = gr.Textbox(value=watch_file_and_update, label="状态信息", every=1, info="审查进度", lines=9,
                               max_lines=9)
            with gr.Column():
                key_content_review_document = gr.File(label="关键内容审查文件", show_label=True)
                tender_response_review_document = gr.File(label="响应招标文件要求审查文件", show_label=True)

        submit_button.click(fn=generate_review, inputs=[tender_file, bid_file], outputs=[key_content_review_document, tender_response_review_document])

    return demo


if __name__ == "__main__":
    demo = create_app()

    demo.launch(server_port=40072, root_path="https://www.aiwaves.cn/bianbiaozhushou_review/")