from pathlib import Path
import json

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


# ==========================================
# KONFIGURASI
# ==========================================

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

VECTOR_STORE_PATH = Path(
    "data/vector_store"
)

INDEX_PATH = VECTOR_STORE_PATH / "index.faiss"
METADATA_PATH = VECTOR_STORE_PATH / "metadata.json"

TOP_K = 3


# ==========================================
# LOAD MODEL
# ==========================================

print("=" * 60)
print("MEMUAT MODEL EMBEDDING")
print("=" * 60)

model = None


def get_model():

    global model

    if model is None:

        print("Memuat model embedding...")

        model = SentenceTransformer(
            MODEL_NAME
        )

        print("Model berhasil dimuat.")

    return model


# ==========================================
# LOAD FAISS
# ==========================================

print("\n")
print("=" * 60)
print("MEMUAT FAISS INDEX")
print("=" * 60)

index = faiss.read_index(
    str(INDEX_PATH)
)

print(
    f"Jumlah vector : {index.ntotal}"
)


# ==========================================
# LOAD METADATA
# ==========================================

with open(
    METADATA_PATH,
    "r",
    encoding="utf-8"
) as file:

    metadata = json.load(file)

print(
    f"Jumlah metadata : {len(metadata)}"
)


# ==========================================
# RETRIEVAL
# ==========================================

def search(
    query: str,
    top_k: int = TOP_K,
    min_score: float = 0.50
):

    # ======================================
    # Embedding query
    # ======================================

    model_instance = get_model()

    query_embedding = model_instance.encode(
        [query],
        convert_to_numpy=True
    )

    query_embedding = query_embedding.astype(
        "float32"
    )

    # ======================================
    # Normalisasi
    # ======================================

    faiss.normalize_L2(
        query_embedding
    )

    # ======================================
    # Search FAISS
    # ======================================

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        if idx < 0:
            continue

        chunk = metadata[idx].copy()

        # Hanya dokumen aktif
        if not chunk.get("is_active", False):
            continue

        # Filter berdasarkan similarity
        if float(score) < min_score:
            continue

        chunk["score"] = float(score)

        results.append(chunk)

    return results

# ======================================
# CONFIDENCE
# ======================================

def get_confidence(results):

    # Tidak ada context yang melewati
    # threshold relevansi
    if not results:
        return {
            "confidence_label": "low",
            "reason_code": "no_relevant_context"
        }

    top_score = results[0]["score"]

    if top_score >= 0.60:
        return {
            "confidence_label": "high",
            "reason_code": "answered"
        }

    return {
        "confidence_label": "medium",
        "reason_code": "answered"
    }


# ==========================================
# TEST RETRIEVAL
# ==========================================

if __name__ == "__main__":

    query = input(
        "\nMasukkan pertanyaan: "
    )

    results = search(
        query=query,
        top_k=TOP_K,
        min_score=0.50
    )

    confidence = get_confidence(
        results
    )

    print("\n")
    print("=" * 60)
    print("HASIL RETRIEVAL")
    print("=" * 60)

    print(
        f"Pertanyaan : {query}"
    )

    print(
        f"Top-K      : {TOP_K}"
    )

    print(
        f"Confidence : "
        f"{confidence['confidence_label']}"
    )

    print(
        f"Reason     : "
        f"{confidence['reason_code']}"
    )

    if not results:

        print("\n")
        print(
            "Tidak ditemukan context "
            "yang relevan dalam dokumen."
        )

    else:

        for i, result in enumerate(
            results,
            start=1
        ):

            print("\n")
            print("-" * 60)

            print(
                f"Rank       : {i}"
            )

            print(
                f"Score      : "
                f"{result['score']:.4f}"
            )

            print(
                f"Chunk ID    : "
                f"{result['chunk_id']}"
            )

            print(
                f"Section     : "
                f"{result['section_title']}"
            )

            print(
                f"Subsection  : "
                f"{result['subsection_title'] or '-'}"
            )

            print(
                f"Doc Version : "
                f"{result['doc_version']}"
            )

            print(
                f"Is Active   : "
                f"{result['is_active']}"
            )

            print("\nIsi:")
            print(result["text"])