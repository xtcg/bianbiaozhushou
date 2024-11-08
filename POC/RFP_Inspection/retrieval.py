from langchain_core.embeddings import Embeddings
from typing import Optional, List
import requests
import numpy as np


class JinaEmbeddings(Embeddings):
    def __init__(self, url: str, batch_size: Optional[int] = None) -> None:
        super().__init__()
        self.url = url
        self.batch_size = batch_size

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = {"text": texts,
                   "batch_size": self.batch_size}
        response = requests.post(self.url, json=payload)

        if response.status_code == 200:
            return np.array(eval(response.text))
        else:
            return response.status_code

    def embed_query(self, text: str) -> List[float]:

        return self.embed_documents([text])[0]