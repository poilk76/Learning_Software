from langchain_core.documents.base import Document
from pathlib import Path
from pymupdf4llm import to_markdown
from re import findall
from PIL import Image
import unicodedata
import os
from numpy import array

CONNECTED_TREASHOLD = 0.6

def are_images_connected(img1:Image.Image,img2:Image.Image) -> bool:

    r = min((img1.width,img2.width))
    effect = 0

    img1 = array(img1)
    img2 = array(img2)

    for i in range(r):

        if img1[-1][i][0] == img2[0][i][0]:
            effect += 1

    return effect/r >= CONNECTED_TREASHOLD



def merge_two_images(img_a: Image.Image, img_b: Image.Image) -> Image.Image:
    
    w = max(img_a.width, img_b.width)
    h = img_a.height + img_b.height

    combined = Image.new("RGB", (w, h), "white")
    combined.paste(img_a, (0, 0))
    combined.paste(img_b, (0, img_a.height))

    return combined



def merge_images(file_content:str,image_path:Path) -> str:

    images = get_images(file_content)

    for image in filter(lambda img_data: len(img_data['image'])>1,images):

        connected = 0
        saved_image=None
        for i in range(1,len(image['image'])):

            if are_images_connected(image['image'][i-1],image['image'][i]):
                connected += 1
                if saved_image == None:
                    saved_image = merge_two_images(image['image'][i-1],image['image'][i])
                else:
                    saved_image = merge_two_images(saved_image,image['image'][i])
            elif connected > 0:
                new_image = merge_two_images(saved_image,image['image'][i])
                saved_image = None

                save_path = f'{image_path}/new0.png'
                j=1
                while os.path.isfile(save_path):
                    save_path = f'{image_path}/new{j}.png'
                    j += 1
                new_image.save(save_path)
                index = file_content.index(image['text'])
                file_content = (
                    file_content[:index]
                    + f"![]({save_path})"
                    + file_content[index + len(image["text"]):]
                )
                connected = 0

def get_images(file_content:str) -> list:

    # Matches one or more consecutive ![](images/....png) blocks
    block_pattern = (
        r"(?:!\[\]\(images\/[^\/]+\.pdf-\d{4}-\d{2}\.png\))"
        r"(?:\s+!\[\]\(images\/[^\/]+\.pdf-\d{4}-\d{2}\.png\))*"
    )

    # Extracts just the path from a single ![](path) token
    path_pattern = r"!\[\]\((images\/[^)]+)\)"

    images = []
    for block in findall(block_pattern, file_content):
        img_paths = findall(path_pattern, block)
        
        images.append({
            "text": block,
            "paths": img_paths,
            "image": [Image.open(img_path) for img_path in img_paths],
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

    file_content = merge_images(file_content,'./images')

    return Document(
        file_content,
        metadata={'source':file_path}
    )

