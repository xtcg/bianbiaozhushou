from core.rapidocr_paddle import LoadImageError, RapidOCR
import os
import fitz
import re
import json
import concurrent.futures
from .utils import timer


def extract_text_from_page(page, engine, scale=1.0):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    img_path = f"temp_page_{page.number}.png"
    pix.save(img_path)
    print(f"temp_page_{page.number}.png size: {pix.width} x {pix.height} pixels")

    text_instances, _ = engine(img_path)

    os.remove(img_path)

    text = "\n".join([text_instance[1].strip() for text_instance in text_instances])

    return text


def parse_toc(content):
    """
    解析一段文字中的章节信息
    """
    toc_entries = []
    lines = content.split("\n")
    current_section = None

    section_pattern = re.compile(
        r"^(?:^\d{1,2}\.\s*[\u4e00-\u9fff].*|第[一二三四五六七八九十]{1,2}[卷章节部分]{1,2}.*)"
    )
    page_pattern = re.compile(r"(\d+)\s*$")

    for line in lines:
        line = line.strip()
        cleaned_line = re.sub(r"[\.。．:：…·\-∙,，、——\*\^]*$", "", line).strip()
        if section_pattern.match(cleaned_line):
            current_section = cleaned_line
            toc_entries.append({"section": current_section, "absolute_page": None})
        elif current_section:
            page_match = page_pattern.search(cleaned_line)
            if page_match:
                page_number = int(page_match.group(1))

                toc_entries[-1]["absolute_page"] = page_number

    section_pattern = re.compile(
        r"^(?:^\d{1,2}\.\s*[\u4e00-\u9fff].*|第[一二三四五六七八九十]{1,2}[卷章节部分]{1,2}.*)"
    )

    first_valid_index = None
    for index, entry in enumerate(toc_entries):
        if section_pattern.match(entry["section"]):
            first_valid_index = index
            break

    if first_valid_index is not None:
        toc_entries = toc_entries[first_valid_index:]

    return toc_entries


def create_flexible_pattern(title):

    char_mapping = {
        "（": "(",
        "）": ")",
        "．": ".",
        "，": ",",
        "！": "!",
        "？": "?",
        "：": ":",
        "；": ";",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
    reversed_mapping = {v: k for k, v in char_mapping.items()}

    title = title.replace(" ", "")
    mapped_title = []
    for char in title:
        if char in char_mapping:

            mapped_char = f"[{re.escape(char)}{re.escape(char_mapping[char])}]"
        elif char in reversed_mapping:
            mapped_char = f"[{re.escape(char)}{re.escape(reversed_mapping[char])}]"
        else:
            mapped_char = re.escape(char)
        mapped_title.append(mapped_char)

    flexible_pattern = "\s*".join(mapped_title)

    return re.compile(
        f"^\s*{flexible_pattern}\s*$", re.IGNORECASE | re.MULTILINE | re.DOTALL
    )


def find_toc_end(doc, first_section_title):
    toc_start_page = 1
    toc_end_page = toc_start_page
    first_section_pattern = create_flexible_pattern(first_section_title)

    for i in range(toc_start_page + 1, len(doc)):
        page = doc.load_page(i)
        text = page.get_text()
        match = first_section_pattern.search(text)

        if match:
            print(f"匹配到第一章标题在第 {i+1} 页: {repr(match.group())}")
            toc_end_page = i - 1
            break

    return toc_end_page


def extract_toc(pdf_path):
    doc = fitz.open(pdf_path)
    toc_entries = []
    first_section_title = None
    engine = RapidOCR()

    text = extract_text_from_page(page=doc.load_page(1), engine=engine)
    toc_entries.extend(parse_toc(text))
    first_section_title = toc_entries[0]["section"]

    toc_end_page = find_toc_end(pdf_path, first_section_title=first_section_title)

    for page_idx in range(2, toc_end_page + 1):
        text = extract_text_from_page(page=doc.load_page(page_idx), engine=engine)
        toc_entries.extend(parse_toc(text))

    return toc_entries


def extract_section_content(pdf_path, sections, start_page):
    doc = fitz.open(pdf_path)
    engine = RapidOCR()

    for section in sections:
        section["data"] = ""
        section["absolute_page"] = None
        section["pattern"] = create_flexible_pattern(section["section"])

    current_section = None
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_page = {executor.submit(extract_text_from_page, page, engine): page for page in doc[start_page:]}

        page_texts = []
        for future in concurrent.futures.as_completed(future_to_page):
            page_texts.append(future.result())

    for page_number, page_text in enumerate(page_texts, start=start_page):
        for section in sections:
            if section["pattern"].search(page_text):
                if current_section and current_section["absolute_page"] is not None:
                    current_section["data"] = current_section["data"].strip()

                current_section = section
                current_section["absolute_page"] = page_number + 1

        if current_section:
            current_section["data"] += page_text + "\n"

    if current_section and current_section["absolute_page"] is not None:
        current_section["data"] = current_section["data"].strip()

    return sections


def get_footer_text(pdf_path, page_number, step=7):
    doc = fitz.open(pdf_path)

    page = doc.load_page(page_number - 1)

    footer_height = 50
    max_footer_height = page.rect.height / 2

    original_height = page.rect.height
    original_width = page.rect.width

    while footer_height <= max_footer_height:
        rect = fitz.Rect(
            0, original_height - footer_height, original_width, original_height
        )

        page.set_cropbox(rect)

        match = re.search(r"\d+", page.get_text().strip())
        footer_text = match.group() if match else ""

        if footer_text.isdigit():
            doc.close()
            return footer_text
        elif footer_text == "":

            footer_height += step
        else:
            footer_height -= step

    doc.close()
    return ""


def parse_pdf(pdf_path):
    toc = extract_toc(pdf_path)
    sections = extract_section_content(
        pdf_path, toc, find_toc_end(pdf_path, first_section_title=toc[0]["section"]) + 1
    )
    for sec in sections:
        if "pattern" in sec:
            del sec["pattern"]
        if sec["absolute_page"]:
            sec["page"] = int(get_footer_text(pdf_path, sec["absolute_page"], step=7))
        else:
            print(json.dumps(sec, ensure_ascii=False, indent=4))

    return sections

def extract_message_per_page(page, engine, out_path, scale=1.0):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale))
    img_path = f"{out_path}/temp_page_{page.number}.png"
    pix.save(img_path)
    print(f"temp_page_{page.number}.png size: {pix.width} x {pix.height} pixels")

    text_instances, _ = engine(img_path)
    page_dict = {"page": "", "content": ""}
    if text_instances:
        if text_instances[-1][1].strip().isdigit():
            page_dict["page"] = text_instances[-1][1].strip()
            page_dict["content"] = "\n".join([text_instance[1].strip() for text_instance in text_instances[:-1]])
        elif match:=re.search(r'第(\d+)页共\d+页', text_instances[-1][1].strip()):
            page_dict["page"] = match.group(1)
            page_dict["content"] = "\n".join([text_instance[1].strip() for text_instance in text_instances[:-1]])
        elif match:=re.search(r'第(\d+)页共\d+', text_instances[-1][1].strip()):
            page_dict["page"] = match.group(1)
            page_dict["content"] = "\n".join([text_instance[1].strip() for text_instance in text_instances[:-1]])
        else:
            page_dict["content"] = "\n".join([text_instance[1].strip() for text_instance in text_instances])

    return page_dict

def correct_page_number(lst, repair_number=5):
    # 找到第一个有效的数字段
    valid_segment_found = False
    start_index = None
    count = 0
    valid_start = None

    # 遍历列表查找连续整数
    for i in range(len(lst)):
        if lst[i].isdigit():
            if start_index is None:
                start_index = i
                valid_start = int(lst[i])
                count = 1
            elif int(lst[i]) == int(lst[i - 1]) + 1:
                count += 1
            else:
                start_index = i
                valid_start = int(lst[i])
                count = 1
        else:
            start_index = None
            count = 0

        # 检查是否已经有足够的连续数字
        if count >= repair_number:
            valid_segment_found = True
            break

    if valid_segment_found:  
        first_int_index = start_index + 1 - valid_start  # 回溯到1的位置
        prefix = ['封面'] + ['目录'] * (first_int_index-1)
        corrected_list = prefix + list(range(1, 1 + len(lst) - first_int_index))
        return corrected_list
    else:
        return lst

@timer
def parse_pdf_with_pages(pdf_path, file_hash=None):
    if file_hash is not None:
        file_path = file_hash
    else:
        file_path = './data/'+pdf_path.split('/', -1)[-1].replace('.pdf', "").strip()
    if not os.path.exists(file_path):
        os.makedirs(file_path)  # 使用makedirs创建文件夹，包括所有必要的中间文件夹
    
    if not os.path.exists(f"{file_path}/pdf_results.json"):
        toc_entries = []
        doc = fitz.open(pdf_path)
        engine = RapidOCR(det_use_cuda=True, cls_use_cuda=True, rec_use_cuda=True)

        page_texts = [None]*len(doc)
        toc_end_page = 0
        for i in range(toc_end_page, len(doc)):
            page_texts[i] = extract_message_per_page(doc[i], engine, file_path)
        
        # find_start_page = False
        # for page_id in range(int(len(doc)*0.2)):
        #     if not find_start_page:
        #         text = extract_text_from_page(doc[page_id], engine=engine)
        #         if ("目录" in text) or ("目\n录" in text):
        #             find_start_page = True
        #             start_page = page_id
        #             text = extract_text_from_page(page=doc.load_page(start_page), engine=engine)
        #             toc_entries.extend(parse_toc(text))
        #             first_section_title = toc_entries[0]["section"]
        #             toc_end_page = find_toc_end(doc, first_section_title=first_section_title)
        #         else:
        #             page_texts[page_id] = {"page": "封面", "content": text}
        #     else:
        #         break

        # with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        #     future_to_page = {executor.submit(extract_message_per_page, doc[i], engine, file_path): i for i in range(toc_end_page, len(doc))} 
        #     for future in concurrent.futures.as_completed(future_to_page):
        #                 index = future_to_page[future]
        #                 page_texts[index] = future.result()
        
        
        page_list = [p["page"] for p in page_texts]
        corrected_page_list = correct_page_number(page_list)
        filtered_pages = [{"page": str(corrected_page_list[j]), "content": page_texts[j]["content"]} for j in range(len(page_texts))]
        with open(f"{file_path}/pdf_results.json", "w") as f:
            json.dump(filtered_pages, f, ensure_ascii=False, indent=4)
    
    return file_path


if __name__ == "__main__":
    pdf_path = "/home/star/jiamin/bianbiaozhushou/test_cases/bid-tender/【已脱敏】青青草原(招标文件).pdf"
    sections = parse_pdf_with_pages(pdf_path=pdf_path)

    # with open("result_parse.json", "w") as f:
    #     f.write(json.dumps(sections, ensure_ascii=False, indent=4))