import re

from services.parsers.txt_parser import parse_txt
from services.parsers.pdf_parser import parse_pdf
from services.parsers.docx_parser import parse_docx


def clean_markdown(text: str) -> str:
    # merging lines with line-break in the middle of the word
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # removing page numbers
    text = re.sub(r'\n\d+\n', '\n', text)

    # removing repeated EOL (>3 ==> 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def parse(file_name: str):
    extension = re.search(r'(\.[^.]+)$', file_name).group()[1:]

    match(extension):
        case "txt":
            text = parse_txt(file_name)
        case "pdf":
            text = parse_pdf(file_name)
        case "docx":
            text = parse_docx(file_name)

    return text