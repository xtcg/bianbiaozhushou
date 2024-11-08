import argparse
import json
import re
import time
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
import pypdf
import docx
import fitz  # PyMuPDF
import re  # 正则表达式库
from typing import Optional
from docx.opc.pkgreader import _SerializedRelationships, _SerializedRelationship
from docx.opc.oxml import parse_xml
import zipfile
from bs4 import BeautifulSoup


def load_from_xml_v2(baseURI, rels_item_xml):
    """
    Return |_SerializedRelationships| instance loaded with the
    relationships contained in *rels_item_xml*. Returns an empty
    collection if *rels_item_xml* is |None|.
    """
    srels = _SerializedRelationships()
    if rels_item_xml is not None:
        rels_elm = parse_xml(rels_item_xml)
        for rel_elm in rels_elm.Relationship_lst:
            if rel_elm.target_ref in ('../NULL', 'NULL'):
                continue
            srels._srels.append(_SerializedRelationship(baseURI, rel_elm))
    return srels

_SerializedRelationships.load_from_xml = load_from_xml_v2

def print_to_file(message, file_name='./state_review.log'):
    with open(file_name, 'a') as file:
        print(message, file=file)


def get_footer_text(pdf_path, page_number, step=7):
    # 打开PDF文件
    doc = fitz.open(pdf_path)

    # 选择页面（注意：页码从0开始，因此要减1）
    page = doc.load_page(page_number - 1)

    # 初始化页脚高度
    footer_height = 50
    max_footer_height = page.rect.height / 2  # 页脚高度不应超过页面高度的一半

    original_height = page.rect.height
    original_width = page.rect.width

    while footer_height <= max_footer_height:
        # 定义页脚区域
        rect = fitz.Rect(0, original_height - footer_height, original_width, original_height)

        # 裁剪页面到只包含页脚区域
        page.set_cropbox(rect)

        # 提取页脚文本
        footer_text = page.get_text().strip()  # 使用strip()移除前后的空格和换行符
        # 检查footer_text是否符合预期格式：仅数字
        if footer_text.isdigit():
            # 格式正确，返回页脚文本
            doc.close()
            return footer_text
        elif footer_text == "":
            # 如果没有提取到内容，增加footer_height
            footer_height += step
        else:
            # 如果提取到过多内容，减少footer_height
            footer_height -= step

    # 如果没有找到合适的页脚，返回空字符串
    doc.close()
    return ""

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 函数执行耗时 {(end_time - start_time):.4f} 秒。")
        return result

    return wrapper


class StyleAnalyser:
    @staticmethod
    def get_heading_level(para):
        style = para.style
        while isinstance(style, docx.styles.style.ParagraphStyle):
            match = re.search(r'(标题|Heading)\s*(\d+)', style.name, re.IGNORECASE)
            if match:
                return int(match.group(2)) - 1
            style = getattr(style, 'base_style', None)
        return None


class XMLAnalyser:
    @staticmethod
    def get_outline_level(para):
        xml = para._p.xml
        match = re.search('<w:outlineLvl w:val="(\d+)"', xml)
        if match:
            return int(match.group(1))
        return None


def add_section(data, section_hierarchy, section_content, section_text=[], section_tables=[]):
    section_hierarchy_filtered = list(filter(None, section_hierarchy))
    if section_hierarchy_filtered:
        section_data = {
            "section": section_hierarchy_filtered,
            "absolute_page": None,
            "page": None,
            "data": '\n'.join(section_content),
            "text": '\n'.join(section_text),
            "table": section_tables.copy()
        }
        data.append(section_data)

def parse_table(table):
    tbl_content = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            # print(cell.text)
            row_data.append(cell.text.strip())
        tbl_content.append('\t'.join(row_data))
    return '\n'.join(tbl_content)

@timer
def parse_docx(file_path):
    document = docx.Document(file_path)
    
    data = []
    section_hierarchy = [None] * 10
    section_text = []
    section_tables = []
    section_content = []

    for element in document.element.body:
        if isinstance(element, CT_P):
            para = docx.text.paragraph.Paragraph(element, document)
            if para.text:
                heading_level = StyleAnalyser.get_heading_level(para)
                outline_level = XMLAnalyser.get_outline_level(para)
                level = heading_level if heading_level is not None else outline_level

                if level is not None:
                    add_section(data, section_hierarchy, section_content, section_text=section_text, section_tables=section_tables)
                    section_content.clear()
                    section_text.clear()
                    section_tables.clear()
                    section_hierarchy[level] = para.text
                    section_hierarchy[level + 1:] = [None] * (9 - level)
                else:
                    section_text.append(para.text)
                    section_content.append(para.text)
        elif isinstance(element, CT_Tbl):
            table = docx.table.Table(element, document)
            table_text = parse_table(table)
            section_content.append(f'\n{table_text}\n')
            section_tables.append(table_text)

    add_section(data, section_hierarchy, section_content, section_text=section_text, section_tables=section_tables)
    return data


@timer
def preprocess_pdf(pdf_path):
    text_by_page = []
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            text_by_page.append(text)
    return text_by_page


def generate_regex_pattern(text):
    punctuation = r'[.,;:!?]'
    parts = re.split(f'({punctuation}|\s+|\d+|[a-zA-Z]+|[^a-zA-Z\d\s]+)', text)
    escaped_parts = [(r'\s*' if part.isspace() else re.escape(part)) for part in parts if part]
    pattern = r'\s*'.join(escaped_parts)
    return pattern


def find_text(text_by_page, search_text, start_page=1):
    start_index = max(start_page - 1, 0)
    pattern = generate_regex_pattern(search_text)
    compiled_pattern = re.compile(pattern)
    for i, page_text in enumerate(text_by_page[start_index:], start=start_index):
        if compiled_pattern.search(page_text):
            return i + 1
    return None


def find_first_page(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        outlines = reader.outline

        if outlines:
            first_outline = outlines[0]  # Assuming the first outline is the first chapter
            page_number = reader.get_destination_page_number(first_outline)
            return page_number

    return None


@timer
def preprocess(docx_path: str, pdf_path: Optional[str] = None, search_limit=10, skip_scale=3):
    # if not pdf_path:
    #     # 如果没有提供PDF路径，假设PDF文件与DOCX文件在同一目录，仅扩展名不同
    #     pdf_path = docx_path.replace('.docx', '.pdf')
    # start_page = find_first_page(pdf_path) or skip_scale
    print_to_file("开始解析docx文件...")
    data = parse_docx(docx_path)
    print_to_file("docx文件解析完成！")
    print('docx_path', docx_path)
    # print_to_file("开始预处理PDF文件...")
    # text_by_page = preprocess_pdf(pdf_path)
    # print_to_file("PDF文件预处理完成！")

    print_to_file("开始解析内容参考信息...")
    # for d in data[1:]:
        # d['absolute_page'] = find_text(text_by_page, f'{d["text"][:search_limit]}', start_page=start_page)
        # d['absolute_page'] = find_text(text_by_page, f'{d["section"][-1]}\n', start_page=start_page)
        # if d['absolute_page'] is None:
        #     print(f'============================')
        #     print(f'can not find section {d["section"][-1]}')
        #     #print(f'{d["data"]}')
        #     print(f'============================')
        #     continue

        # start_page = d['absolute_page']
        # d['page'] = int(get_footer_text(pdf_path, d['absolute_page'], step=7))
    print_to_file("参考信息解析完成！")

    metadata_path = docx_path.replace('.docx', '.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return metadata_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a .docx file and output data to a .json file.")
    parser.add_argument("--docx", help="The .docx file to process")
    args = parser.parse_args()
    preprocess(args.docx)
