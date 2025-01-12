import os
from openai import OpenAI
import json

from core.utils import timer, parse_section_content_info, parse_section_info
api_key = os.environ.get("API_KEY", "sk-xqwmnocyzfusneirumhmskwiumxtaxiufequpppqwnprntqw")
api_base = os.environ.get("API_BASE", "https://api.siliconflow.cn/v1")
client = OpenAI(api_key=api_key, base_url=api_base)

with open("core/abstract/prompt_check.json", "r", encoding='utf-8') as f:
    prompt_check = json.load(f)

@timer
def generate_response(element, rag_content, prompt_path, check=False):
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_dict = json.load(file)
    remove_dup = []
    seen = set()
    for x in rag_content:
        if x['content'] not in seen:
            remove_dup.append(x)
            seen.add(x['content'])
    rag_content = '\n'.join(x['content'] for x in remove_dup)
    
    sysprompt = prompt_dict[element]["sysprompt"].format(info=rag_content)[:7000]
    userprompt = prompt_dict[element]["userprompt"]
    message = [
        {"role": "system", "content": sysprompt},
        {"role": "user", "content": userprompt}
    ]
    model = 'Qwen/Qwen2.5-72B-Instruct'

    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=5000,
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
        
        if check:
            message = [
                    {"role": "system", "content": prompt_check["system"]},
                    {"role": "user", "content": prompt_check["user"].format(response=response)}
            ]

            stream = client.chat.completions.create(
                model=model, messages=message,
                stream=True,
                max_tokens=5000,
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

            return response, response2
        else:
            return response

    except Exception as e:
        raise
        # print(f"An unexpected error occurred: {e}")
        # print('generation error while', element)
        # return ""

@timer
def generate_respons_pair(element, bid_info, tender_info, prompt_path):
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_dict = json.load(file)
    remove_dup = []
    seen = set()
    for x in bid_info:
        if x['content'] not in seen:
            remove_dup.append(x)
            seen.add(x['content'])
    bid_info = '\n'.join(x['content'] for x in remove_dup)
    systemplate = "你现在是一个标书审阅人，你需要判断输入的信息中提及的{element}是否与招标文件一致。\n输入信息如下\n{bid_info}\n"
    usertemplate = "招标文件中的要求是：\n{tender_info}\n\n你需要判断输入信息的{element}是否与招标文件一致。请你按照规格格式输出结果，格式如下：\ntender_source: 招标文件具体要求内容\nconclusion: 一致/不一致\ncontent: 输入信息内容，对一致/不一致的原因分析"

    try:
        sysprompt = prompt_dict[element]["sysprompt"].format(bid_info=bid_info[:2000])
        userprompt = prompt_dict[element]["userprompt"].format (tender_info=tender_info)
    except:
        sysprompt = systemplate.format(element=element, bid_info=bid_info[:2000])
        userprompt = usertemplate.format(element=element, tender_info=tender_info)
    message = [
        {"role": "system", "content": sysprompt},
        {"role": "user", "content": userprompt}
    ]
    model = 'Qwen/Qwen2.5-72B-Instruct'

    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=5000,
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
        return response

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print('generation error while', element)
        return ""

@timer
def generate_check_elements(tender_info):
    sysprompt = """
你是一个投标文件撰写者，你需要对招标文件的<评审标准>中的审查点进行提取，以便于从投标文件中检索到相关信息。

<评审标准>
{info}
</评审标准>
"""
    userprompt = """
请注意<评审标准>中与评审内容无关的条款，例如候选人数量、评分、计算公式等不需要进行输出。
审查点无需提取评分部分，无需出现商务、技术、报价的详细评审。请按照下面格式输出：
point: 审查点
requirement: 对应的审查要求
"""
    message = [
        {"role": "system", "content": sysprompt.format(info=tender_info)},
        {"role": "user", "content": userprompt}
    ]
    # print(message)
    model = 'Qwen/Qwen2.5-72B-Instruct'

    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=5000,
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
        # print(response)
        return response

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        response = ""


@timer
def generate_outline_sections(section_info):
    sysprompt = f"请你从下面信息中提取第八章投标文件格式需要的子章节信息：\n\n{section_info}"
    userprompt = """
请你输出所有的子章节标题，以下面的为例，但不要照抄例子里的内容：
section: 投标函及投标函附录
section: 法定代表人身份证明或授权委托书

请按照下面的格式进行输出：
section: 对应的子章节，不包含数字
"""
    message = [
        {"role": "system", "content": sysprompt.format(info=section_info)},
        {"role": "user", "content": userprompt}
    ]
    print(message)
    model = 'Qwen/Qwen2.5-72B-Instruct'

    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=5000,
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
        return response

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        response = ""

def generate_outline_content(element, rag_info, eval_info):
    sysprompt = "请根据下面信息判断{element}是否有固定的格式，并输出对应内容：{rag_info}"
    userprompt = "请你直接输出{element}的内容，1为有固定格式，0是没有固定格式。有固定格式的输出对应的格式，但需要去掉不必要的换行；\n没有固定格式的情况需要在content输出对应的评审要求。不要输出其他内容，输出格式为\nfixed: 1或0\ncontent: 格式/评审要求"
    message = [
        {"role": "system", "content": sysprompt.format(element=element, rag_info=rag_info)},
        {"role": "user", "content": userprompt.format(element=element)}
    ]
    model = 'Qwen/Qwen2.5-72B-Instruct'

    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=5000,
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
        print(response)
        fixed, content = parse_section_content_info(response)
        if_fixed = 0
        if fixed.strip() in ['0', '1']:
            if_fixed = int(fixed.strip())
        if if_fixed:
            return content
        
        else:
            sysprompt = "请从中提取与\"{element}\"相匹配的评审标准：\n\n{eval_info}"
            userprompt = """
请你提取出与“{element}”相匹配的评审标准，并作为一个三级标题进行输出，以下面的内容为例，但不要照抄例子里的内容：
section: 对项目重点、难点的分析及施工布置
section: 投标人供主要设备材料的品牌和质量

请按照下面的格式进行输出：
section: 总结性的评审标准作为章节名称
"""
            message = [
        {"role": "system", "content": sysprompt.format(eval_info=eval_info, element=element)},
        {"role": "user", "content": userprompt.format(element=element)}
            ]
            print(message)
            model = 'Qwen/Qwen2.5-72B-Instruct'

            try:
                stream = client.chat.completions.create(
                    model=model, messages=message,
                    stream=True,
                    max_tokens=5000,
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
                print(response)
                eval_list = parse_section_info(response)
                return eval_list
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                response = ""


        # return response

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        response = ""

def generate_outline_type(section_info):
    sysprompt = f"""你现在是一个标书撰写人，现在你需要对一些标书大纲文件按照<商务标，技术标，财务标，报价标，综合>进行分类，其中
                    <商务标>通常包含投标人在财务和合同条款方面的信息。这部分内容主要关注价格、付款条件和其他商务条款。
                    <技术标>主要包括投标人在技术能力和方案方面的信息。技术标的目的是评估投标人是否具备完成项目所需的技术能力和经验，并确定其方案是否符合项目的技术要求和规范。
                    <财务标>主要涉及投标人的财务状况和经济实力评估。这部分内容对于确定投标人的履约能力和项目的经济可行性具有重要意义。
                    <报价标>专门用于详细说明投标方对项目或合同的报价。这通常包括项目的总报价、分项报价、以及与价格相关的各种条款和条件。
                    <综合>如果你认为标书内容包含以上三个方面的内容，那你就可以将它归于此类"""
    userprompt = """
请你仔细阅读以下标书内容{section_info}，并对该内容进行分类。
并仅从<商务标，技术标，财务标，报价标，综合>中选择一项进行回答，不要输出任何其他内容，不需要对你的分析进行解释。
如果你发现没有标书内容或者你认为不能准确的进行分类，直接回复“综合”。
"""
    message = [
        {"role": "system", "content": sysprompt},
        {"role": "user", "content": userprompt.format(section_info=section_info)}
    ]
    # print(message)
    model = 'Qwen/Qwen2.5-72B-Instruct'

    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=100,
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
        return response

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        response = ""

def generate_outline_split(section_info):
    sysprompt = f"""你现在是一个标书撰写人，现在你需要对一些标书大纲文件按照<商务标，技术标，财务标，综合>对一份标书进行拆分，其中
                    <商务标>通常包含投标人在财务和合同条款方面的信息。这部分内容主要关注价格、付款条件和其他商务条款。
                    <技术标>主要包括投标人在技术能力和方案方面的信息。技术标的目的是评估投标人是否具备完成项目所需的技术能力和经验，并确定其方案是否符合项目的技术要求和规范。
                    <财务标>主要涉及投标人的财务状况和经济实力评估。这部分内容对于确定投标人的履约能力和项目的经济可行性具有重要意义。
                    <综合>如果你认为标书内容包含以上三个方面的内容，那你就可以将它归于此类。
                    你会读到标书的内容，同时在每一行内容的最后会有一个<index>，里面的数字方便用来定位。"""
    userprompt = """
请你仔细阅读一下标书内容{section_info}，并对该内容进行分卷。
请返回一个列表，里面的元素是分卷起点的index，不要输出其他内容。
"""
    message = [
        {"role": "system", "content": sysprompt},
        {"role": "user", "content": userprompt.format(info=section_info)}
    ]
    # print(message)
    model = 'Qwen/Qwen2.5-72B-Instruct'

    try:
        stream = client.chat.completions.create(
            model=model, messages=message,
            stream=True,
            max_tokens=5000,
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
        return response

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        response = ""

