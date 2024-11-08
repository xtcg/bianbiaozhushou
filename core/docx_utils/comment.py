#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/7/15 10:29
# @File    : comment.py
# @Software: PyCharm
from datetime import datetime

from docx.opc.packuri import PackURI
from docx.opc.part import XmlPart
from docx.opc.constants import CONTENT_TYPE as CT, NAMESPACE, RELATIONSHIP_TYPE as RT
from docx.oxml import parse_xml, OxmlElement, CT_R
from docx.oxml.parser import register_element_cls
from docx.oxml.simpletypes import ST_String, ST_DecimalNumber
from docx.oxml.xmlchemy import BaseOxmlElement, RequiredAttribute, ZeroOrOne, ZeroOrMore
from docx.text.paragraph import Paragraph
from docx.text.run import Run

__all__ = ["add_comment"]

DEFAULT_COMMENTS_XML = (
    b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n"""
    b"""<w:comments xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" """
    b"""xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" """
    b"""xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" """
    b"""xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" """
    b"""xmlns:o="urn:schemas-microsoft-com:office:office" """
    b"""xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" """
    b"""xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" """
    b"""xmlns:v="urn:schemas-microsoft-com:vml" """
    b"""xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" """
    b"""xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" """
    b"""xmlns:w10="urn:schemas-microsoft-com:office:word" """
    b"""xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" """
    b"""xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" """
    b"""xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" """
    b"""xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" """
    b"""xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" """
    b"""xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" """
    b"""xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" """
    b"""xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" """
    b"""mc:Ignorable="w14 w15 w16se wp14"></w:comments>"""
)


class CommentsPart(XmlPart):
    """Definition of Comments Part"""

    @classmethod
    def default(cls, package):
        part_name = PackURI("/word/comments.xml")
        content_type = CT.WML_COMMENTS
        element = parse_xml(cls._default_comments_xml())
        return cls(part_name, content_type, element, package)

    @classmethod
    def _default_comments_xml(cls):
        return DEFAULT_COMMENTS_XML


class CT_Com(BaseOxmlElement):  # noqa
    """
    A ``<w:comment>`` element, a container for Comment properties
    """
    initials = RequiredAttribute('w:initials', ST_String)
    _id = RequiredAttribute('w:id', ST_DecimalNumber)
    date = RequiredAttribute('w:date', ST_String)
    author = RequiredAttribute('w:author', ST_String)

    p = ZeroOrOne('w:p', successors=('w:comment',))

    @classmethod
    def new(cls, initials, comm_id, date, author):
        """
        Return a new ``<w:comment>`` element having _id of *comm_id* and having
        the passed params as meta data
        """
        comment = OxmlElement('w:comment')
        comment.initials = initials
        comment.date = date
        comment._id = comm_id
        comment.author = author
        return comment

    def _add_p(self, text):
        _p = OxmlElement('w:p')
        _r = _p.add_r()  # noqa
        run = Run(_r, self)
        run.text = text
        self._insert_p(_p)  # noqa
        return _p

    @property
    def meta(self):
        return [self.author, self.initials, self.date]

    @property
    def paragraph(self):
        return Paragraph(self.p, self)  # noqa

    @property
    def id(self):
        return self._id


class CT_Comments(BaseOxmlElement):  # noqa
    """
    A ``<w:comments>`` element, a container for Comments properties
    """
    comment = ZeroOrMore('w:comment', successors=('w:comments',))

    def add_comment(self, author, initials, date):
        _next_id = self._next_commentId
        comment = CT_Com.new(initials, _next_id, date, author)
        comment = self._insert_comment(comment)  # noqa
        return comment

    @property
    def _next_commentId(self):
        ids = self.xpath('./w:comment/@w:id')
        _ids = [int(_str) for _str in ids]
        _ids.sort()

        try:
            return _ids[-1] + 2
        except (IndexError, TypeError):
            return 0

    def get_comment_by_id(self, _id):
        namespace = NAMESPACE().WML_MAIN
        for c in self.findall('.//w:comment', {'w': namespace}):
            if c._id == _id:  # noqa
                return c
        return None


class CT_CRS(BaseOxmlElement):  # noqa
    """
    A ``<w:commentRangeStart>`` element
    """
    _id = RequiredAttribute('w:id', ST_DecimalNumber)

    @classmethod
    def new(cls, _id):
        commentRangeStart = OxmlElement('w:commentRangeStart')  # noqa
        commentRangeStart._id = _id

        return commentRangeStart


class CT_CRE(BaseOxmlElement):  # noqa
    """
    A ``w:commentRangeEnd`` element
    """
    _id = RequiredAttribute('w:id', ST_DecimalNumber)

    @classmethod
    def new(cls, _id):
        commentRangeEnd = OxmlElement('w:commentRangeEnd')  # noqa
        commentRangeEnd._id = _id
        return commentRangeEnd


class CT_CRef(BaseOxmlElement):
    """
    w:commentReference
    """
    _id = RequiredAttribute('w:id', ST_DecimalNumber)

    @classmethod
    def new(cls, _id):
        commentReference = OxmlElement('w:commentReference')  # noqa
        commentReference._id = _id
        return commentReference


register_element_cls('w:comments', CT_Comments)
register_element_cls('w:comment', CT_Com)
register_element_cls('w:commentRangeStart', CT_CRS)
register_element_cls('w:commentRangeEnd', CT_CRE)
register_element_cls('w:commentReference', CT_CRef)


def get_comment_element(p: Paragraph):
    """
    Return the ``<w:comments>`` element for the paragraph *p*, creating it if it not exists
    """
    part = p.part
    try:
        comments_part = part.part_related_by(RT.COMMENTS)
    except KeyError:
        comments_part = CommentsPart.default(part)
        part.relate_to(comments_part, RT.COMMENTS)
    return comments_part.element


def add_reference(r: CT_R, comment_id):
    """
    Add a reference to the comment
    """
    reference = OxmlElement('w:commentReference')
    reference._id = comment_id
    r.append(reference)
    return reference


def link_comment(p: Paragraph, comment_id, start: int, end: int):
    """
    Link the comment to the paragraph
    """
    rStart = OxmlElement('w:commentRangeStart')  # noqa
    rStart._id = comment_id
    rEnd = OxmlElement('w:commentRangeEnd')  # noqa
    rEnd._id = comment_id
    elem = p._p  # noqa
    if start == 0 and end == 0:
        elem.insert(0, rStart)
        elem.append(rEnd)
    else:
        elem.insert(start, rStart)
        if end == len(elem.getchildren()) - 1:
            elem.append(rEnd)
        else:
            elem.insert(end + 1, rEnd)


def add_comment(
    p: Paragraph,
    text: str,
    author: str = "AIWaves",
    initials: str = "AI",
    date: str = None,
    start: int = 0,
    end: int = 0
):
    """
    Add a comment to the paragraph

    *p* is the paragraph to which the comment is added
    *text* is the text of the comment
    *author* is the name of the author of the comment
    *initials* is the initials of the author
    *date* is the date of the comment
    *start* is the start index of the comment
    *end* is the end index of the comment
    """
    date = date or datetime.now().isoformat(sep=" ")
    comment_element = get_comment_element(p)
    comment = comment_element.add_comment(author, initials, date)
    comment._add_p(text)  # noqa

    r = p._p.add_r()  # noqa
    add_reference(r, comment.id)
    link_comment(p, comment.id, start, end)
    return comment


if __name__ == '__main__':
    from docx import Document

    d = Document(
        "/Users/huzhenyu/Downloads/测试文件/招标文件测试摘要/00中核寒亭固堤街道300MW光伏发电乡村振兴示范基地项目光伏EPC总承包招标文件（发布稿）.docx"
    )
    paragraph = d.paragraphs[4]
    add_comment(paragraph, text="测试")
    d.save("text.docx")
    ...
