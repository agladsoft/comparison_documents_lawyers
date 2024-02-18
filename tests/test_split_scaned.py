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


