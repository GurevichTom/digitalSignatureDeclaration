# Digital Signature Declaration

A Python library (and optional GUI) for detecting PDF declaration type and signing PDFs with placeholder or real signature images. This project is designed to handle Hebrew text rendering in PDF declarations and attach signature images based on the user’s chosen settings.

## Features

- **Declaration Type Detection**: Scans PDF text to classify it as `company`, `foreigner`, or `israeli`.
- **Signature Overlay**: Merges dynamic text (in Hebrew) onto an existing PDF’s first page, then stamps placeholder images representing signatures.
- **GUI Option**: Includes a `gui.py` for a Tkinter-based front end to easily input name, ID, and PDF paths.
- **Configuration**: Centralizes resource paths (signatures, icons, poppler path) in `config.py`, allowing environment-based overrides.

## Requirements

See [requirements.txt](./requirements.txt) for exact versions:
```
PyPDF2, pdfrw, pdf2image, Pillow, reportlab, setuptools
```
You must also have **Poppler** installed or accessible. If running on Windows, set `POPPLER_PATH` in your environment or in `config.py`.

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/GurevichTom/digitalSignatureDeclaration.git
   cd digitalSignatureDeclaration
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure paths** in [`config.py`](./digitalSignatureDeclaration/config.py). For instance:
   - `POPPLER_PATH` for your local Poppler bin directory.
   - `SIGNATURE_PATHS` for placeholder images.
   - `icon_path` if using a specific `.ico` for a GUI.

## Usage

- **As a Library**:
  ```python
  from digitalSignatureDeclaration import sign_declaration, detect_declaration_type

  decl_type = detect_declaration_type("path/to/input.pdf")
  signed_pdf = sign_declaration(
      name="John Doe",
      id_number="123456789",
      input_pdf_path="path/to/input.pdf",
      output_folder="output_dir",
      declaration_type=decl_type,
      declarator_gender="male"
  )
  print("PDF signed, saved at:", signed_pdf)
  ```

- **As a GUI** (`gui.py`):
  ```bash
  python digitalSignatureDeclaration/gui.py
  ```
  This opens a Tkinter window prompting the user for name, ID, PDF path, etc.

## Handling Real Signatures

By default, `signatures/` contains **placeholder** images (`placeholder_signature_1.png` and `placeholder_signature_2.png`). Replace them with real signature scans **only** if authorized and never commit sensitive images publicly.

## Additional Notes

- **Poppler**: If Windows users do not have Poppler installed, either install it or set the path in `POPPLER_PATH`.
- **Icons**: The `.ico` file (`1000_F_387566890_...ico`) is placed in the same directory as `gui.py`. Path references are handled in `config.py`.

## License

Licensed under the [MIT License](https://opensource.org/licenses/MIT). Feel free to adapt or extend this codebase for your needs.

