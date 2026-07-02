from langchain_core.documents.base import Document
from pathlib import Path
from pymupdf4llm import to_markdown
from re import findall
from PIL import Image
import unicodedata

def get_images(file_contet: str) -> list:

    # Matches one or more consecutive ![](images/....png) blocks
    block_pattern = (
        r"(?:!\[\]\(images\/[^\/]+\.pdf-\d{4}-\d{2}\.png\))"
        r"(?:\s+!\[\]\(images\/[^\/]+\.pdf-\d{4}-\d{2}\.png\))*"
    )

    # Extracts just the path from a single ![](path) token
    path_pattern = r"!\[\]\((images\/[^)]+)\)"

    images = []
    for block in findall(block_pattern, file_contet):
        img_paths = findall(path_pattern, block)
        images.append({
            "text": block,
            "paths": img_paths,
            "images": [Image.open(p) for p in img_paths],
        })

    return images

def md_handler(file_path:Path) -> Document:

    if not str(file_path).split('.')[-1] == 'md': raise TypeError('File has to be a md format.')
    
    with open(file_path,'r',encoding='UTF-8') as file:
        file_content = file.read()

    return Document(
        file_content,
        metadata={'source':str(file_path)}
    )


def pdf_handler(file_path:Path) -> Document:

    if not str(file_path).split('.')[-1] == 'pdf': raise TypeError('File has to be a pdf format.')

    file_content = to_markdown(
        file_path,
        write_images=True,
        image_path='./images',
        image_format='png',
        dpi=300
    )

    file_content =  unicodedata.normalize("NFC", file_content)

    images = get_images(file_content)

    return Document()

