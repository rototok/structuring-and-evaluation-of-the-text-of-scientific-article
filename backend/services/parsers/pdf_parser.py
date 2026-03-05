import re

import pymupdf4llm


def parse_pdf(file_name: str) -> str:
    md_text = pymupdf4llm.to_markdown(file_name)

    return md_text