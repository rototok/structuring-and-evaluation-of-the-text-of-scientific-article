import re

from parsers.txt_parser import parse_txt
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx


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
        case "rtf":
            pass

    return text


if __name__ == "__main__":
    file_1 = "C:/Users/alexa/Desktop/Саша/MISIS/Master/Diploma/test texts/Статья_ТолстенкоАА_ред_v2.txt"
    file_2 = "C:/Users/alexa/Desktop/Саша/Резюме Толстенко.pdf"
    file_3 = "C:/Users/alexa/Desktop/Саша/MISIS/Master/Diploma/test texts/Статья_ТолстенкоАА_ред_v2.pdf"
    file_4 = "C:/Users/alexa/Desktop/Саша/MISIS/Master/Diploma/test texts/Статья_ТолстенкоАА_ред_v2.docx"

    text_1 = parse(file_1)
    text_2 = parse(file_2)
    text_3 = parse(file_3)
    text_4 = parse(file_4)

    with open("test.md", mode='w', encoding="UTF-8") as file:
        file.write(text_4)