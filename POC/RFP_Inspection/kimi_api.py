import os
from openai import OpenAI
from docx import Document
from preprocessor import preprocess
from langchain.text_splitter import RecursiveCharacterTextSplitter
from zipfile import ZipFile
from bs4 import BeautifulSoup
from langchain_community.retrievers import BM25Retriever
import jieba


MOONSHOT_API_KEY = "sk-Uh9SyrU6wOt2pHidIhQjENaU412rB6mLDjurTKJmkHaVgzoL"

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
    )

def default_preprocessing_func(text: str):
    return list(jieba.cut_for_search(text))

def KimiChat(query : str, temperautre = 0.3) -> str:
    client = OpenAI(
        api_key=MOONSHOT_API_KEY,
        base_url="https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
      model="moonshot-v1-128k",
      messages=[
        {"role": "system", "content": "请抽取出文段中项目业主、项目名称、标段名称、工期、质量、安全、文中落款日期的日期，并以\{'项目业主': \}的格式进行输出。"},
        {"role": "user", "content": query}
      ],
      temperature=temperautre,
    )
    print(completion)
    return completion.choices[0].message.content



if __name__ == "__main__":
    query = preprocess("技术标脱敏稿.docx")
