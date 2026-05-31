import subprocess
import streamlit as st
from PIL import Image
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from pdf2image import convert_from_bytes
from docx import Document
import fitz
import os
import zipfile

os.makedirs("output", exist_ok=True)

st.set_page_config(page_title="PDF Converter", layout="centered")

st.title("PDF Converter Tool")

option = st.sidebar.selectbox(
    "Choose Tool",
    [
        "Image to PDF",
        "Text to PDF",
        "DOCX to PDF",
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


# 1. Image to PDF
if option == "Image to PDF":
    files = st.file_uploader(
        "Upload images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if files and st.button("Convert Images to PDF"):
        images = []

        for file in files:
            img = Image.open(file).convert("RGB")
            images.append(img)

        output_path = "output/images_to_pdf.pdf"
        images[0].save(output_path, save_all=True, append_images=images[1:])

        st.success("Images converted to PDF")
        download_file(output_path, "Download PDF", "images_to_pdf.pdf")


# 2. Text to PDF
elif option == "Text to PDF":
    text = st.text_area("Enter your text")

    if st.button("Convert Text to PDF"):
        pdf = FPDF()
        pdf.add_page()

        font_path = "C:/Windows/Fonts/arial.ttf"
        pdf.add_font("ArialUnicode", "", font_path)
        pdf.set_font("ArialUnicode", size=12)

        for line in text.split("\n"):
            pdf.multi_cell(0, 8, line)

        output_path = "output/text_to_pdf.pdf"
        pdf.output(output_path)

        st.success("Text converted to PDF")
        download_file(output_path, "Download PDF", "text_to_pdf.pdf")


# 3. DOCX to PDF
elif option == "DOCX to PDF":
    file = st.file_uploader("Upload DOCX file", type=["docx"])

    if file and st.button("Convert DOCX to PDF"):
        input_path = "output/input.docx"

        with open(input_path, "wb") as f:
            f.write(file.read())

        libreoffice_path = "libreoffice"

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
            st.success("DOCX converted to PDF with same layout")
            download_file(output_path, "Download PDF", "converted_resume.pdf")
        else:
            st.error("Conversion failed")
            st.write(result.stderr)

# 4. PDF to Images
elif option == "PDF to Images":
    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file and st.button("Convert PDF to Images"):
        images = convert_from_bytes(file.read())

        zip_path = "output/pdf_images.zip"

        with zipfile.ZipFile(zip_path, "w") as zip_file:
            for i, image in enumerate(images):
                img_path = f"output/page_{i + 1}.png"
                image.save(img_path, "PNG")
                zip_file.write(img_path)

        st.success("PDF converted to images")
        download_file(zip_path, "Download Images ZIP", "pdf_images.zip")


# 5. Merge PDFs
elif option == "Merge PDFs":
    files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    if files and st.button("Merge PDFs"):
        merger = PdfMerger()

        for file in files:
            merger.append(file)

        output_path = "output/merged.pdf"
        merger.write(output_path)
        merger.close()

        st.success("PDFs merged successfully")
        download_file(output_path, "Download Merged PDF", "merged.pdf")


# 6. Split PDF
elif option == "Split PDF":
    file = st.file_uploader("Upload PDF", type=["pdf"])

    start_page = st.number_input("Start page", min_value=1, step=1)
    end_page = st.number_input("End page", min_value=1, step=1)

    if file and st.button("Split PDF"):
        reader = PdfReader(file)
        writer = PdfWriter()

        total_pages = len(reader.pages)

        if end_page > total_pages:
            st.error(f"PDF has only {total_pages} pages")
        else:
            for page_num in range(start_page - 1, end_page):
                writer.add_page(reader.pages[page_num])

            output_path = "output/split.pdf"

            with open(output_path, "wb") as output:
                writer.write(output)

            st.success("PDF split successfully")
            download_file(output_path, "Download Split PDF", "split.pdf")


# 7. Compress PDF
elif option == "Compress PDF":
    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file and st.button("Compress PDF"):
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


# 8. Rotate PDF
elif option == "Rotate PDF":
    file = st.file_uploader("Upload PDF", type=["pdf"])
    angle = st.selectbox("Select rotation angle", [90, 180, 270])

    if file and st.button("Rotate PDF"):
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


# 9. Password Protect PDF
elif option == "Password Protect PDF":
    file = st.file_uploader("Upload PDF", type=["pdf"])
    password = st.text_input("Enter password", type="password")

    if file and password and st.button("Protect PDF"):
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


# 10. Unlock PDF
elif option == "Unlock PDF":
    file = st.file_uploader("Upload protected PDF", type=["pdf"])
    password = st.text_input("Enter password", type="password")

    if file and password and st.button("Unlock PDF"):
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


# 11. PDF Info
elif option == "PDF Info":
    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file and st.button("Show PDF Info"):
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