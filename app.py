import streamlit as st
from PIL import Image
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from pdf2image import convert_from_bytes
import fitz
import os
import zipfile
import subprocess
import time
import shutil

os.makedirs("output", exist_ok=True)

st.set_page_config(
    page_title="PDF Converter",
    page_icon="📄",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    .block-container {
        max-width: 1000px;
        padding-top: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .title-box {
        text-align: center;
        padding: 28px 18px;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0px 8px 30px rgba(0,0,0,0.25);
    }

    .title-box h1 {
        font-size: clamp(28px, 6vw, 44px);
        margin-bottom: 10px;
        color: white;
        line-height: 1.2;
    }

    .title-box p {
        font-size: clamp(14px, 3vw, 18px);
        color: #e0e7ff;
        margin-bottom: 0;
    }

    .tool-box {
        background: rgba(15, 23, 42, 0.88);
        padding: 24px;
        border-radius: 18px;
        box-shadow: 0px 4px 18px rgba(0,0,0,0.35);
        margin-bottom: 25px;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    .tool-box h2,
    .tool-box h3,
    .tool-box label,
    .tool-box p {
        color: #f8fafc;
    }

    .stButton button,
    .stDownloadButton button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
        border: none;
    }

    .stButton button:hover,
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #1d4ed8, #6d28d9);
        color: white;
    }

    section[data-testid="stFileUploader"] {
        width: 100%;
    }

    section[data-testid="stFileUploader"] label {
        color: #f8fafc !important;
    }

    section[data-testid="stFileUploader"] button {
        width: auto !important;
        min-width: 120px;
    }

    [data-testid="stFileUploaderDropzone"] {
        padding: 16px !important;
        min-height: 120px !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #020617;
    }

    .footer {
        text-align: center;
        margin-top: 40px;
        padding: 18px;
        color: #cbd5e1;
        font-size: 14px;
    }

    .footer span {
        font-weight: bold;
        color: #60a5fa;
    }

    @media only screen and (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        .title-box {
            padding: 22px 14px;
            border-radius: 16px;
        }

        .tool-box {
            padding: 18px;
            border-radius: 15px;
        }

        [data-testid="stFileUploaderDropzone"] {
            padding: 14px !important;
            min-height: 110px !important;
        }

        section[data-testid="stFileUploader"] button {
            width: 100% !important;
            margin-top: 8px;
        }

        .stButton button,
        .stDownloadButton button {
            font-size: 15px;
            padding: 11px;
        }

        .footer {
            font-size: 13px;
            margin-top: 25px;
        }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-box">
    <h1>PDF Converter Tool</h1>
    <p>Convert, merge, split, compress, rotate and protect your PDF files easily</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("PDF Tools")

option = st.sidebar.selectbox(
    "Choose Tool",
    [
        "DOCX to PDF",
        "Image to PDF",
        "Text to PDF",
        "PDF to Images",
        "Merge PDFs",
        "Split PDF",
        "Compress PDF",
        "Rotate PDF",
        "Password Protect PDF",
        "Unlock PDF",
        "PDF Info"
    ]
)


def download_file(path, label, filename):
    with open(path, "rb") as file:
        st.download_button(label, file, file_name=filename)


def show_progress(message="Processing"):
    progress_text = st.empty()
    progress_bar = st.progress(0)

    for percent in range(0, 101, 10):
        progress_text.write(f"{message}... {percent}%")
        progress_bar.progress(percent)
        time.sleep(0.08)

    progress_text.empty()


def get_libreoffice_path():
    windows_path = r"C:\Program Files\LibreOffice\program\soffice.exe"

    if os.path.exists(windows_path):
        return windows_path

    libreoffice_path = shutil.which("libreoffice")
    if libreoffice_path:
        return libreoffice_path

    soffice_path = shutil.which("soffice")
    if soffice_path:
        return soffice_path

    return None


st.markdown('<div class="tool-box">', unsafe_allow_html=True)


if option == "DOCX to PDF":
    st.subheader("DOCX to PDF")

    file = st.file_uploader(
        "Upload DOCX file",
        type=["docx"],
        key="docx_uploader"
    )

    if file is not None:
        st.success(f"File uploaded: {file.name}")
        st.write(f"File size: {round(file.size / 1024, 2)} KB")

        if st.button("Convert DOCX to PDF"):
            show_progress("Converting DOCX to PDF")

            input_path = "output/input.docx"

            with open(input_path, "wb") as f:
                f.write(file.getbuffer())

            libreoffice_path = get_libreoffice_path()

            if libreoffice_path is None:
                st.error("LibreOffice is not installed or not found.")
                st.info("For local testing, install LibreOffice. For Render deployment, use Dockerfile with LibreOffice installed.")
                st.stop()

            command = [
                libreoffice_path,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                "output",
                input_path
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            output_path = "output/input.pdf"

            if os.path.exists(output_path):
                st.success("DOCX converted successfully")
                download_file(output_path, "Download PDF", "converted_docx.pdf")
            else:
                st.error("Conversion failed")
                st.write(result.stderr)


elif option == "Image to PDF":
    st.subheader("Image to PDF")

    files = st.file_uploader(
        "Upload images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="image_uploader"
    )

    if files and st.button("Convert Images to PDF"):
        show_progress("Converting Images to PDF")

        images = []

        for file in files:
            img = Image.open(file).convert("RGB")
            images.append(img)

        output_path = "output/images_to_pdf.pdf"
        images[0].save(output_path, save_all=True, append_images=images[1:])

        st.success("Images converted to PDF")
        download_file(output_path, "Download PDF", "images_to_pdf.pdf")


elif option == "Text to PDF":
    st.subheader("Text to PDF")

    text = st.text_area("Enter your text")

    if st.button("Convert Text to PDF"):
        if not text.strip():
            st.error("Please enter some text")
        else:
            show_progress("Converting Text to PDF")

            pdf = FPDF()
            pdf.add_page()

            font_path = "C:/Windows/Fonts/arial.ttf"

            if os.path.exists(font_path):
                pdf.add_font("ArialUnicode", "", font_path)
                pdf.set_font("ArialUnicode", size=12)
            else:
                pdf.set_font("Arial", size=12)

            for line in text.split("\n"):
                pdf.multi_cell(0, 8, line)

            output_path = "output/text_to_pdf.pdf"
            pdf.output(output_path)

            st.success("Text converted to PDF")
            download_file(output_path, "Download PDF", "text_to_pdf.pdf")


elif option == "PDF to Images":
    st.subheader("PDF to Images")

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="pdf_to_images_uploader"
    )

    if file and st.button("Convert PDF to Images"):
        show_progress("Converting PDF to Images")

        images = convert_from_bytes(file.read())
        zip_path = "output/pdf_images.zip"

        with zipfile.ZipFile(zip_path, "w") as zip_file:
            for i, image in enumerate(images):
                img_path = f"output/page_{i + 1}.png"
                image.save(img_path, "PNG")
                zip_file.write(img_path, arcname=f"page_{i + 1}.png")

        st.success("PDF converted to images")
        download_file(zip_path, "Download Images ZIP", "pdf_images.zip")


elif option == "Merge PDFs":
    st.subheader("Merge PDFs")

    files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_pdf_uploader"
    )

    if files and st.button("Merge PDFs"):
        if len(files) < 2:
            st.error("Please upload at least 2 PDF files")
        else:
            show_progress("Merging PDFs")

            merger = PdfMerger()

            for file in files:
                merger.append(file)

            output_path = "output/merged.pdf"
            merger.write(output_path)
            merger.close()

            st.success("PDFs merged successfully")
            download_file(output_path, "Download Merged PDF", "merged.pdf")


elif option == "Split PDF":
    st.subheader("Split PDF")

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="split_pdf_uploader"
    )

    start_page = st.number_input("Start page", min_value=1, step=1)
    end_page = st.number_input("End page", min_value=1, step=1)

    if file and st.button("Split PDF"):
        show_progress("Splitting PDF")

        reader = PdfReader(file)
        writer = PdfWriter()

        total_pages = len(reader.pages)

        if end_page > total_pages:
            st.error(f"PDF has only {total_pages} pages")
        elif start_page > end_page:
            st.error("Start page cannot be greater than end page")
        else:
            for page_num in range(start_page - 1, end_page):
                writer.add_page(reader.pages[page_num])

            output_path = "output/split.pdf"

            with open(output_path, "wb") as output:
                writer.write(output)

            st.success("PDF split successfully")
            download_file(output_path, "Download Split PDF", "split.pdf")


elif option == "Compress PDF":
    st.subheader("Compress PDF")

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="compress_pdf_uploader"
    )

    if file and st.button("Compress PDF"):
        show_progress("Compressing PDF")

        input_bytes = file.read()
        doc = fitz.open(stream=input_bytes, filetype="pdf")

        output_path = "output/compressed.pdf"

        doc.save(
            output_path,
            garbage=4,
            deflate=True,
            clean=True
        )

        doc.close()

        st.success("PDF compressed")
        download_file(output_path, "Download Compressed PDF", "compressed.pdf")


elif option == "Rotate PDF":
    st.subheader("Rotate PDF")

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="rotate_pdf_uploader"
    )

    angle = st.selectbox("Select rotation angle", [90, 180, 270])

    if file and st.button("Rotate PDF"):
        show_progress("Rotating PDF")

        reader = PdfReader(file)
        writer = PdfWriter()

        for page in reader.pages:
            page.rotate(angle)
            writer.add_page(page)

        output_path = "output/rotated.pdf"

        with open(output_path, "wb") as output:
            writer.write(output)

        st.success("PDF rotated")
        download_file(output_path, "Download Rotated PDF", "rotated.pdf")


elif option == "Password Protect PDF":
    st.subheader("Password Protect PDF")

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="protect_pdf_uploader"
    )

    password = st.text_input("Enter password", type="password")

    if file and password and st.button("Protect PDF"):
        show_progress("Protecting PDF")

        reader = PdfReader(file)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output_path = "output/protected.pdf"

        with open(output_path, "wb") as output:
            writer.write(output)

        st.success("PDF password protected")
        download_file(output_path, "Download Protected PDF", "protected.pdf")


elif option == "Unlock PDF":
    st.subheader("Unlock PDF")

    file = st.file_uploader(
        "Upload protected PDF",
        type=["pdf"],
        key="unlock_pdf_uploader"
    )

    password = st.text_input("Enter password", type="password")

    if file and password and st.button("Unlock PDF"):
        show_progress("Unlocking PDF")

        reader = PdfReader(file)

        if reader.is_encrypted:
            result = reader.decrypt(password)

            if result == 0:
                st.error("Wrong password")
            else:
                writer = PdfWriter()

                for page in reader.pages:
                    writer.add_page(page)

                output_path = "output/unlocked.pdf"

                with open(output_path, "wb") as output:
                    writer.write(output)

                st.success("PDF unlocked")
                download_file(output_path, "Download Unlocked PDF", "unlocked.pdf")
        else:
            st.info("This PDF is not password protected")


elif option == "PDF Info":
    st.subheader("PDF Info")

    file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        key="pdf_info_uploader"
    )

    if file and st.button("Show PDF Info"):
        show_progress("Reading PDF Info")

        reader = PdfReader(file)

        st.write("Total Pages:", len(reader.pages))
        st.write("Encrypted:", reader.is_encrypted)

        metadata = reader.metadata

        if metadata:
            st.write("Metadata:")
            for key, value in metadata.items():
                st.write(key, ":", value)
        else:
            st.write("No metadata found")


st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    Owned by <span>Spark Industry</span>
</div>
""", unsafe_allow_html=True)