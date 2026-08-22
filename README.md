# NusantaraCare RAG

NusantaraCare RAG merupakan aplikasi Customer Service AI yang menggunakan
pendekatan Retrieval-Augmented Generation (RAG).

Aplikasi ini dibuat untuk menjawab pertanyaan pengguna berdasarkan
Knowledge Base internal NusantaraCare. Informasi dari dokumen diproses
menjadi beberapa bagian (chunk), kemudian dibuat embedding agar sistem
dapat mencari informasi yang memiliki kemiripan dengan pertanyaan
pengguna.

Hasil retrieval digunakan sebagai context sebelum pertanyaan dijawab
oleh Large Language Model (LLM).

Jika informasi yang ditanyakan tidak terdapat atau tidak relevan dengan
Knowledge Base, sistem tidak akan membuat informasi baru dan akan
memberikan keterangan bahwa informasi tersebut tidak ditemukan dalam
dokumen.

---

## Tujuan

Project ini bertujuan untuk menerapkan konsep Retrieval-Augmented
Generation (RAG) dalam pembuatan Customer Service AI.

Konsep yang digunakan dalam project ini meliputi:

- Text chunking
- Embedding
- Semantic search
- FAISS
- Hybrid retrieval
- Context retrieval
- Large Language Model (LLM)
- Confidence labeling
- Guardrail untuk mencegah hallucination

---

## Knowledge Base

Knowledge Base yang digunakan dalam project ini adalah dokumen:

**"Panduan Operasional Layanan Internal NusantaraCare"**

Dokumen tersebut berisi panduan mengenai layanan internal NusantaraCare,
seperti:

- Permintaan akses aplikasi
- Penanganan gangguan layanan
- Fasilitas dan perlengkapan kerja
- Kebijakan data
- Status tiket
- SLA
- FAQ operasional

Dokumen tersebut menjadi sumber informasi utama yang digunakan oleh
sistem ketika menjawab pertanyaan pengguna.