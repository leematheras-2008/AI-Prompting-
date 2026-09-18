"""
OCR-capable version of create_db_with_pdf.py
----------------------------------------------
Handles BOTH kinds of PDFs automatically:
  1. Normal text PDFs  -> extracted directly (fast, like your original script)
  2. Scanned/image PDFs -> OCR'd page by page using Tesseract
  3. Mixed PDFs (some real-text pages, some scanned pages) -> handled per-page

Logic: for each page, try normal text extraction first. If that page comes
back empty/near-empty (a strong sign it's a scanned image), fall back to
OCR for JUST that page. This avoids running slow OCR on every page when
it isn't needed.

Install:
    pip install langchain-community langchain-text-splitters langchain-huggingface \
                faiss-cpu pypdf pdf2image pytesseract --break-system-packages

You also need the actual OCR engine + PDF renderer installed on your system
(these are NOT python packages, they're system tools):
    Ubuntu/Debian:  sudo apt-get install tesseract-ocr poppler-utils
    Mac:            brew install tesseract poppler
    Windows:        install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
                    install poppler from https://github.com/oschwartz10612/poppler-windows
"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from pdf2image import convert_from_path
import pytesseract

# ============================================================
# CONFIGURATION
# ============================================================

PDF_FILE = "company_policy.pdf"
DB_PATH = "faiss_index"

# A page is treated as "scanned / needs OCR" if normal extraction
# returns fewer than this many characters of text.
MIN_TEXT_LENGTH_THRESHOLD = 20


# ============================================================
# 1. LOAD PDF - TEXT FIRST, OCR FALLBACK PER PAGE
# ============================================================

def load_pdf_with_ocr_fallback(pdf_path: str) -> list[Document]:
    print("Reading PDF (text layer first)...")

    # Try normal text extraction for every page
    text_loader = PyPDFLoader(pdf_path)
    text_pages = text_loader.load()   # one Document per page, in order

    # Render every page as an image ONCE (needed only for pages that fail text check)
    print("Rendering pages as images (for OCR fallback if needed)...")
    page_images = convert_from_path(pdf_path)

    final_documents = []
    ocr_page_count = 0

    for i, page_doc in enumerate(text_pages):
        extracted_text = page_doc.page_content.strip()

        if len(extracted_text) >= MIN_TEXT_LENGTH_THRESHOLD:
            # Real text layer present and usable - keep as is
            final_documents.append(page_doc)
        else:
            # Looks scanned/empty - OCR this specific page
            ocr_page_count += 1
            print(f"  Page {i + 1}: no usable text layer, running OCR...")
            ocr_text = pytesseract.image_to_string(page_images[i])

            ocr_doc = Document(
                page_content=ocr_text,
                metadata={**page_doc.metadata, "ocr_applied": True}
            )
            final_documents.append(ocr_doc)

    print(f"Total pages: {len(final_documents)}  |  OCR applied to: {ocr_page_count} page(s)")
    return final_documents


documents = load_pdf_with_ocr_fallback(PDF_FILE)


# ============================================================
# 2. SPLIT PDF INTO CHUNKS  (same as your original script)
# ============================================================

print("Splitting PDF into chunks...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # NOTE: your original had 50, which is very small -
    chunk_overlap=50     # 500 keeps more context per chunk for better retrieval
)

chunks = splitter.split_documents(documents)

print("Number of chunks:", len(chunks))


# ============================================================
# 3. CREATE EMBEDDING MODEL  (same as your original script)
# ============================================================

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ============================================================
# 4. CREATE FAISS DATABASE  (same as your original script)
# ============================================================

print("Creating FAISS database...")

vector_db = FAISS.from_documents(
    chunks,
    embeddings
)


# ============================================================
# 5. SAVE FAISS DATABASE  (same as your original script)
# ============================================================

vector_db.save_local(DB_PATH)

print("\n======================================")
print("FAISS DATABASE CREATED")
print("======================================")

print("Vectors:", vector_db.index.ntotal)
print("Vector dimensions:", vector_db.index.d)

print("\nDatabase location:")
print(Path(DB_PATH).absolute())
