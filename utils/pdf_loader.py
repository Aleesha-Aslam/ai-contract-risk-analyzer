import fitz  # PyMuPDF

def load_pdf(file):
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")

    for page in doc:
        text += page.get_text()

    return text