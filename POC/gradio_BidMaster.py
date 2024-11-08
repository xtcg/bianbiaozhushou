import io
import os
import random
import sys
import time
import functools
import gradio as gr

from .RFP_Inspection.main import key_element_review, document_element_review
from .RFP_assistant.main import run_parallel_tasks

state_file_path_abstract = "./state_abstract.log"

if os.path.exists(state_file_path_abstract):
    os.remove(state_file_path_abstract)

state_file_path_review = "./state_review.log"

if os.path.exists(state_file_path_review):
    os.remove(state_file_path_review)


def watch_file_and_update_review():
    try:
        with open(state_file_path_review, 'r') as file:
            return file.read()
    except:
        return None


def watch_file_and_update_abstract():
    try:
        with open(state_file_path_abstract, 'r') as file:
            return file.read()
    except:
        return None


def generate_review(tender_file_path, bid_file_path):
    """
    根据「招标文件」和「投标文件」生成审查文件
    :param tender_file_path: docx 格式的「招标文件」
    :param bid_file_path: docx 格式的「投标文件」
    :return: key_content_review_document, tender_response_review_document: 「关键内容审查」文件和「响应招标文件审查」文件
    """
    if os.path.exists(state_file_path_review):
        os.remove(state_file_path_review)

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
            ["项目名称", "工期", "质量", "安全"]
    }

    zhaobiao_metadata, db_toubiao_sections, text_splitter, query_dict = key_element_review(types, tender_file_path, bid_file_path, outline=outline)
    yield key_content_review_document, None
    document_element_review(zhaobiao_metadata, db_toubiao_sections, text_splitter, query_dict)
    yield key_content_review_document, tender_response_review_document

    return key_content_review_document, tender_response_review_document


def _print():
    for i in range(3):
        time.sleep(1)
        print(f"idx: {i}")


def generate_digest(docx_file_path=None, pdf_file_path=None):
    """
    根据「招标文件」生成「摘要文件」
    :param docx_file_path: docx 格式的「招标文件」
    :param pdf_file_path: pdf 格式的「招标文件」
    :return: digest_file_path:
    """
    if os.path.exists(state_file_path_abstract):
        os.remove(state_file_path_abstract)
    types = [
        "项目名称",
        "项目业主",
        "项目概况",
        "建设地点", "计划工期", "质量标准", "最高投标限价",
        "投标文件递交",
        "招标范围",
        # "合同价格", "预付款", "工程进度付款",
        # "质量保证金", "竣工结算",
        # "最终结清", "增值税专用发票", "支付方式"
    ]

    outline = {
        "一、项目概况与招标范围": {
            "1. 项目概况": ["项目名称", "项目业主", "项目背景", "项目概况", "其他需重点关注的技术要求",
                            "建设地点", "质量标准", "最高投标限价", "投标文件递交"],
            "2. 招标范围": ["招标范围"]
        },
        "二、资信及业绩要求": [],
        "三、主要人员资格要求、财务要求、信誉要求": [],
        "四、踏勘现场": [],
        "五、最高投标限价": [],
        "六、评标方法": [],
        "七、合同价格与支付": [],
        "八、罚则": [],
        "九、其他合同条件": [],
        "十、投标报价": []
    }

    digest_file_path = "./摘要文件.docx"

    run_parallel_tasks(types=types, doc_path=docx_file_path, outline=outline, pdf_path=pdf_file_path, out_path=digest_file_path)

    return digest_file_path


def create_app():
    with gr.Blocks(theme=gr.themes.Monochrome(), title="Aiwaves - BidMaster") as demo:
        with gr.Tab(label="摘要生成"):
            gr.Markdown(value="# 智能编标助手 - 摘要生成")
            with gr.Row(equal_height=False):
                with gr.Column():
                    docx_file = gr.File(file_types=[".docx"], label="请上传「docx」格式招标文件", show_label=True,
                                        height=50)
                    pdf_file = gr.File(file_types=[".pdf"], label="请上传「pdf」格式招标文件", show_label=True, height=50)
                    with gr.Row():
                        gr.ClearButton(components=[docx_file, pdf_file], value="清除")
                        generate_digest_button = gr.Button(value="提交")

                gr.Textbox(value=watch_file_and_update_abstract, label="状态信息", every=1, info="摘要生成进度", lines=9,
                                   max_lines=9)

                digest_file = gr.File(label="生成的摘要文件", show_label=True)

            generate_digest_button.click(fn=generate_digest, inputs=[docx_file, pdf_file], outputs=[digest_file])
        with gr.Tab(label="内容审查"):
            gr.Markdown(value="# 智能编标助手 - 内容审查")
            with gr.Row(equal_height=False):
                with gr.Column():
                    tender_file = gr.File(file_types=[".docx"], label="请上传「招标」文件", show_label=True, height=50)
                    bid_file = gr.File(file_types=[".docx"], label="请上传「投标」文件", show_label=True, height=50)
                    with gr.Row():
                        gr.ClearButton(components=[tender_file, bid_file], value="清除")
                        generate_review_button = gr.Button(value="提交")

                gr.Textbox(value=watch_file_and_update_review, label="状态信息", every=1, info="审查进度", lines=9, max_lines=9)
                with gr.Column():
                    key_content_review_file = gr.File(label="关键内容审查文件", show_label=True)
                    tender_response_review_file = gr.File(label="响应招标文件要求审查文件", show_label=True)

            generate_review_button.click(fn=generate_review, inputs=[tender_file, bid_file],
                                         outputs=[key_content_review_file, tender_response_review_file])

    return demo


if __name__ == "__main__":
    demo = create_app()

    demo.launch(server_port=8080, server_name="0.0.0.0", root_path="https://www.aiwaves.cn/bianbiaozhushou/")
