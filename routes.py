from flask import Blueprint, request, render_template, send_from_directory, current_app
from werkzeug.utils import secure_filename
from utils import (
    extract_text_pdf,
    extract_text_docx,
    smart_chunk_paragraphs_by_page,
    detect_ai_text
)
import os

main_routes = Blueprint('main', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = {"pdf", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@main_routes.route("/", methods=["GET", "POST"])
def upload_file():
    chunks, filetype, filename, detections, text_detections = [], None, None, [], []

    if request.method == "POST":

        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]

            if not allowed_file(file.filename):
                return render_template("upload.html", chunks=[(0, "❌ Unsupported file format.")])

            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if filename.lower().endswith(".pdf"):
                pages = extract_text_pdf(filepath)
                filetype = "pdf"
                chunks = smart_chunk_paragraphs_by_page(pages)

            elif filename.lower().endswith(".docx"):
                pages = extract_text_docx(filepath)
                filetype = "docx"
                chunks = smart_chunk_paragraphs_by_page(pages)

            texts = [chunk for _, chunk in chunks]
            detections = detect_ai_text(texts)


        elif "input_text" in request.form:
            user_text = request.form.get("input_text", "").strip()
            if user_text:
                text_detections = detect_ai_text([user_text])

    return render_template(
    "upload.html",
    chunks=chunks,
    detections=detections,
    text_detections=text_detections,
    filetype=filetype,
    filename=filename,
    zipped_data=zip(chunks, detections)
)



@main_routes.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
