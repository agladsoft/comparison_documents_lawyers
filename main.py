import secrets  # built-in module
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_uploads import IMAGES, UploadSet, configure_uploads, DOCUMENTS

app = Flask(__name__)
pdf = UploadSet("photos", DOCUMENTS)

app.config["UPLOADED_PHOTOS_DEST"] = "static/img"
app.config["SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
configure_uploads(app, pdf)


@app.post("/upload")
def upload():
    if "photo" in request.files:
        pdf.save(request.files["photo"])
        flash("Photo saved successfully.")
        return redirect(url_for("index"))


@app.get("/")
def index():
    return render_template("upload.html")


if __name__ == "__main__":
    app.run()