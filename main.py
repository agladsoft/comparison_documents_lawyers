import magic
from pdf_ import PDF
from docx_ import Docx
from __init__ import *
from typing import Union
from unified.split_scanned_by_paragraph import *
from flask import render_template, request, jsonify, Response
from difference_between_files.difference import save_disagreement

mime_type = None

@app.get("/")
def index() -> str:
    return render_template("index.html")

@app.post("/upload")
def upload_docx() -> Union[Response, str]:
    global mime_type
    file = request.files['file']
    page_header = request.headers.environ["HTTP_PAGE_HEADER"] == "true"
    file_for_define_mime = f"{os.environ.get('PATH_DOCUMENTS')}/{file.filename}"
    if not mime_type:
        mime_type = magic.Magic().from_buffer(file.stream.read())
    if "PDF" in mime_type:
        absolute_path_filename = f"{dir_name_pdf}/{file.filename}"
        pdf = PDF(file, absolute_path_filename)
        pdf.join_chunks_in_file()
        if request.content_length < 250800:
            logger.info(f"Content length is {request.content_length}")
            return pdf.main()
        return absolute_path_filename
    else:
        file.save(file_for_define_mime)
        absolute_path_filename = f"{dir_name_docx}/{file.filename}"
        docx = Docx(absolute_path_filename)
        return docx.get_text(mime_type, page_header)


@app.post("/get_disagreement/")
def get_disagreement():
    response = request.json
    return save_disagreement(response["docx"], response["pdf"], response["countError"], response["group_paragraph"],
                             response["file_name_docx"], response["file_name_pdf"])


@app.post("/unified/")
def get_unified_data():
    response = request.json
    max_thr = response["threshold"]
    left_text = response["docx"].split("\n")
    right_text = response["pdf"].split("\n")
    left_final, right_final = main(left_text, right_text, max_thr)
    dict_data = {
        "docx": left_final,
        "pdf": right_final
    }
    return jsonify(dict_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
