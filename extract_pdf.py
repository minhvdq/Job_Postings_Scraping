import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# pdf_path = "./resumes/Minh_Vu.pdf"
# content = extract_text_from_pdf(pdf_path)
# print(content)