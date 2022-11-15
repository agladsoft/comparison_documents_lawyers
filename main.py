import re
import os
import json
import shutil
import PyPDF2
import enchant
import contextlib
import subprocess
import pdfplumber
from __init__ import *
from pathlib import Path
from fuzzywuzzy import process
from docx2python import docx2python
from typing import TextIO, Union, List
from werkzeug.datastructures import FileStorage
from flask import render_template, request, make_response, jsonify, Response


def clean_special_chars(lst: List[str]) -> List[str]:
    lst = [s.replace(u"\u202F", " ") for s in lst]
    return lst


def get_paragraph_starts(docx_text: List[str], pdf_text: List[str]) -> List[int]:
    index_paragraph = 0
    p_starts = set()
    for dl in docx_text:
        if len(dl) < 3:
            continue
        i = min(70, len(dl))
        prefix = dl[:i]
        pls = process.extract(prefix, pdf_text[index_paragraph:], limit=1)
        pl = pls[0][0]
        index_paragraph = pdf_text.index(pl)
        p_starts.add(index_paragraph)
    return sorted(p_starts)


def format_paragraphs(docx_text: List[str], pdf_text: List[str]) -> str:
    docx_text = clean_special_chars(docx_text)
    pdf_text = clean_special_chars(pdf_text)

    p_starts = get_paragraph_starts(docx_text, pdf_text)

    paragraphs = []
    current_paragraph = ''
    for i, pl in enumerate(pdf_text):
        if i in p_starts:
            if current_paragraph:
                paragraphs.append(current_paragraph)
            current_paragraph = pl
        else:
            current_paragraph = current_paragraph.replace("\n", " ")
            current_paragraph += pl
    return "".join(paragraphs)


def get_text(filename: str) -> str:
    docx_text = docx2python(filename)
    subprocess.check_output(['libreoffice', '--convert-to', 'pdf', filename, '--outdir', os.path.dirname(filename)])
    texts = pdfplumber.open(filename.replace(".docx", ".pdf"))
    list_pdf_text = []
    for text in texts.pages:
        list_pdf_text.extend(line.strip() + '\n' for line in text.extract_text().split('\n'))
    list_docx_text = [line.strip() + '\n' for line in docx_text.text.split('\n')]
    return format_paragraphs(list_docx_text, list_pdf_text)


def join_chunks_in_file(file: FileStorage, save_path: str) -> Response:
    current_chunk = int(request.form['dzchunkindex'])
    if os.path.exists(save_path) and current_chunk == 0:
        return make_response(('File already exists', 400))
    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))
    total_chunks = int(request.form['dztotalchunkcount'])
    if current_chunk + 1 == total_chunks and os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
        return make_response(('Size mismatch', 500))


def get_files(file: str, directory: str, total_pages: int, path_root_completed_files: str) -> TextIO:
    infinite_loop = True
    filenames = []
    while infinite_loop:
        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                if file in name:
                    if os.path.join(root, name) not in filenames:
                        filenames.append(os.path.join(root, name))
                        filenames = sorted(filenames, key=lambda x: int(re.findall(r'\d{1,5}', re.split("[.]pdf", x)[1])
                                                                        [0]))
                    infinite_loop = len(filenames) != total_pages
    logger.info(f"All needed files {filenames}")
    return concatenate_files(f"{path_root_completed_files}/{file}.txt", filenames)
    # return concatenate_json_files(f"{path_root_completed_files}/{file}.json", filenames)


def concatenate_files(file_name: str, filenames: list) -> TextIO:
    with open(file_name, "w") as outfile:
        for filename in filenames:
            with open(filename) as infile:
                contents = infile.read()
                outfile.write(contents)
        return outfile


def concatenate_json_files(file_name: str, filenames: list) -> TextIO:
    result = []
    for f1 in filenames:
        with open(f1, 'r') as infile:
            result.extend(json.load(infile))

    with open(file_name, 'w') as output_file:
        json.dump(result, output_file, indent=4, ensure_ascii=False)
        return output_file


def remove_empty_lines(file_name: str) -> str:
    dictionary = enchant.Dict("ru_RU")
    file_name_without_character = f'{file_name}_without_character.txt'
    with open(file_name, "r", encoding="utf-8") as f:
        with open(file_name_without_character, 'w') as f2:
            data = f.read()
            for line in data.split("\n"):
                with contextlib.suppress(Exception):
                    if len(line.strip()) < 10 and not dictionary.check(line.strip().split()[1]):
                        continue
                    else:
                        f2.write(line + "\n")
    return file_name_without_character


def return_text_from_pdf(file_name_without_character: str) -> Response:
    with open(file_name_without_character, 'r') as file:
        data = file.read()
    dict_new_file = {'text': data}
    logger.info(f"type {type(dict_new_file)}")
    return jsonify(dict_new_file)


def return_list_from_json(file_name_without_character: str) -> Response:
    with open(file_name_without_character, 'r') as file:
        data = json.load(file)
    dict_new_file = {'text': data}
    logger.info(f"type {type(dict_new_file)}")
    return jsonify(dict_new_file)


def main(file: str, base_name_file: str) -> Response:
    path_root = os.environ.get('PATH_ROOT')
    path_root_completed_files = os.environ.get('PATH_ROOT_COMPLETED_FILES')
    pdf_file = PyPDF2.PdfFileReader(open(file, 'rb'))
    if not Path(f"{path_root}/{base_name_file}").is_file():
        shutil.move(file, path_root)
    new_file = get_files(os.path.basename(file).replace(".pdf", ""), f"{path_root}/txt",
                         pdf_file.numPages, path_root_completed_files)
    return return_text_from_pdf(remove_empty_lines(new_file.name))
    # return return_list_from_json(new_file.name)


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.post("/upload")
def upload_chunk() -> Union[Response, str]:
    file = request.files['file']
    save_path = f"{dir_name_pdf}/{file.filename}"
    join_chunks_in_file(file, save_path)
    if request.content_length < 250800:
        logger.info(f"Content length is {request.content_length}")
        return main(save_path, file.filename)
    return save_path


@app.post("/upload_docx")
def upload_docx() -> str:
    file = request.files['file']
    path_file = f"{dir_name_docx}/{file.filename}"
    file.save(path_file)
    return get_text(path_file)


if __name__ == "__main__":
    app.run()
