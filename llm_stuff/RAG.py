from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents.base import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from pathlib import Path

DB_PATH = "./test_db"
EMBEDDING_MODEL = OllamaEmbeddings(model='embeddinggemma:300m')


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


