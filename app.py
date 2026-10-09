
from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from classifier import classify_image


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp"}
MAX_FILE_SIZE = 10 * 1024 * 1024

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "image" not in request.files:
            return render_template(
                "index.html",
                error="Please select an image."
            )

        file = request.files["image"]

        if not file.filename:
            return render_template(
                "index.html",
                error="Please select an image."
            )

        if not allowed_file(file.filename):
            return render_template(
                "index.html",
                error="Unsupported file type. "
                "Please upload JPG, PNG, WEBP or BMP."
            )

        safe_filename = secure_filename(file.filename)
        extension = safe_filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid4().hex}.{extension}"
        file_path = UPLOAD_FOLDER / filename

        file.save(file_path)

        try:
            prediction = classify_image(file_path)
        except FileNotFoundError as error:
            file_path.unlink(missing_ok=True)

            return render_template(
                "index.html",
                error=str(error)
            )

        return render_template(
            "result.html",
            image_filename=filename,
            label=prediction["label"],
            confidence=prediction["confidence"]
        )

    return render_template("index.html")


@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "index.html",
        error="The image is too large. Maximum size is 10 MB."
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
