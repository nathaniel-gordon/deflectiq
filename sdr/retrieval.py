"""Hybrid lexical retrieval core: BM25 + TF-IDF cosine with reciprocal-rank fusion.

Canonical template — copied into RAG projects. Pure numpy/sklearn, fully offline.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_TOKEN_RE = re.compile(r"[a-z0-9]+")

STOPWORDS = frozenset(
    "a an the and or but if then else for to of in on at by with from as is are was were be been "
    "this that these those it its they them their we you your i he she his her not no do does did "
    "can could should would will shall may might must have has had what which who whom how when "
    "where why all each any both more most other some such only own same so than too very".split()
)


def _stem(t: str) -> str:
    """Light suffix stripping so 'passwords' matches 'password', 'policies' matches 'policy'."""
    if len(t) > 4 and t.endswith("ies"):
        return t[:-3] + "y"
    if len(t) > 5 and t.endswith("ing"):
        return t[:-3]
    if len(t) > 4 and t.endswith("ed"):
        return t[:-2]
    if len(t) > 3 and t.endswith("s") and not t.endswith(("ss", "us", "is")):
        return t[:-1]
    return t


def tokenize(text: str) -> list[str]:
    return [_stem(t) for t in _TOKEN_RE.findall(text.lower())
            if t not in STOPWORDS and len(t) > 1]


@dataclass
class Chunk:
    doc_id: str
    chunk_id: int
    text: str
    meta: dict = field(default_factory=dict)


def chunk_text(text: str, doc_id: str, target_words: int = 120, overlap: int = 25,
               meta: dict | None = None) -> list[Chunk]:
    """Split text into overlapping word-window chunks, respecting paragraph breaks."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    words: list[str] = []
    for p in paragraphs:
        words.extend(p.split())
        words.append("\n")  # soft boundary marker
    words = [w for w in words if w != "\n"] or text.split()
    chunks, start, cid = [], 0, 0
    while start < len(words):
        window = words[start:start + target_words]
        chunks.append(Chunk(doc_id, cid, " ".join(window), dict(meta or {})))
        cid += 1
        if start + target_words >= len(words):
            break
        start += target_words - overlap
    return chunks


class BM25:
    """Okapi BM25 over tokenized chunks."""

    def __init__(self, corpus_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.doc_tokens = corpus_tokens
        self.doc_len = np.array([len(d) for d in corpus_tokens], dtype=float)
        self.avgdl = float(self.doc_len.mean()) if len(corpus_tokens) else 0.0
        self.doc_freqs = [Counter(d) for d in corpus_tokens]
        df: Counter = Counter()
        for d in corpus_tokens:
            df.update(set(d))
        n = len(corpus_tokens)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query_tokens: list[str]) -> np.ndarray:
        out = np.zeros(len(self.doc_tokens))
        for tok in query_tokens:
            idf = self.idf.get(tok)
            if idf is None:
                continue
            tf = np.array([d.get(tok, 0) for d in self.doc_freqs], dtype=float)
            denom = tf + self.k1 * (1 - self.b + self.b * self.doc_len / (self.avgdl or 1.0))
            out += idf * tf * (self.k1 + 1) / np.where(denom == 0, 1.0, denom)
        return out


class HybridIndex:
    """BM25 + TF-IDF(1-2gram) cosine, fused with reciprocal-rank fusion."""

    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("cannot index an empty chunk list")
        self.chunks = chunks
        self._tokens = [tokenize(c.text) for c in chunks]
        self.bm25 = BM25(self._tokens)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                                          tokenizer=tokenize, token_pattern=None)
        self.matrix = self.vectorizer.fit_transform([c.text for c in chunks])

    def search(self, query: str, k: int = 5, rrf_k: int = 60) -> list[tuple[Chunk, float]]:
        q_tokens = tokenize(query)
        bm25_scores = self.bm25.scores(q_tokens)
        cos_scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()
        fused: dict[int, float] = {}
        for scores in (bm25_scores, cos_scores):
            order = np.argsort(scores)[::-1]
            for rank, idx in enumerate(order):
                if scores[idx] <= 0:
                    continue
                fused[int(idx)] = fused.get(int(idx), 0.0) + 1.0 / (rrf_k + rank + 1)
        ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:k]
        return [(self.chunks[i], s) for i, s in ranked]
