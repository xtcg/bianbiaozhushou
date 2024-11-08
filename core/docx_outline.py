import re
import os
from core.docx_parse import Docx, POTENTIAL_PATTERNS, remove_space
from langchain_core.documents import Document as langchain_Document
from langchain_community.vectorstores import FAISS
from core.retrieval import content_retrieve, JinaEmbeddings
from core.generate import generate_outline_type
from core.docx_comment import add_comment_to_elements_in_place
class Outline(Docx):

    def __init__(self, file_path: str, use_cache: bool = False, temp_path: str = None, hash_path: str = None):
        super().__init__(file_path, use_cache) 
        if temp_path and hash_path:
            self.set_cached_dir(temp_path, hash_path)
        self.get_rag()
        # print(file_path)
        # print(list(self.contents['paragraphs'].values())[:5])
        self.index_list = list(map(str, self.contents['paragraphs']))
  
    def find_target_in_catalogs(self):
        try:
            all_documents = []
            for i in self.catalogs:
                all_documents.append(langchain_Document(page_content=i))
            db = FAISS.from_documents(documents=all_documents, embedding=JinaEmbeddings)
            _, docs = content_retrieve({"query":"第七章投标文件格式"}, db, 3)
            target = docs[0].page_content
            if '格式' in target:    
                return True, Target
        except:
            pass
        return True, "第七章 投标文件格式"
        if "格式" not in target:
            self.doc.save(os.path.join(self.cached_dir,'outline.docx'))
            return False, os.path.join(self.cached_dir,'outline.docx')
        else:
            return True, target
    
    def find_entry(self, target: str):
        # find pattern for detected outline entry string
        pattern = None
        for p in POTENTIAL_PATTERNS[::-1]:
            pa = re.compile(p)
            if pa.match(target):
                print(p,target)
                pattern = pa
                break
        
        split_index = []
        left = int(self.head_of_content)
        index_list = list(map(str, self.contents['paragraphs'].keys()))
        
        # find detected str, find final positin with edit distance <= 1
        for threshold in [2,3,4,5]:
            point = 0
            tag = len(index_list)
            while point < len(index_list):
                if r:=self.minDistance(remove_space(self.contents['paragraphs'][index_list[point]]['text']), remove_space(target)) <= threshold:
                    tag = point
                    threshold = r
                point += 1
            if tag != len(index_list):
                break
        if tag == len(index_list):
            self.doc.save(os.path.join(self.cached_dir,'outline.docx'))
            return False, os.path.join(self.cached_dir,'outline.docx')
        point = tag
        split_index.append(point)
        # find peer subtitile and record the number of titles. cover usually contains title
        point += 1
        title_list = []
        while point < len(index_list) and (not pattern.match(self.contents['paragraphs'][index_list[point]]['text'])):
            if self.minDistance(self.contents['paragraphs'][index_list[point]]['text'],self.head) < 3:
                title_list.append(point)
            point += 1
        split_index.append(point)
        if len(title_list) and len(title_list) <= 4:
            split_index.extend(title_list)
        # print(split_index,self.head)
        return True, split_index
    
    def find_split(self,split_index):
        pattern = None
        point = split_index[0]+1
        while pattern == None and point < split_index[-1]:
            for p in POTENTIAL_PATTERNS[-4:]:
                pa = re.compile(p)
                if pa.match(self.contents['paragraphs'][self.index_list[point]]['text']):
                    pattern = pa
                    # print(p)
                    break
            point += 1
        if pattern == None:
            return False, split_index
        point = split_index[0]+1
        seen = dict()
        right_end = min(len(self.index_list),split_index[-1]) if len(self.index_list) > 1 else len(self.index_list)
        # print(right_end)
        while point < right_end:
            if r := pattern.match(self.contents['paragraphs'][self.index_list[point]]['text']):
                seen[self.contents['paragraphs'][self.index_list[point]]['text']] = point
                # print(self.contents['paragraphs'][self.index_list[point]]['text'])
            point += 1
        for i in seen:
            split_index.append(seen[i])
        return True, split_index
    
    def find_split1(self, split_index):
        # find the highest catalog level after the first line of detected content
        point = split_index[0]+1
        pattern = ''
        head = ''
        seen = dict()
        
        while pattern == '' and point < len(self.index_list):
            for p in POTENTIAL_PATTERNS[::-1]:
                pp = re.compile(p)
                if r := pp.match(self.contents['paragraphs'][self.index_list[point]]['text']):
                    seen[self.contents['paragraphs'][self.index_list[point]]['text']] = point
                    head = r.group(1)
                    pattern = re.compile(p)
                    break
            point += 1
            
        right_end = min(len(self.index_list),split_index[-1]) if len(self.index_list) > 1 else len(self.index_list)
        print(right_end)
        while point < right_end:
            if r := pattern.match(self.contents['paragraphs'][self.index_list[point]]['text']):
                if r.group(1) == head:
                    if len(seen) and self.contents['paragraphs'][self.index_list[point]]['text'] in seen:
                        split_index.append(point)
                        seen.pop(self.contents['paragraphs'][self.index_list[point]]['text'])
                    else:
                        seen[self.contents['paragraphs'][self.index_list[point]]['text']] = point
            point += 1
        return split_index
    
    def get_split_type(self, split_index):
        comments = []
        if len(self.index_list) == split_index[-1]:
            self.doc.add_paragraph('')
            self.index_list.append(str(int(self.index_list[-1])+1))
            self.contents['check'][str(self.index_list[split_index[-1]])] = {"index":str(len(self.doc.paragraphs)),
                                                                          "type": "paragraph"}

        if len(split_index) == 2:
            comments = ['综合','end']
        else:
            comments.append('cover')
            for sp in range(1,len(split_index)-1):
                s = ''
                for i in range(int(self.contents['check'][str(self.index_list[split_index[sp]])]['index']),int(self.contents['check'][str(self.index_list[split_index[sp+1]])]['index'])):
                    if len(self.doc.paragraphs[i].text):
                        s += self.doc.paragraphs[i].text + '\n'
                split_type = generate_outline_type(s)
                if split_type == '综合' or split_type not in ['商务标','技术标','财务标','报价标']:
                    split_type = '综合'
                elif split_type[:2] not in s[:min(250,len(s))]:
                    # print(split_type, s[:200])
                    split_type = '综合'
                comments.append(split_type)
            comments.append('end')
        return comments
    
    def add_comments(self, split_index, comments):
        import collections
        count = collections.Counter(comments)
        if len(split_index) <= 3:
            split_index = [split_index[0],split_index[-1]]
            comments = [comments[0],comments[-1]]
        elif any([count[x] > 1 for x in count]):
            split_index = [split_index[0],split_index[-1]]
            comments = [comments[0],comments[-1]]
        elif '综合' in comments and comments.index('综合') > 1:
            split_index = [split_index[0],split_index[-1]]
            comments = [comments[0],comments[-1]]
        if len(comments) == 2:
            comments[0] = '综合'
        if len(self.index_list) == split_index[-1] + 1:
            split_index.pop()
            add_comment_to_elements_in_place(self.doc, [self.doc.paragraphs[-1]._element], 'bianbiaozhushou', comments.pop())
        # print(len(self.doc.paragraphs))
        # print(split_index)
        # print(self.file_path)
        # print(self.contents['paragraphs'])
        for i in range(len(split_index)):
            print(i)
            pos = int(self.contents['check'][str(self.index_list[split_index[i]])]['index'])
            print(pos)
            add_comment_to_elements_in_place(self.doc, [self.doc.paragraphs[pos]._element], 'bianbiaozhushou', comments[i])
        self.doc.save(os.path.join(self.cached_dir,'outline.docx'))
        # self.doc.save(self.file_path.replace('test_docx','test_pdf'))
