"""
signing.py

Core module for generating PDF declarations in Hebrew, merging them with an existing
PDF, adding image-based signatures, and adjusting final PDF size to A4.

Exposes:
    - sign_declaration(...): The main entry point for creating a signed, final PDF.
"""

import io
import json
import os
import sys
from datetime import date

import PyPDF2
from PIL import Image
from pdf2image import convert_from_path
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from config import SIGNATURE_PATHS, poppler_bin


def register_hebrew_font():
    """
    Registers the 'Arial.ttf' font with ReportLab for Hebrew character support.

    Raises:
        TTFError: If the font file is not found or fails to load.
    """
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))


def generate_declaration_text(current_date, declarator_name, id_number, declarator_gender):
    """
    Builds the list of Hebrew lines used in the final PDF declaration.

    Args:
        current_date (str): The current date in DD-MM-YYYY format.
        declarator_name (str): Name of the declarant.
        id_number (str): ID number of the declarant, reversed as used in the PDF text.
        declarator_gender (str): 'male' or 'female', determines Hebrew grammar in the text.

    Returns:
        List[str]: The lines of text to be placed on the PDF declaration.
    """

    gender_terms = {
        'male': {
            'title': 'מר', 'known': 'המוכר', 'warned': 'שהוזהר',
            'pronoun': 'עליו', 'expected': 'צפוי', 'confirmed': 'אישר', 'signed': 'חתם'
        },
        'female': {
            'title': 'גב', 'known': 'המוכרת', 'warned': 'שהוזהרה',
            'pronoun': 'עליה', 'expected': 'צפויה', 'confirmed': 'אישרה', 'signed': 'חתמה'
        }
    }
    terms = gender_terms.get(declarator_gender.lower(), gender_terms['male'])

    declaration_text_lines = [
        f' הריני מאשרת כי ביום {current_date} הופיע בפני ',
        'עו"ד מירי רז במשרדי שברחוב השרון 1 קריית שדה התעופה',
        f'{terms["title"]} {declarator_name} ת.ז {id_number} {terms["known"]} לי אישית,',
        f'ולאחר {terms["warned"]} כי {terms["pronoun"]} לאמר את האמת אחרת יהיה',
        f'{terms["expected"]} לעונשים הקבועים בחוק אם לא יעשה כן,',
        f'{terms["confirmed"]} את נכונות ההצהרה ) {terms["signed"]} עליה בפני (',
        '**************************************',
        'מירי רז יוקל מ.ר 23145'
    ]
    return declaration_text_lines


def process_hebrew_text(line, current_date):
    """
    Reverses the given Hebrew line for PDF usage
    and replaces reversed date placeholders with the normal date.

    Args:
        line (str): The line of Hebrew text to process.
        current_date (str): The current date string used to revert reversed placeholders.

    Returns:
        str: The processed line, reversed and date-corrected.
    """

    reversed_line = line[::-1]
    reversed_line = reversed_line.replace(current_date[::-1], current_date)
    return reversed_line


def create_declaration_pdf(signature_text_lines, current_date):
    """
    Generates a PDF from the provided signature text lines using ReportLab.

    Args:
        signature_text_lines (List[str]): Lines of text to place on the PDF.
        current_date (str): The date string used for reference in the text.

    Returns:
        BytesIO: An in-memory PDF buffer (the newly created declaration page).
    """

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont("Arial", 12)

    page_width = letter[0]
    y_position = 300
    line_height = 14

    for line in signature_text_lines:
        processed_line = process_hebrew_text(line, current_date)
        text_width = c.stringWidth(processed_line, 'Arial', 12)
        x_position = (page_width - text_width) / 2 - 100
        c.drawString(x_position, y_position, processed_line)
        y_position -= line_height

    c.save()
    packet.seek(0)
    return packet


def merge_pdfs(input_pdf_path, declaration_pdf_stream):
    """
    Overlays the newly generated PDF declaration page onto the first page of an existing PDF.

    Args:
        input_pdf_path (str): The path to the original PDF.
        declaration_pdf_stream (BytesIO): The in-memory PDF page to merge.

    Returns:
        str: The path to an intermediate PDF file named 'signed_declaration.pdf'.
    """

    reader = PdfReader(input_pdf_path)
    declaration_pdf = PdfReader(declaration_pdf_stream)
    first_page = reader.pages[0]
    merge_page = PageMerge().add(declaration_pdf.pages[0])[0]
    PageMerge(first_page).add(merge_page).render()

    output_file = 'signed_declaration.pdf'
    writer = PdfWriter()
    writer.addPage(first_page)
    writer.write(output_file)

    return output_file


def add_signatures(input_pdf_path, output_pdf_path, declaration_type, signature_paths):
    """
    Pastes signature images onto the first page of the PDF at positions
    dependent on the declaration_type (company, foreigner, israeli).

    Args:
        input_pdf_path (str): Path to the PDF to be signed.
        output_pdf_path (str): Output path for the newly stamped PDF.
        declaration_type (str): One of ['foreigner', 'company', 'israeli'].
        signature_paths (dict): Mapping of keys {'signature', 'domicar_signature'} to image file paths.

    Raises:
        FileNotFoundError: If the signature images are missing.
    """

    pages = convert_from_path(input_pdf_path, poppler_path=poppler_bin())

    signature = Image.open(signature_paths['signature']).resize((600, 600))
    domicar_signature = Image.open(signature_paths['domicar_signature']).resize((650, 650))

    pages[0].paste(signature, (350, 1320), signature)
    if declaration_type == 'foreigner':
        pages[0].paste(domicar_signature, (-30, 1820), domicar_signature)
    elif declaration_type == 'company':
        pages[0].paste(domicar_signature, (-30, 900), domicar_signature)
    elif declaration_type == 'israeli':
        pages[0].paste(domicar_signature, (-30, 1650), domicar_signature)

    pages[0].save(output_pdf_path, save_all=True, append_images=pages[1:])


def adjust_pdf_size(output_pdf_path):
    """
    Ensures the final PDF is scaled to A4 dimensions (595.28 x 841.89 points).

    Args:
        output_pdf_path (str): Path to the PDF to be scaled in-place.

    Raises:
        OSError: If the file cannot be read or written.
    """

    pdf = PyPDF2.PdfReader(output_pdf_path)
    page0 = pdf.pages[0]

    current_width = float(page0.mediabox.width)
    current_height = float(page0.mediabox.height)

    desired_width = 595.28
    desired_height = 841.89

    scale_factor_width = desired_width / current_width
    scale_factor_height = desired_height / current_height

    page0.scale_by(scale_factor_width)
    writer = PyPDF2.PdfWriter()
    writer.add_page(page0)
    with open(output_pdf_path, "wb") as f:
        writer.write(f)


def sign_declaration(name, id_number, input_pdf_path, output_folder, declaration_type, declarator_gender):
    """
    High-level function to produce a fully signed PDF from an existing PDF.

    Steps:
    1. Registers Hebrew font.
    2. Builds lines of text for the declaration.
    3. Merges them onto the first PDF page.
    4. Pastes signatures (regular + domicar) at designated positions.
    5. Adjusts final PDF size to A4 and saves to output_folder.

    Args:
        name (str): The declarant's name.
        id_number (str): The declarant's ID number (normally reversed for some textual effect).
        input_pdf_path (str): Path to the PDF on which to overlay the new text.
        output_folder (str): Directory in which to place the final PDF.
        declaration_type (str): 'company', 'foreigner', or 'israeli'.
        declarator_gender (str): 'male' or 'female'.

    Returns:
        str: The path to the final signed PDF in output_folder.

    Raises:
        Exception: If merging or signature stamping fails for any reason.
    """

    register_hebrew_font()
    current_date = date.today().strftime("%d-%m-%Y")
    id_number_reversed = id_number[::-1]

    signature_text_lines = generate_declaration_text(current_date, name, id_number_reversed, declarator_gender)
    declaration_pdf_stream = create_declaration_pdf(signature_text_lines, current_date)

    merged_pdf_path = merge_pdfs(input_pdf_path, declaration_pdf_stream)

    output_pdf_path = os.path.join(output_folder, "final_output_with_signature.pdf")

    if os.path.isfile(output_pdf_path):
        os.remove(output_pdf_path)

    add_signatures(merged_pdf_path, output_pdf_path, declaration_type, SIGNATURE_PATHS)
    adjust_pdf_size(output_pdf_path)

    return output_pdf_path
