import secrets  # built-in module
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads, DOCUMENTS
import os
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
pdf = UploadSet("photos", DOCUMENTS)

app.config["UPLOADED_PHOTOS_DEST"] = "static/img"
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
configure_uploads(app, pdf)


# @app.post("/upload")
# def upload():
#     if "photo" in request.files:
#         photos.save(request.files["photo"])
#         flash("Photo saved successfully.")
#         return redirect(url_for("index"))


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload_chunk():
    file = request.files["file"]
    file_uuid = request.form["dzuuid"]
    # Generate a unique filename to avoid overwriting using 8 chars of uuid before filename.
    filename = f"{file_uuid[:8]}_{secure_filename(file.filename)}"
    save_path = Path("static", "img", filename)
    current_chunk = int(request.form["dzchunkindex"])

    try:
        with open(save_path, "ab") as f:
            f.seek(int(request.form["dzchunkbyteoffset"]))
            f.write(file.stream.read())
    except OSError:
        return "Error saving file.", 500

    total_chunks = int(request.form["dztotalchunkcount"])

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form["dztotalfilesize"]):
            return "Size mismatch.", 500

    return "Chunk upload successful.", 200


if __name__ == "__main__":
    app.run()