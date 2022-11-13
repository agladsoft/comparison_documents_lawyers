import os
import re
import json
import docx
import fitz
import pdfplumber
import shutil
import PyPDF2
import logging
import enchant
import contextlib
from pathlib import Path
from typing import TextIO
import pypdfium2 as pdfium
from flask_cors import CORS
from dotenv import load_dotenv
from docx2python import docx2python
from flask import Flask, render_template, request, make_response, jsonify, Response

app = Flask(__name__)
CORS(app)
load_dotenv()

console = logging.StreamHandler()
logger = logging.getLogger("loggger")
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(console)
logger.setLevel(logging.INFO)

dir_name = "static/documents"


def get_text(filename):
    # document = docx2python(filename)
    # print(document.text)
    # return document.text

    # with fitz.open(filename) as doc:
    #     text = ""
    #     for page in doc:
    #         text += page.get_text()
    #     return text

    texts = pdfplumber.open(filename)
    pdf_text = ""
    for text in texts.pages:
        pdf_text += text.extract_text().strip()
    return pdf_text


def join_chunks_in_file(file, save_path):
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
    # return concatenate_files(f"{path_root_completed_files}/{file}.txt", filenames)
    return concatenate_json_files(f"{path_root_completed_files}/{file}.json", filenames)


def concatenate_files(file_name: str, filenames: list) -> TextIO:
    with open(file_name, "w") as outfile:
        for filename in filenames:
            with open(filename) as infile:
                contents = infile.read()
                outfile.write(contents)
        return outfile


def concatenate_json_files(file_name, filenames):
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


def main(file, base_name_file):
    path_root = os.environ.get('PATH_ROOT')
    path_root_completed_files = os.environ.get('PATH_ROOT_COMPLETED_FILES')
    pdf_file = PyPDF2.PdfFileReader(open(file, 'rb'))
    if not Path(f"{path_root}/{base_name_file}").is_file():
        shutil.move(file, path_root)
    new_file = get_files(os.path.basename(file).replace(".pdf", ""), f"{path_root}/txt",
                         pdf_file.numPages, path_root_completed_files)
    # return return_text_from_pdf(remove_empty_lines(new_file.name))
    return return_list_from_json(new_file.name)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload_chunk():
    file = request.files['file']
    save_path = f"{dir_name}/{file.filename}"
    join_chunks_in_file(file, save_path)
    if request.content_length < 250900:
        return main(save_path, file.filename)
    return save_path


# @app.post("/move_file")
# def move_file():
#     path_file = request.json['path']
#     save_path = f"{dir_name}/{os.path.basename(path_file)}"
#     return main(save_path, os.path.basename(path_file))


@app.post("/upload_docx")
def upload_docx():
    file = request.files['file']
    path_file = f"{dir_name}/{file.filename}"
    file.save(path_file)
    return get_text(path_file)


if __name__ == "__main__":
    app.run()