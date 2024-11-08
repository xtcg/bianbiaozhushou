import functools
import time
import re

from asgi_correlation_id import correlation_id


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} 函数执行耗时 {(end_time - start_time):.4f} 秒。")
        return result

    return wrapper


def parse_eval_content(multiline_text: str):
    # Regex pattern to match multiple page-content pairs
    pattern = r"point:\s*(?P<point>.+?)\s*requirement:\s*(?P<requirement>.+?)\s*(?=point:|$)"
    matches = re.finditer(pattern, multiline_text, re.DOTALL)

    # Dictionary to collect content based on page
    content_dict = {}
    for match in matches:
        point = match.group('point').strip()
        requirement = match.group('requirement').strip()
        content_dict[point] = {"tender_info": requirement}

    return content_dict


def parse_and_combine_content(multiline_text: str):
    # Regex pattern to match multiple page-content pairs
    pattern = r"page:\s*(?P<page>.+?)\s*content:\s*(?P<content>.+?)\s*(?=page:|$)"
    matches = re.finditer(pattern, multiline_text, re.DOTALL)

    # Dictionary to collect content based on page
    content_dict = {}
    for match in matches:
        page = match.group('page').strip()
        content = match.group('content').strip()
        if page in content_dict:
            # Append new content with a newline if page already exists
            content_dict[page] += '\n' + content
        else:
            content_dict[page] = content

    # Create the combined dictionary for output
    combined_dict = {
        "page": ", ".join(content_dict.keys()),
        "content": "\n".join(list(set(content_dict.values())))
    }
    return combined_dict


def parse_and_combine_content_review(multiline_text: str):
    # Regex pattern to match multiple page-content pairs
    # pattern = r"page:\s*(?P<page>.+?)\s*tender_source:\s*(?P<tender_source>.+?)\s*conclusion:\s*(?P<conclusion>.+?)\s*content:\s*(?P<content>.+?)(?=page:|$)"
    pattern = r"tender_source:\s*(?P<tender_source>.+?)\s*conclusion:\s*(?P<conclusion>.+?)\s*content:\s*(?P<content>.+?)(?=page:|$)"
    matches = re.finditer(pattern, multiline_text, re.DOTALL)

    # Dictionary to collect content based on page
    content_dict = {}
    for index, match in enumerate(matches):
        # page = match.group('page').strip()
        tender_source = match.group('tender_source').strip()
        conclusion = match.group('conclusion').strip()
        content = match.group('content').strip()
        if index in content_dict:
            # Append new content with a newline if page already exists
            content_dict[index] += '\n' + content
        else:
            content_dict[index
                         ] = content

    # Create the combined dictionary for output
    combined_dict = {
        # "page": ", ".join(content_dict.keys()) if content_dict else "",
        "content": "\n".join(list(set(content_dict.values()))) if content_dict else "",
        "tender_source": tender_source if content_dict else "",
        "conclusion": conclusion if content_dict else ""
    }
    return combined_dict


def parse_and_combine_content_review_bid(multiline_text: str):
    # Regex pattern to match multiple page-content pairs
    pattern = r"\s*conclusion:\s*(?P<conclusion>.+?)\s*content:\s*(?P<content>.+?)(?=page:|$)"
    matches = re.finditer(pattern, multiline_text, re.DOTALL)

    # Dictionary to collect content based on page
    content_dict = {}
    # conclusion = ""
    # content = ""
    for index, match in enumerate(matches):
        # page = match.group('page').strip()
        conclusion = match.group('conclusion').strip()
        content = match.group('content').strip()
        if index in content_dict:
            # Append new content with a newline if page already exists
            content_dict[index] += '\n' + content
        else:
            content_dict[index] = content

    # Create the combined dictionary for output
    try:
        if conclusion not in ['一致','不一致','无法判断']:
            conclusion = '无法判断'
    except:
        print(multiline_text)
    combined_dict = {
        # "page": ", ".join(content_dict.keys()) if content_dict else "",
        "content": "\n".join(list(set(content_dict.values()))) if content_dict else "",
        "conclusion": conclusion if content_dict else ""
    }
    if combined_dict["content"] == "":
        combined_dict["content"] = '无法判断'
    return combined_dict


def parse_section_info(multiline_text: str):
    # Regex pattern to match multiple page-content pairs
    pattern = r"section:\s*(?P<section>.+?)(?=section:|$)"
    matches = re.finditer(pattern, multiline_text, re.DOTALL)

    # Dictionary to collect content based on page
    content_list = []
    for match in matches:
        point = match.group('section').strip()
        content_list.append(point)

    return content_list


def parse_section_content_info(multiline_text: str):
    # Regex pattern to match multiple page-content pairs
    pattern = r"fixed:\s*(?P<fixed>.+?)\s*content:\s*(?P<content>.+?)(?=fixed:|$)"
    matches = re.finditer(pattern, multiline_text, re.DOTALL)

    # Dictionary to collect content based on page
    for match in matches:
        fixed = match.group('fixed').strip()
        content = match.group('content').strip()

    return fixed, content


def set_request_id():
    request_id = correlation_id.get()

    def _set_request_id():
        correlation_id.set(request_id)

    return _set_request_id
