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


split_left_docx_refactoring = read_file('/home/uventus/Works/Юристы/refactoring/left_docx_split_by_scan.txt')
split_right_pdf_refactoring = read_file('/home/uventus/Works/Юристы/refactoring/right_pdf_split_by_scan.txt')
split_left_pdf_refactoring = read_file('/home/uventus/Works/Юристы/refactoring/left_pdf_split_by_scan.txt')
split_right_docx_refactoring = read_file('/home/uventus/Works/Юристы/refactoring/right_docx_split_by_scan.txt')

split_left_docx_improove = read_file('/home/uventus/Works/Юристы/improove/left_docx_split_by_scan.txt')
split_right_pdf_improove = read_file('/home/uventus/Works/Юристы/improove/right_pdf_split_by_scan.txt')

split_right_docx_improove = read_file('/home/uventus/Works/Юристы/improove/right_docx_split_by_scan.txt')
split_left_pdf_improove = read_file('/home/uventus/Works/Юристы/improove/left_pdf_split_by_scan.txt')


def test_len_text_left_docx():
    assert len(split_left_docx_refactoring) == len(split_left_docx_improove)


def test_len_text_right_docx():
    assert len(split_right_docx_refactoring) == len(split_right_docx_improove)


def test_len_text_left_pdf():
    assert len(split_left_pdf_refactoring) == len(split_left_pdf_improove)


def test_len_text_right_pdf():
    assert len(split_right_pdf_refactoring) == len(split_right_pdf_improove)


def test_len_text_split_left_docx():
    assert len(split_left_docx_refactoring.split('\n\n')) == len(split_left_docx_improove.split('\n\n'))


def test_len_text_split_right_docx():
    assert len(split_right_docx_refactoring.split('\n\n')) == len(split_right_docx_improove.split('\n\n'))


def test_len_text_split_left_pdf():
    assert len(split_left_pdf_refactoring.split('\n\n')) == len(split_left_pdf_improove.split('\n\n'))


def test_len_text_split_right_pdf():
    assert len(split_right_pdf_refactoring.split('\n\n')) == len(split_right_pdf_improove.split('\n\n'))


def test_len_paragraph_left_docx():
    for index, paragraph in enumerate(split_left_docx_refactoring.split('\n\n')):
        assert len(paragraph) == len(split_left_docx_improove.split('\n\n')[index])


def test_len_paragraph_right_docx():
    for index, paragraph in enumerate(split_left_pdf_refactoring.split('\n\n')):
        assert len(paragraph) == len(split_left_pdf_improove.split('\n\n')[index])


def test_len_paragraph_left_pdf():
    for index, paragraph in enumerate(split_right_docx_refactoring.split('\n\n')):
        assert len(paragraph) == len(split_right_docx_improove.split('\n\n')[index])


def test_len_paragraph_right_pdf():
    for index, paragraph in enumerate(split_right_pdf_refactoring.split('\n\n')):
        assert len(paragraph) == len(split_right_pdf_improove.split('\n\n')[index])



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