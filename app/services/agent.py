import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.services.retrieval import search


# ==========================================
# LOAD ENVIRONMENT
# ==========================================

load_dotenv()

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY belum ditemukan. "
        "Pastikan sudah dibuat di file .env"
    )


# ==========================================
# GROQ CLIENT
# ==========================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ==========================================
# KONFIGURASI
# ==========================================

TOP_K = 3
MIN_SCORE = 0.50

MODEL_NAME = "openai/gpt-oss-20b"


# ==========================================
# SYSTEM PROMPT
# ==========================================

SYSTEM_PROMPT = """
Anda adalah Customer Service AI NusantaraCare.

Tugas Anda adalah menjawab pertanyaan pengguna
HANYA berdasarkan context yang diberikan.

ATURAN:

1. Jangan menggunakan pengetahuan di luar context.
2. Jangan mengarang informasi.
3. Jika context tidak cukup untuk menjawab,
   katakan bahwa informasi tidak ditemukan
   dalam dokumen.
4. Jangan membuat fakta, prosedur, SLA, angka,
   nama, atau kebijakan baru.
5. Jawaban harus menggunakan bahasa Indonesia
   yang jelas dan mudah dipahami.
6. Jawaban harus relevan dengan pertanyaan pengguna.
7. Jika context memiliki informasi yang relevan,
   gunakan informasi tersebut secara ringkas.
8. Output WAJIB berupa JSON valid.
9. Jangan menambahkan markdown seperti ```json.
10. Jangan menambahkan penjelasan di luar JSON.

Format JSON:

{
  "answer": "jawaban kepada pengguna",
  "confidence_label": "high|medium|low",
  "reason_code": "answered|no_relevant_context"
}
"""


# ==========================================
# MEMBUAT CONTEXT
# ==========================================

def build_context(results):

    if not results:
        return ""

    context_parts = []

    for result in results:

        part = f"""
Chunk ID: {result['chunk_id']}
Section: {result['section_title']}
Subsection: {result['subsection_title'] or '-'}
Document Version: {result['doc_version']}
Is Active: {result['is_active']}
Similarity Score: {result['score']:.4f}

Isi:
{result['text']}
"""

        context_parts.append(
            part.strip()
        )

    return "\n\n---\n\n".join(
        context_parts
    )


# ==========================================
# MEMBUAT PROMPT
# ==========================================

def build_prompt(
    question,
    context
):

    return f"""
{SYSTEM_PROMPT}

PERTANYAAN PENGGUNA:

{question}

CONTEXT DARI KNOWLEDGE BASE:

{context}

INSTRUKSI:

Jawab pertanyaan pengguna hanya berdasarkan
context di atas.

Jika context tidak cukup untuk menjawab,
jangan mengarang.

Kembalikan HANYA JSON valid dengan format:

{{
  "answer": "...",
  "confidence_label": "high|medium|low",
  "reason_code": "answered|no_relevant_context"
}}
"""


# ==========================================
# RETRIEVAL + CONTEXT
# ==========================================

def prepare_agent_input(question):

    results = search(
        query=question,
        top_k=TOP_K,
        min_score=MIN_SCORE
    )

    # ======================================
    # TIDAK ADA CONTEXT RELEVAN
    # ======================================

    if not results:

        return {
            "question": question,
            "context": "",
            "results": [],
            "confidence_label": "low",
            "reason_code": "no_relevant_context"
        }

    # ======================================
    # ADA CONTEXT
    # ======================================

    context = build_context(
        results
    )

    top_score = results[0]["score"]

    # ======================================
    # CONFIDENCE
    # ======================================

    if top_score >= 0.60:

        confidence = "high"

    else:

        confidence = "medium"

    return {
        "question": question,
        "context": context,
        "results": results,
        "confidence_label": confidence,
        "reason_code": "answered"
    }


# ==========================================
# PANGGIL GROQ
# ==========================================

def ask_llm(
    question,
    context,
    confidence_label
):

    prompt = build_prompt(
        question=question,
        context=context
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    response_text = (
        response.choices[0]
        .message
        .content
        .strip()
    )

    return response_text


# ==========================================
# VALIDASI JSON
# ==========================================

def parse_llm_response(
    response_text,
    fallback_confidence="medium"
):

    try:

        # ----------------------------------
        # Bersihkan markdown JSON jika ada
        # ----------------------------------

        cleaned = response_text.strip()

        if cleaned.startswith(
            "```json"
        ):

            cleaned = cleaned[
                7:
            ]

        elif cleaned.startswith(
            "```"
        ):

            cleaned = cleaned[
                3:
            ]

        if cleaned.endswith(
            "```"
        ):

            cleaned = cleaned[
                :-3
            ]

        cleaned = cleaned.strip()

        # ----------------------------------
        # Parse JSON
        # ----------------------------------

        data = json.loads(
            cleaned
        )

        # ----------------------------------
        # Validasi field
        # ----------------------------------

        answer = data.get(
            "answer"
        )

        confidence = data.get(
            "confidence_label"
        )

        reason = data.get(
            "reason_code"
        )

        if not isinstance(
            answer,
            str
        ):

            raise ValueError(
                "Field answer tidak valid."
            )

        if confidence not in {
            "high",
            "medium",
            "low"
        }:

            confidence = fallback_confidence

        if reason not in {
            "answered",
            "no_relevant_context"
        }:

            reason = "answered"

        return {
            "answer": answer,
            "confidence_label": confidence,
            "reason_code": reason
        }

    except Exception:

        return {
            "answer": response_text,
            "confidence_label": fallback_confidence,
            "reason_code": "answered"
        }


# ==========================================
# JAWAB PERTANYAAN
# ==========================================

def answer_question(question):

    # ======================================
    # RETRIEVAL
    # ======================================

    data = prepare_agent_input(
        question
    )

    # ======================================
    # JIKA TIDAK ADA CONTEXT
    # ======================================

    if not data["context"]:

        return {
            "answer": (
                "Informasi tersebut tidak "
                "ditemukan dalam dokumen "
                "Knowledge Base NusantaraCare."
            ),
            "confidence_label": "low",
            "reason_code": "no_relevant_context"
        }

    # ======================================
    # PANGGIL LLM
    # ======================================

    response_text = ask_llm(
        question=data["question"],
        context=data["context"],
        confidence_label=data[
            "confidence_label"
        ]
    )

    # ======================================
    # VALIDASI RESPONSE
    # ======================================

    result = parse_llm_response(
        response_text,
        fallback_confidence=data[
            "confidence_label"
        ]
    )

    # ======================================
    # SINKRONISASI DENGAN RETRIEVAL
    # ======================================
    #
    # Confidence utama berasal dari retrieval.
    # LLM tetap menghasilkan confidence sesuai
    # format materi, tetapi kita cegah hasil akhir
    # bertentangan dengan hasil retrieval.
    #

    result["confidence_label"] = data[
        "confidence_label"
    ]

    result["reason_code"] = data[
        "reason_code"
    ]
    
    # ======================================
    # TAMBAHKAN SUMBER
    # ======================================
    #
    # Sumber diambil dari chunk dengan
    # similarity score tertinggi.
    #

    if (
        result["reason_code"] == "answered"
        and data["results"]
    ):

        source = data["results"][0]

        source_text = (
            f"\n\nSumber: "
            f"{source['chunk_id']} - "
            f"{source['section_title']}"
        )

        result["answer"] += source_text

    return result


# ==========================================
# MAIN / TEST
# ==========================================

if __name__ == "__main__":

    print("=" * 60)
    print("NUSANTARACARE RAG AGENT")
    print("=" * 60)

    question = input(
        "\nMasukkan pertanyaan: "
    )

    print("\n")
    print("=" * 60)
    print("MEMPROSES PERTANYAAN")
    print("=" * 60)

    print(
        f"Pertanyaan: {question}"
    )

    try:

        result = answer_question(
            question
        )

        print("\n")
        print("=" * 60)
        print("FINAL RESPONSE")
        print("=" * 60)

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2
            )
        )

    except Exception as e:

        print("\n")
        print("=" * 60)
        print("ERROR")
        print("=" * 60)

        print(
            f"{type(e).__name__}: {e}"
        )