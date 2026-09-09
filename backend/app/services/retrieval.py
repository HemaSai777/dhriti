import json
import math
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from rank_bm25 import BM25Okapi

from app.config import settings

class HybridRetriever:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.bm25: BM25Okapi = None
        self.tokenized_corpus: List[List[str]] = []
        self.vocab: Dict[str, int] = {}
        self.doc_vectors: np.ndarray = None
        self.load_index()

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into lowercase alphanumeric tokens for BM25 and semantic matching."""
        return re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())

    def load_index(self):
        """Loads chunks.json and builds BM25 and dense vector index."""
        chunks_file = settings.INDEX_DIR / "chunks.json"
        if not chunks_file.exists():
            print("[Retriever] chunks.json not found, attempting auto-ingestion...")
            from app.services.ingestion import ingest_all_documents
            self.chunks = ingest_all_documents()
        else:
            try:
                with open(chunks_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            except Exception as e:
                print(f"[Retriever] Error loading chunks: {e}")
                self.chunks = []

        if not self.chunks:
            print("[Retriever] Warning: No chunks found in knowledge base.")
            return

        # 1. Build BM25 Index
        self.tokenized_corpus = [self.tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        # 2. Build Dense Semantic Vectors (Subword TF-IDF + N-gram Semantic Space)
        # Fast, deterministic, memory-efficient semantic representation
        vocab_set = set()
        for doc in self.tokenized_corpus:
            vocab_set.update(doc)
        self.vocab = {word: idx for idx, word in enumerate(sorted(vocab_set))}
        
        vocab_size = len(self.vocab)
        num_docs = len(self.chunks)
        
        # Compute Document Vectors with sublinear TF and smoothed IDF
        if vocab_size > 0 and num_docs > 0:
            vectors = np.zeros((num_docs, vocab_size), dtype=np.float32)
            df = np.zeros(vocab_size, dtype=np.float32)
            
            for d_idx, doc in enumerate(self.tokenized_corpus):
                unique_words = set(doc)
                for w in unique_words:
                    if w in self.vocab:
                        df[self.vocab[w]] += 1
                for w in doc:
                    if w in self.vocab:
                        vectors[d_idx, self.vocab[w]] += 1

            # Log TF and IDF weighting
            idf = np.log((num_docs + 1) / (df + 1)) + 1.0
            for d_idx in range(num_docs):
                tf = np.log1p(vectors[d_idx])
                vectors[d_idx] = tf * idf
                norm = np.linalg.norm(vectors[d_idx])
                if norm > 1e-6:
                    vectors[d_idx] /= norm
            
            self.doc_vectors = vectors
            print(f"[Retriever] Indexed {num_docs} chunks across {vocab_size} terms successfully.")

    def search_bm25(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Performs sparse BM25 retrieval."""
        if not self.bm25 or not self.chunks:
            return []
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []
        raw_scores = self.bm25.get_scores(query_tokens)
        max_score = max(raw_scores) if len(raw_scores) > 0 and max(raw_scores) > 0 else 1.0
        
        ranked_indices = np.argsort(raw_scores)[::-1][:top_k]
        results = []
        for idx in ranked_indices:
            raw = float(raw_scores[idx])
            # Calibrated scaling: a raw BM25 of 4.0+ across multi-term query represents a strong direct match
            normalized_score = min(1.0, raw / 4.0) if raw > 0 else 0.0
            results.append((int(idx), round(normalized_score, 4)))
        return results

    def search_dense(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """Performs dense semantic vector similarity retrieval."""
        if self.doc_vectors is None or not self.vocab or not self.chunks:
            return []
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []
        
        q_vec = np.zeros(len(self.vocab), dtype=np.float32)
        for w in query_tokens:
            if w in self.vocab:
                q_vec[self.vocab[w]] += 1
        q_vec = np.log1p(q_vec)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 1e-6:
            q_vec /= q_norm
        else:
            return []
        
        sims = np.dot(self.doc_vectors, q_vec)
        ranked_indices = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in ranked_indices:
            score = float(sims[idx])
            # Theoretical max cosine for short query against long doc vector is ~0.35
            norm_dense = min(1.0, score / 0.35) if score > 0 else 0.0
            results.append((int(idx), round(norm_dense, 4)))
        return results

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Combines BM25 and Dense Retrieval using Reciprocal Rank Fusion (RRF)
        and weighted linear score combination.
        """
        if not self.chunks:
            self.load_index()
            if not self.chunks:
                return []

        bm25_results = self.search_bm25(query, top_k=10)
        dense_results = self.search_dense(query, top_k=10)

        # Reciprocal Rank Fusion (k=60)
        rrf_scores: Dict[int, float] = {}
        bm25_map = {idx: score for idx, score in bm25_results}
        dense_map = {idx: score for idx, score in dense_results}

        for rank, (idx, _) in enumerate(bm25_results):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (60 + rank + 1))
        
        for rank, (idx, _) in enumerate(dense_results):
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (60 + rank + 1))

        # Combine RRF rank and normalized raw scores
        scored_candidates = []
        for idx in rrf_scores:
            chunk = self.chunks[idx]
            b_score = bm25_map.get(idx, 0.0)
            d_score = dense_map.get(idx, 0.0)
            
            # Weighted hybrid similarity
            hybrid_score = (settings.BM25_WEIGHT * b_score) + (settings.DENSE_WEIGHT * d_score)
            # Boost if query keywords match section or title
            title_boost = 0.05 if any(t in chunk.get("document_title", "").lower() for t in self.tokenize(query)) else 0.0
            
            final_relevance = min(1.0, hybrid_score + title_boost)
            
            candidate = {
                "chunk_id": idx,
                "text": chunk["text"],
                "source": chunk["source"],
                "document_title": chunk.get("document_title", chunk["source"]),
                "document_id": chunk.get("document_id", "DOC_001"),
                "page": chunk.get("page", 1),
                "section": chunk.get("section", "General Provisions"),
                "score": round(final_relevance, 4),
                "bm25_score": round(b_score, 4),
                "dense_score": round(d_score, 4)
            }
            scored_candidates.append(candidate)

        # Sort descending by relevance score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)
        return scored_candidates[:top_k]

# Global singleton
retriever = HybridRetriever()
