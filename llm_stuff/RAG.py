from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from pathlib import Path
import os
import file_types_handlers as fth

DB_PATH = "./test_db"
EMBEDDING_MODEL = OllamaEmbeddings(model='embeddinggemma:300m')

FILE_TYPE_HANDLERS = {
    "md": fth.md_handler,
    "pdf":fth.pdf_handler
}

def file_handler(file:Path) -> Document:

    file_type = str(file).split('.')[-1]

    if file_type in FILE_TYPE_HANDLERS:

        return FILE_TYPE_HANDLERS[file_type](file)

    else:

        raise TypeError('This file type is not supported.')



def data_load(path:Path) -> list[Document]:

    # Loads all possible to handle files from directory as Document

    if not os.path.exists(path): raise FileNotFoundError('Directory or file with data to load doesn\'t exist.')

    documents = []

    for directory in os.walk(path):

        files_full_paths:list[Path] = [Path(f'./{directory[0]}/{file_name}') for file_name in directory[-1]]
        
        # filter for only possible to handle files
        files_full_paths = filter(lambda file_path: str(file_path).split('.')[-1] in FILE_TYPE_HANDLERS,files_full_paths)

        for file_path in files_full_paths:
        
            documents.append(file_handler(file_path))

    return documents



def chunking(documents: list[Document]) -> list[Document]:

    # chop documents to chunks befor embedding it

    result = []

    headers = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers,
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750,
        chunk_overlap=100
    )

    for document in documents:

        path = document.metadata['source']

        chunks = markdown_splitter.split_text(document.page_content)

        for chunk in chunks:
            text = chunk.page_content if hasattr(chunk, "page_content") else str(chunk)

            if len(text) > 1100:
                result = result + [Document(page_content=content,\
                                            metadata={'source':path})\
                                            for content in text_splitter.split_text(text)]
            else:
                chunk.metadata = {'source':path}
                result.append(chunk)

    return result



def embedding(documents: list[Document]) -> None:

    db = Chroma.from_documents(
        documents, 
        EMBEDDING_MODEL,
        persist_directory=DB_PATH
    )



def search_from_db(path:Path,query:str,amount:int=3) -> list[Document]:

    db = Chroma(persist_directory=path, embedding_function=EMBEDDING_MODEL)

    return db.similarity_search_with_relevance_scores(query,k=amount)


if __name__ == "__main__":

    path = Path('./test/')

    d = data_load(path)

    chunks = chunking(d)

    #embedding(chunks)

    #print(search_from_db(DB_PATH,'Wyjątki w C++'))