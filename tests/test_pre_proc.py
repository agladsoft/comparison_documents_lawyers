import os
import tempfile
import logging
import pytest
from docx_ import Docx
from unified.split_scanned_by_paragraph import main


def read_file(file_name):
    with open(file_name, 'r') as f:
        file = f.read()
    return file


pre_proc_left_docx_refactoring = read_file(
    '/home/uventus/Works/Юристы/refactoring/left_docx_Предобработка пере split .txt')
pre_proc_right_pdf_refactoring = read_file(
    '/home/uventus/Works/Юристы/refactoring/right_pdf_Предобработка пере split.txt')

pre_proc_left_pdf_refactoring = read_file(
    '/home/uventus/Works/Юристы/refactoring/left_pdf_Предобработка пере split  .txt')
pre_proc_right_docx_refactoring = read_file(
    '/home/uventus/Works/Юристы/refactoring/right_docx_Предобработка пере split .txt')

pre_proc_left_docx_improove = read_file('/home/uventus/Works/Юристы/improove/left_docx_Предобработка пере split .txt')
pre_proc_right_pdf_improove = read_file('/home/uventus/Works/Юристы/improove/right_pdf_Предобработка пере split.txt')

pre_proc_right_docx_improove = read_file('/home/uventus/Works/Юристы/improove/right_docx_Предобработка пере split .txt')
pre_proc_left_pdf_improove = read_file('/home/uventus/Works/Юристы/improove/left_pdf_Предобработка пере split  .txt')


def test_len_text_left_docx():
    assert len(pre_proc_left_docx_refactoring) == len(pre_proc_left_docx_improove)


def test_len_text_right_docx():
    assert len(pre_proc_right_docx_refactoring) == len(pre_proc_right_docx_improove)


def test_len_text_left_pdf():
    assert len(pre_proc_left_pdf_refactoring) == len(pre_proc_left_pdf_improove)


def test_len_text_right_pdf():
    assert len(pre_proc_right_pdf_refactoring) == len(pre_proc_right_pdf_improove)


def test_len_text_split_left_docx():
    assert len(pre_proc_left_docx_refactoring.split('\n')) == len(pre_proc_left_docx_improove.split('\n'))


def test_len_text_split_right_docx():
    assert len(pre_proc_right_docx_refactoring.split('\n')) == len(pre_proc_right_docx_improove.split('\n'))


def test_len_text_split_left_pdf():
    assert len(pre_proc_left_pdf_refactoring.split('\n')) == len(pre_proc_left_pdf_improove.split('\n'))


def test_len_text_split_right_pdf():
    assert len(pre_proc_right_pdf_refactoring.split('\n')) == len(pre_proc_right_pdf_improove.split('\n'))


def test_len_paragraph_left_docx():
    for index, paragraph in enumerate(pre_proc_left_docx_refactoring.split('\n')):
        assert len(paragraph) == len(pre_proc_left_docx_improove.split('\n')[index])


def test_len_paragraph_right_docx():
    for index, paragraph in enumerate(pre_proc_left_pdf_refactoring.split('\n')):
        assert len(paragraph) == len(pre_proc_left_pdf_improove.split('\n')[index])


def test_len_paragraph_left_pdf():
    for index, paragraph in enumerate(pre_proc_right_docx_refactoring.split('\n')):
        assert len(paragraph) == len(pre_proc_right_docx_improove.split('\n')[index])


def test_len_paragraph_right_pdf():
    for index, paragraph in enumerate(pre_proc_right_pdf_refactoring.split('\n')):
        assert len(paragraph) == len(pre_proc_right_pdf_improove.split('\n')[index])



if __name__ == '__main__':
    test_len_text_left_docx()
    test_len_text_right_docx()
    test_len_text_left_pdf()
    test_len_text_right_pdf()
    test_len_text_split_left_docx()
    test_len_text_split_right_docx()
    test_len_text_split_left_pdf()
    test_len_text_split_right_pdf()
    test_len_paragraph_left_docx()
    test_len_paragraph_right_docx()
    test_len_paragraph_left_pdf()
    test_len_paragraph_right_pdf()
