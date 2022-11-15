import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)
load_dotenv()

console = logging.StreamHandler()
logger = logging.getLogger("loggger")
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(console)
logger.setLevel(logging.INFO)

dir_name_docx = "static/documents/docx"
dir_name_pdf = "static/documents/pdf"
