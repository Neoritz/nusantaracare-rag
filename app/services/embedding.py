from pathlib import Path
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.services.rag import load_knowledge_base


# ==========================================
# KONFIGURASI
# ==========================================

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

VECTOR_STORE_PATH = Path("data/vector_store")

INDEX_PATH = VECTOR_STORE_PATH / "index.faiss"
METADATA_PATH = VECTOR_STORE_PATH / "metadata.json"


# ==========================================
# MEMBUAT VECTOR STORE
# ==========================================

def create_vector_store():

    print("=" * 60)
    print("MEMUAT KNOWLEDGE BASE")
    print("=" * 60)

    chunks = load_knowledge_base()

    print(f"Jumlah chunk : {len(chunks)}")

    if not chunks:
        raise ValueError(
            "Knowledge base kosong."
        )

    # ======================================
    # FILTER DOKUMEN AKTIF
    # ======================================

    active_chunks = [
        chunk
        for chunk in chunks
        if chunk.get("is_active") is True
    ]

    print(
        f"Chunk aktif  : {len(active_chunks)}"
    )

    if not active_chunks:
        raise ValueError(
            "Tidak ada chunk aktif."
        )

    # ======================================
    # LOAD MODEL EMBEDDING
    # ======================================

    print("\n")
    print("=" * 60)
    print("MEMUAT MODEL EMBEDDING")
    print("=" * 60)

    print(f"Model : {MODEL_NAME}")

    model = SentenceTransformer(
        MODEL_NAME,
        backend="onnx",
        model_kwargs={
            "file_name": "onnx/model_quint8_avx2.onnx"
        }
    )

    print("Model berhasil dimuat.")

    # ======================================
    # SIAPKAN TEXT UNTUK EMBEDDING
    # ======================================

    texts = []

    for chunk in active_chunks:

        text_for_embedding = (
            f"Section: {chunk['section_title']}\n"
        )

        if chunk["subsection_title"]:

            text_for_embedding += (
                f"Subsection: "
                f"{chunk['subsection_title']}\n"
            )

        text_for_embedding += (
            f"\n{chunk['text']}"
        )

        texts.append(
            text_for_embedding
        )

    # ======================================
    # BUAT EMBEDDING
    # ======================================

    print("\n")
    print("=" * 60)
    print("MEMBUAT EMBEDDING")
    print("=" * 60)

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    # ======================================
    # NORMALISASI VECTOR
    # ======================================

    embeddings = embeddings.astype(
        "float32"
    )

    faiss.normalize_L2(
        embeddings
    )

    print(
        f"Jumlah embedding : "
        f"{len(embeddings)}"
    )

    print(
        f"Dimensi vector   : "
        f"{embeddings.shape[1]}"
    )

    # ======================================
    # MEMBUAT FAISS INDEX
    # ======================================

    print("\n")
    print("=" * 60)
    print("MEMBUAT FAISS INDEX")
    print("=" * 60)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    print(
        f"Vector di index : "
        f"{index.ntotal}"
    )

    # ======================================
    # BUAT FOLDER VECTOR STORE
    # ======================================

    VECTOR_STORE_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    # ======================================
    # SIMPAN FAISS INDEX
    # ======================================

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    # ======================================
    # SIMPAN METADATA
    # ======================================

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            active_chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    # ======================================
    # SELESAI
    # ======================================

    print("\n")
    print("=" * 60)
    print("VECTOR STORE BERHASIL DIBUAT")
    print("=" * 60)

    print(
        f"Index    : {INDEX_PATH}"
    )

    print(
        f"Metadata : {METADATA_PATH}"
    )


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    create_vector_store()