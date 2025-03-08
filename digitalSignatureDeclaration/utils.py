"""
utils.py

Contains auxiliary functions for digitalSignatureDeclaration, such as
PDF text extraction or type detection.
"""

import PyPDF2

def detect_declaration_type(file_path):
    """
    Scans a PDF for keywords to classify the declaration as 'company', 'foreigner', or 'israeli'.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: One of ['company', 'foreigner', 'israeli'] based on textual content.
    """

    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            text = reader.pages[page_num].extract_text()
            if 'פרטי החברה השוכרת' in text:
                return 'company'
            if 'זר' in text:
                return 'foreigner'
    return 'israeli'
