import re
import json
import shutil
import PyPDF2
import enchant
import contextlib
from docx_ import Docx
from __init__ import *
from pathlib import Path
from typing import TextIO, Union
from werkzeug.datastructures import FileStorage
from difference_between_files.difference import save_disagreement
from flask import render_template, request, make_response, jsonify, Response
from unified.paragraph import paragraph_factory, chapters_by_token_factory, MatchedChapter, ChapterSide, logger


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

    def join_chunks_in_file(self) -> Response:
        current_chunk = int(request.form['dzchunkindex'])
        if os.path.exists(self.absolute_path_filename) and current_chunk == 0:
            return make_response(('File already exists', 400))
        try:
            with open(self.absolute_path_filename, 'ab') as f:
                f.seek(int(request.form['dzchunkbyteoffset']))
                f.write(self.file.stream.read())
        except OSError:
            return make_response(("Not sure why,"
                                  " but we couldn't write the file to disk", 500))
        total_chunks = int(request.form['dztotalchunkcount'])
        if current_chunk + 1 == total_chunks and os.path.getsize(self.absolute_path_filename) != \
                int(request.form['dztotalfilesize']):
            return make_response(('Size mismatch', 500))

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
        pdf_file = PyPDF2.PdfFileReader(open(self.absolute_path_filename, 'rb'))
        if not Path(f"{path_root}/{self.file.filename}").is_file():
            shutil.move(self.absolute_path_filename, path_root)
        new_file = self.get_files(os.path.basename(self.absolute_path_filename).replace(".pdf", ""), f"{path_root}/txt",
                                  pdf_file.numPages, path_root_completed_files)
        return self.return_text_from_pdf(self.remove_empty_lines(new_file.name))


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.post("/upload")
def upload_chunk() -> Union[Response, str]:
    file = request.files['file']
    logger.info(f"Filename is {file.filename}")
    absolute_path_filename = f"{dir_name_pdf}/{file.filename}"
    pdf = PDF(file, absolute_path_filename)
    pdf.join_chunks_in_file()
    if request.content_length < 250800:
        logger.info(f"Content length is {request.content_length}")
        return pdf.main()
    return absolute_path_filename


@app.post("/upload_docx")
def upload_docx() -> str:
    file = request.files['file']
    absolute_path_filename = f"{dir_name_docx}/docx.docx"
    file.save(absolute_path_filename)
    docx = Docx(absolute_path_filename)
    return docx.get_text()


@app.post("/get_disagreement/")
def get_disagreement():
    response = request.json
    return save_disagreement(response["docx"], response["pdf"], response["countError"], response["group_paragraph"],
                             response["file_name_docx"], response["file_name_pdf"])


@app.post("/unified/")
def get_unified_data():
    response = request.json

    # logger = logging.getLogger(__name__)
    all_m_chapters = dict()

    def write_chapters_to_files(head_chapter, filename_prefix):
        text_left = ''
        text_right = ''
        with open(f'{filename_prefix}_left_{thr}.txt', 'w') as f_left:
            with open(f'{filename_prefix}_right_{thr}.txt', 'w') as f_right:
                write_chapter = head_chapter
                while write_chapter:
                    header_to_write = "se2_id: {}, born_border_match: {}, timestamp: {}\n".format(
                        write_chapter.se2_id, write_chapter.born_border_match, write_chapter.born_datetime)
                    f_left.write(header_to_write)
                    f_right.write(header_to_write)

                    lines_to_write = ''
                    for key, val in write_chapter.left_chapter.paragraphs.items():
                        if key >= write_chapter.left_chapter.start_id and key <= write_chapter.left_chapter.end_id:
                            lines_to_write += val.symbols
                    f_left.writelines(lines_to_write)
                    text_left += lines_to_write
                    text_left += '\n'

                    lines_to_write = ''
                    for key, val in write_chapter.right_chapter.paragraphs.items():
                        if key >= write_chapter.right_chapter.start_id and key <= write_chapter.right_chapter.end_id:
                            lines_to_write += val.symbols
                    f_right.writelines(lines_to_write)
                    text_right += lines_to_write
                    text_right += '\n'

                    write_chapter = write_chapter.next
        return text_left, text_right

    def write_all_m_chapters(prefix):
        with open(f'{prefix}_{thr}.txt', 'w') as f:
            f.write("\n".join([str(kv) for kv in all_m_chapters.items()]))

    def spawn_chapters(head_chapter: MatchedChapter):
        next_chapter = head_chapter
        while next_chapter:
            current_chapter = next_chapter
            next_chapter = next_chapter.next
            while current_chapter.spawn_possible(thr):
                logger.info(f'current_chapter is {current_chapter}')
                parent_chapter, child_chapter = current_chapter.spawn_child(thr)
                current_chapter.is_obsolete = True
                all_m_chapters[parent_chapter.se2_id] = parent_chapter
                all_m_chapters[child_chapter.se2_id] = child_chapter

                if current_chapter is head_chapter:
                    head_chapter = parent_chapter
                current_chapter = child_chapter
        return head_chapter

    def flatten_right_paragraphs_text(head_chapter):
        right_text = ''
        next_chapter = head_chapter
        right_text_by_lines = []

        while next_chapter:
            right_paragraphs = next_chapter.right_chapter.paragraphs
            for pid in right_paragraphs.keys():
                current_paragraph_text = right_paragraphs[pid].symbols
                right_text += current_paragraph_text.replace('\n', ' ')
                if next_chapter and pid == next_chapter.right_chapter.end_id:
                    # right_text.replace('\n', '')
                    right_text += '\n' if right_text else ''
                    right_text_by_lines.append(right_text)
                    right_text = ''
                    next_chapter = next_chapter.next
        # right_text_by_lines.append('\n')
        return right_text_by_lines

    MAX_THR = response["threshold"]

    left_text = response["docx"].split("\n")
    right_text = response["pdf"].split("\n")

    left_paragraphs = paragraph_factory(left_text)
    # left_head = left_paragraphs[0]

    right_paragraphs = paragraph_factory(right_text)
    # right_head = right_paragraphs[0]

    left_chapter = ChapterSide(left_paragraphs, 0, next(reversed(left_paragraphs)))
    right_chapter = ChapterSide(right_paragraphs, 0, next(reversed(right_paragraphs)))

    logger.info('MatchedChapter - 1st iteration')
    head_chapter = MatchedChapter(left_chapter, right_chapter)
    all_m_chapters[head_chapter.se2_id] = head_chapter
    thr = .1
    while thr < MAX_THR:
        logger.info(f'Next thr cycle started.! thr is {thr}')
        head_chapter = spawn_chapters(head_chapter)
        write_chapters_to_files(head_chapter, 'thr')
        write_all_m_chapters('all_m_chapters')

        thr = thr * (1 + 0.618)

    logger.info('flatten_right_paragraphs_text...')
    right_text = flatten_right_paragraphs_text(head_chapter)
    with open('flatten_right_paragraphs_text.txt', 'w') as f:
        f.writelines(right_text)
    # Build data structeres from the scratch
    right_paragraphs = paragraph_factory(right_text)
    right_chapter = ChapterSide(right_paragraphs, 0, next(reversed(right_paragraphs)))
    head_chapter = MatchedChapter(left_chapter, right_chapter)

    all_m_chapters = dict()
    all_m_chapters[head_chapter.se2_id] = head_chapter

    #       2. run MatchedChapter spawn_subchapter cycle once again
    logger.info('MatchedChapter - 2nd iteration')
    thr = .1
    while thr < MAX_THR:
        head_chapter = spawn_chapters(head_chapter)
        write_chapters_to_files(head_chapter, 'thr2')
        write_all_m_chapters('all_m_chapters2')
        thr = thr * (1 + 0.618)

    logger.info('chapters_by_token_factory...')
    head_chapter_bt = chapters_by_token_factory(head_chapter)
    all_m_chapters = dict()
    all_m_chapters[head_chapter_bt.se2_id] = head_chapter_bt

    logger.info('MatchedChapterByToken iteration')
    thr = .1
    while thr < MAX_THR * pow(0.618, 1):
        head_chapter_bt = spawn_chapters(head_chapter_bt)
        left_final, right_final = write_chapters_to_files(head_chapter_bt, 'bt_thr')
        write_all_m_chapters('all_m_chapters_bt')

        thr = thr * (1 + 0.618)
        print(thr)

    print(left_final)
    print(right_final)

    dict_data = {
        "docx": left_final,
        "pdf": right_final
    }
    return jsonify(dict_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)