import gradio as gr
from main import run_parallel_tasks
import io
import sys
import os

state_file_path = "./state.log"

if os.path.exists(state_file_path):
    os.remove(state_file_path)

def watch_file_and_update():
    try:
        with open(state_file_path, 'r') as file:
            return file.read()
    except:
        return None
    # try:
    #     # 获取文件当前的最后修改时间
    #     current_modified = os.path.getmtime(state_file_path)
        
    #     # 检查文件是否被修改（通过比较最后修改时间）
    #     if current_modified > last_modified:
    #         last_modified = current_modified  # 更新最后修改时间
    #         # 读取并返回文件内容
    #         with open(state_file_path, 'r') as file:
    #             return file.read()
    # except FileNotFoundError:
    #     return None

def generate_digest(docx_file, pdf_file):
    if os.path.exists(state_file_path):
        os.remove(state_file_path)
    types = [
    "项目名称",
      "项目业主",  
    "项目概况",
    "建设地点", "计划工期", "质量标准", "最高投标限价",
      "投标文件递交",
        "招标范围",
    "合同价格", "预付款", "工程进度付款",
      "质量保证金", "竣工结算",
    "最终结清", "增值税专用发票", "支付方式"
]
    
    outline = {
        "一、项目概况与招标范围": {
            "1. 项目概况": ["项目名称", "项目业主", "项目背景","项目概况","其他需重点关注的技术要求",
                "建设地点", "质量标准","最高投标限价","投标文件递交"],
            "2. 招标范围" : ["招标范围"]
        },
        "二、资信及业绩要求": [],
        "三、主要人员资格要求、财务要求、信誉要求": [],
        "四、踏勘现场": [],
        "五、最高投标限价": [],
        "六、评标方法": [],
        "七、合同价格与支付": ["合同价格", "预付款", "工程进度付款", "质量保证金", "竣工结算", "最终结清", "增值税专用发票", "支付方式"],
        "八、罚则": [],
        "九、其他合同条件": [],
        "十、投标报价": []
    }

    digest_file = "./abstract.docx"

    run_parallel_tasks(types=types, doc_path=docx_file, outline=outline, pdf_path=pdf_file)

    return digest_file

def create_app():
    with gr.Blocks(theme="soft", title="Aiwaves - BidMaster") as demo:
        gr.Markdown(value="# 智能编标助手 - 摘要生成")
        with gr.Row(equal_height=False):
            with gr.Column():
                docx_file = gr.File(file_types=[".docx"], label="请上传“docx”格式招标文件", show_label=True, height=50)
                pdf_file = gr.File(file_types=[".pdf"], label="请上传“pdf”格式招标文件", show_label=True, height=50)
                with gr.Row():
                    clear_button = gr.ClearButton(components=[docx_file, pdf_file], value="清除")
                    submit_button = gr.Button(value="提交")

            state = gr.Textbox(value=watch_file_and_update, label="状态信息", every=1, info="摘要生成进度", lines=9, max_lines=9)

            digest_file = gr.File(label="生成的摘要文件", show_label=True)

        submit_button.click(fn=generate_digest, inputs=[docx_file, pdf_file], outputs=[digest_file])

    return demo

if __name__ == "__main__":
    demo = create_app()

    demo.launch(server_port=50026, root_path="https://www.aiwaves.cn/bianbiaozhushou/")