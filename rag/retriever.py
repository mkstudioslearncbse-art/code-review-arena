# rag/retriever.py
from __future__ import annotations
import json
from pathlib import Path
from typing import List
import faiss
import numpy as np
from models import BugPattern, Severity

PATTERNS_PATH = Path(__file__).parent / "bug_patterns.json"
INDEX_PATH    = Path(__file__).parent / "index.faiss"
IDS_PATH      = Path(__file__).parent / "index_ids.json"
MODEL_NAME    = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

KEYWORD_RULES = {
    "OFF_BY_ONE":       ["off by one", "range", "boundary", "index", "loop bound"],
    "WRONG_OPERATOR":   ["wrong operator", "operator", "comparison", "division"],
    "NULL_POINTER":     ["none", "null", "null pointer", "none check", "attribute error"],
    "MUTABLE_DEFAULT":  ["mutable", "default argument", "list default", "dict default"],
    "SQL_INJECTION":    ["sql", "injection", "query", "database", "cursor"],
    "PATH_TRAVERSAL":   ["path", "traversal", "directory", "filename", "basename"],
    "RACE_CONDITION":   ["race", "thread", "lock", "concurrent", "synchronization"],
    "WRONG_COMPARISON": ["comparison", "is none", "== none", "identity", "equality"],
    "INSECURE_RANDOM":  ["random", "secure", "token", "secrets", "crypto"],
    "INTEGER_OVERFLOW": ["overflow", "integer", "division", "type error", "arithmetic"],
}


class BugRetriever:
    def __init__(self):
        self._patterns = {}
        self._index    = None
        self._ids      = []
        self._model    = None
        self._loaded   = False

    def _load_patterns(self):
        if not self._patterns:
            with open(PATTERNS_PATH, encoding="utf-8") as f:
                patterns = json.load(f)
            self._patterns = {p["bug_id"]: p for p in patterns}

    def _load_model(self):
        if self._loaded:
            return
        self._load_patterns()
        if INDEX_PATH.exists():
            self._index = faiss.read_index(str(INDEX_PATH))
            with open(IDS_PATH, encoding="utf-8") as f:
                self._ids = json.load(f)
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(MODEL_NAME)
        self._loaded = True

    def pattern_exists(self, bug_id: str) -> bool:
        self._load_patterns()
        return bug_id.upper() in self._patterns

    def _make_pattern(self, bug_id: str, score: float) -> BugPattern:
        d = self._patterns[bug_id.upper()]
        return BugPattern(
            bug_id=d["bug_id"],
            name=d["name"],
            description=d["description"],
            example_buggy=d["example_buggy"],
            example_fixed=d["example_fixed"],
            severity=Severity(d["severity"]),
            detection_hint=d["detection_hint"],
            score=float(score),
        )

    def _keyword_match(self, query: str, top_k: int) -> List[BugPattern]:
        self._load_patterns()
        query_lower = query.lower()
        scores = {}
        for bug_id, keywords in KEYWORD_RULES.items():
            score = sum(1.0 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[bug_id] = score
        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            self._make_pattern(bid, sc)
            for bid, sc in top
            if bid in self._patterns
        ]

    def retrieve(self, query: str, top_k: int = 3) -> List[BugPattern]:
        self._load_patterns()
        keyword_results = self._keyword_match(query, top_k)
        if keyword_results and keyword_results[0].score >= 2.0:
            return keyword_results[:top_k]
        try:
            self._load_model()
            if self._model and self._index:
                emb = self._model.encode(
                    [query],
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                emb = np.array(emb, dtype=np.float32)
                D, I = self._index.search(emb, top_k)
                semantic = []
                for score, idx in zip(D[0], I[0]):
                    if idx < 0 or idx >= len(self._ids):
                        continue
                    bid = self._ids[idx]
                    if bid not in self._patterns:
                        continue
                    semantic.append(self._make_pattern(bid, score))
                if keyword_results:
                    seen = {r.bug_id for r in keyword_results}
                    for r in semantic:
                        if r.bug_id not in seen:
                            keyword_results.append(r)
                            seen.add(r.bug_id)
                    return keyword_results[:top_k]
                return semantic[:top_k]
        except Exception as e:
            print(f"[WARN] Semantic search failed: {e}. Using keyword only.")
        return keyword_results[:top_k]

    def build_index(self):
        from sentence_transformers import SentenceTransformer
        self._load_patterns()
        model    = SentenceTransformer(MODEL_NAME)
        patterns = list(self._patterns.values())
        ids      = [p["bug_id"] for p in patterns]
        texts    = [
            f"{p['bug_id']} {p['name']} {p['description']} "
            f"{p['detection_hint']} {p['example_buggy']}"
            for p in patterns
        ]
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        embeddings = np.array(embeddings, dtype=np.float32)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        faiss.write_index(index, str(INDEX_PATH))
        with open(IDS_PATH, "w", encoding="utf-8") as f:
            json.dump(ids, f)
        print(f"Built FAISS index with {len(ids)} bug patterns")


retriever = BugRetriever()