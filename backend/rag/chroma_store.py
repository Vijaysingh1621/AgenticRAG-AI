from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from .embedder import embedder

def build_chroma(docs, persist_dir="chroma_db"):
    texts = []
    metadatas = []
    for doc in docs:
        texts.append(doc["text"])
        metadatas.append({
            "page": doc["page"],
            "image_path": doc.get("image")
        })

    chroma = Chroma.from_texts(texts=texts, embedding=embedder, metadatas=metadatas, persist_directory=persist_dir)
    chroma.persist()
    return chroma

def load_chroma(persist_dir="chroma_db"):
    return Chroma(persist_directory=persist_dir, embedding_function=embedder)
