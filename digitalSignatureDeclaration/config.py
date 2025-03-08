import os
import sys

def local_dir() -> str:
    """
    Returns the directory where this file (config.py) resides,
    or _MEIPASS if in a PyInstaller environment.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    # fallback: directory of config.py
    return os.path.dirname(os.path.abspath(__file__))

def icon_path() -> str:
    """
    Returns the absolute path to the program icon.
    Kept in the same directory as the code, so it references local_dir().
    """
    return os.path.join(local_dir(), "1000_F_387566890_YDxCELaaf9EJQYHpBojljnvCm8gX7NDW.ico")

def poppler_bin() -> str:
    """
    Returns the path to the poppler bin folder for pdf2image usage.
    If not set, defaults to a local 'poppler-23.05.0/Library/bin'.
    """
    return os.getenv("POPPLER_PATH", "poppler-23.05.0/Library/bin")

def signatures_dir() -> str:
    """
    Returns the path to the 'signatures' folder,
    containing 3-a.png, 5-a.png, etc.
    """
    return os.getenv("SIGNATURES_DIR", os.path.join(local_dir(), "signatures"))

SIGNATURE_PATHS = {
    "signature": os.path.join(signatures_dir(), "placeholder_signature_1.png"),
    "domicar_signature": os.path.join(signatures_dir(), "placeholder_signature_2.png"),
}
