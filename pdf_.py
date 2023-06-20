import re
import json
import shutil
import pikepdf
import enchant
import contextlib
from __init__ import *
from pathlib import Path
from typing import TextIO
from flask import Response, jsonify
from werkzeug.datastructures import FileStorage


class PDF(object):
    def __init__(self, file: FileStorage, absolute_path_filename: str):
        self.file: FileStorage = file
        self.absolute_path_filename: str = absolute_path_filename

    @staticmethod
    def concatenate_files(file_name: str, filenames: list) -> TextIO:
        with open(file_name, "w") as outfile:
            for filename in filenames:
                with open(filename) as infile:
                    contents = infile.read()
                    outfile.write(contents)
            return outfile

    @staticmethod
    def concatenate_json_files(file_name: str, filenames: list) -> TextIO:
        result = []
        for f1 in filenames:
            with open(f1, 'r') as infile:
                result.extend(json.load(infile))
        with open(file_name, 'w') as output_file:
            json.dump(result, output_file, indent=4, ensure_ascii=False)
            return output_file

    @staticmethod
    def remove_empty_lines(file_name: str) -> str:
        logger.info(f"{enchant.list_languages()}")
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

    @staticmethod
    def return_text_from_pdf(file_name_without_character: str) -> Response:
        with open(file_name_without_character, 'r') as file:
            data = file.read()
        dict_new_file = {'text': data}
        logger.info(f"type {type(dict_new_file)}")
        return jsonify(dict_new_file)

    @staticmethod
    def return_list_from_json(file_name_without_character: str) -> Response:
        with open(file_name_without_character, 'r') as file:
            data = json.load(file)
        dict_new_file = {'text': data}
        logger.info(f"type {type(dict_new_file)}")
        return jsonify(dict_new_file)

    def get_files(self, file: str, directory: str, total_pages: int, path_root_completed_files: str) -> TextIO:
        infinite_loop = True
        filenames = []
        while infinite_loop:
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    if file in name:
                        if os.path.join(root, name) not in filenames:
                            filenames.append(os.path.join(root, name))
                            filenames = sorted(filenames,
                                               key=lambda x: int(re.findall(r'\d{1,5}', re.split("[.]pdf", x)[1])[0]))
                        infinite_loop = len(filenames) != total_pages
        logger.info(f"All needed files {filenames}")
        return self.concatenate_files(f"{path_root_completed_files}/{file}.txt", filenames)

    def main(self) -> Response:
        path_root = os.environ.get('PATH_ROOT')
        path_root_completed_files = os.environ.get('PATH_ROOT_COMPLETED_FILES')
        pdf_file = pikepdf.Pdf.open(self.absolute_path_filename)
        if not Path(f"{path_root}/{self.file.filename}").is_file():
            shutil.move(self.absolute_path_filename, path_root)
        new_file = self.get_files(os.path.basename(self.absolute_path_filename).replace(".pdf", ""), f"{path_root}/txt",
                                  pdf_file.Root.Pages.Count, path_root_completed_files)
        return self.return_text_from_pdf(self.remove_empty_lines(new_file.name))
