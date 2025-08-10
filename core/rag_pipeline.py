from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer


class RagPipeline:
    def __init__(self, persist_dir: str, embedding_model: str) -> None:
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection("jarvis")
        self.embedder = SentenceTransformer(embedding_model)

    def add_documents(self, docs: List[Dict[str, Any]]) -> None:
        texts = [d["text"] for d in docs]
        ids = [d["id"] for d in docs]
        metadatas = [d.get("metadata", {}) for d in docs]
        embeddings = self.embedder.encode(texts).tolist()
        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def query(self, q: str, top_k: int = 5) -> List[Dict[str, Any]]:
        emb = self.embedder.encode([q]).tolist()
        res = self.collection.query(query_embeddings=emb, n_results=top_k)
        out: List[Dict[str, Any]] = []
        for i in range(len(res.get("ids", [[]])[0])):
            out.append({
                "id": res["ids"][0][i],
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i]
            })
        return out
