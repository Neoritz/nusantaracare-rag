# NusantaraCare RAG

NusantaraCare RAG merupakan aplikasi Customer Service AI yang menggunakan
pendekatan Retrieval-Augmented Generation (RAG).

Aplikasi ini dibuat untuk menjawab pertanyaan pengguna berdasarkan
Knowledge Base internal NusantaraCare. Informasi dari dokumen diproses
menjadi beberapa bagian, kemudian dibuat embedding agar sistem dapat
mencari informasi yang memiliki kemiripan dengan pertanyaan pengguna.

Hasil pencarian tersebut digunakan sebagai context sebelum pertanyaan
dijawab oleh Gemini.

Jika informasi yang ditanyakan tidak terdapat dalam Knowledge Base,
sistem tidak akan membuat informasi baru dan akan memberikan keterangan
bahwa informasi tersebut tidak ditemukan dalam dokumen.

## Tujuan

Project ini bertujuan untuk menerapkan konsep Retrieval-Augmented
Generation (RAG) dalam pembuatan Customer Service AI.

Konsep yang digunakan dalam project ini meliputi text chunking,
embedding, semantic search, FAISS, retrieval, dan Large Language Model
(LLM).

## Knowledge Base

Knowledge Base yang digunakan dalam project ini adalah dokumen
"Panduan Operasional Layanan Internal NusantaraCare".

Dokumen tersebut berisi panduan mengenai layanan internal NusantaraCare,
seperti permintaan akses aplikasi, penanganan gangguan layanan,
fasilitas dan perlengkapan kerja, kebijakan data, status tiket,
SLA, serta beberapa FAQ operasional.

Dokumen tersebut menjadi sumber informasi utama yang digunakan oleh
sistem ketika menjawab pertanyaan pengguna.

## Teknologi

Project ini dibuat menggunakan Python dengan beberapa library dan
teknologi berikut:

- FastAPI
- Uvicorn
- Sentence Transformers
- FAISS
- NumPy
- Pydantic
- python-dotenv
- Google Gemini API