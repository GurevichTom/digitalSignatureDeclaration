from setuptools import setup, find_packages

setup(
    name="digitalSignatureDeclaration",  # Name of the package
    version="0.1",  # Version
    packages=find_packages(),  # Automatically detects all Python packages inside the project
    install_requires=[
        "pypdf2",
        "pillow",
        "pdf2image",
        "pdfrw",
        "reportlab",
    ],
)
