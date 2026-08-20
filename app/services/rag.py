from pathlib import Path
import re


# ==========================================
# KONFIGURASI DOKUMEN
# ==========================================

DOCUMENT_PATH = Path(
    "data/raw_docs/nusantaracare_panduan_operasional_internal_v2.md"
)


# ==========================================
# MEMBACA METADATA DOKUMEN
# ==========================================

def extract_metadata(text: str):
    metadata = {}

    # Ambil hanya bagian frontmatter YAML
    # yaitu teks di antara --- pertama dan --- kedua.
    frontmatter_match = re.search(
        r"^---\s*\n(.*?)\n---",
        text,
        re.MULTILINE | re.DOTALL
    )

    if not frontmatter_match:
        return metadata

    frontmatter = frontmatter_match.group(1)

    patterns = {
        "doc_id": r"^doc_id:\s*(.+)$",
        "doc_title": r"^doc_title:\s*(.+)$",
        "doc_version": r'^doc_version:\s*"?([^"]+)"?$',
        "effective_date": r"^effective_date:\s*(.+)$",
        "is_active": r"^is_active:\s*(true|false)$",
    }

    for key, pattern in patterns.items():

        match = re.search(
            pattern,
            frontmatter,
            re.MULTILINE | re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            if key == "is_active":
                value = value.lower() == "true"

            metadata[key] = value

    return metadata

# ==========================================
# CHUNKING DOKUMEN
# ==========================================

def create_chunks(text: str, chunk_size: int = 1200):

    # ==========================================
    # Hapus YAML frontmatter
    # ==========================================

    frontmatter_match = re.match(
        r"^---\s*\n.*?\n---\s*\n",
        text,
        re.DOTALL
    )

    if frontmatter_match:
        text = text[frontmatter_match.end():]

    # ==========================================
    # Daftar section utama resmi
    # ==========================================

    section_titles = {
        "Tujuan, Ruang Lingkup, dan Status Dokumen",
        "Istilah dan Peran",
        "Kanal Layanan dan Waktu Operasional",
        "Klasifikasi Permintaan dan Prioritas",
        "SOP Permintaan Akses dan Akun",
        "SOP Gangguan Layanan dan Eskalasi",
        "SOP Fasilitas dan Perlengkapan Kerja",
        "Kebijakan Data, Kerahasiaan, dan Batas Layanan",
        "Status Tiket, SLA, dan Komunikasi Pemohon",
        "FAQ Operasional",
        "Lampiran Matriks Keputusan",
        "Riwayat Perubahan dan Arsip Kebijakan",
    }

    # ==========================================
    # Daftar subsection
    # ==========================================

    subsection_titles = {
        "Definisi Istilah",
        "Peran dan Tanggung Jawab",
        "Saluran Resmi",
        "Waktu Operasional",
        "Prinsip Penetapan Prioritas",
        "Tingkat Prioritas",
        "Contoh Klasifikasi",
        "Input Wajib",
        "Langkah Service Desk",
        "Akses Sementara dan Pengakhiran Akses",
        "Larangan Kredensial",
        "Contoh Lengkap",
        "Pencatatan Insiden",
        "Alur Penanganan Berdasarkan Prioritas",
        "Batasan Komunikasi Waktu Pemulihan",
        "Kondisi Eskalasi",
        "Permintaan Standar",
        "Pengecualian Permintaan Hari yang Sama",
        "Pelaporan Peralatan Hilang atau Rusak",
        "Prinsip Data Minimum",
        "Data yang Dilarang dalam Tiket",
        "Permintaan Informasi Tiket Karyawan Lain",
        "Pelaporan Kecurigaan Keamanan",
        "Daftar Status Tiket dan Transisi",
        "Ketentuan Khusus Status Menunggu Pemohon",
        "Persyaratan Status Selesai",
        "Komunikasi Pemohon",
        "Pertanyaan Saluran Layanan",
        "Pertanyaan Prioritas dan SLA",
        "Pertanyaan Akses",
        "Pertanyaan Gangguan",
        "Pertanyaan Perlengkapan",
        "Pertanyaan Kerahasiaan",
        "Matriks Prioritas",
        "Matriks Pemilihan Jalur",
        "Arsip Kebijakan v1.4 — NONAKTIF",
        "Pengganti Aktif v2.0",
    }

    lines = text.splitlines()

    chunks = []

    current_section = None
    current_subsection = None
    current_text = ""

    chunk_number = 1

    # ==========================================
    # Simpan chunk
    # ==========================================

    def save_chunk():

        nonlocal current_text
        nonlocal chunk_number

        if not current_text.strip():
            return

        chunks.append({
            "chunk_id": f"NC-OPS-001-{chunk_number:03d}",
            "section_title": current_section,
            "subsection_title": current_subsection,
            "text": current_text.strip()
        })

        chunk_number += 1
        current_text = ""

    # ==========================================
    # Proses dokumen
    # ==========================================

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        # ======================================
        # Abaikan judul utama dokumen
        # ======================================

        if clean_line == "Panduan Operasional Layanan Internal NusantaraCare":
            continue

        # ======================================
        # Heading Markdown
        # ======================================

        heading_match = re.match(
            r"^(#{1,6})\s+(.+)$",
            clean_line
        )

        if heading_match:

            heading_text = heading_match.group(2).strip()

            # Section utama
            if (
                current_section == "Lampiran Matriks Keputusan"
                and heading_text in {
                    "SOP Permintaan Akses dan Akun",
                    "SOP Gangguan Layanan dan Eskalasi",
                    "SOP Fasilitas dan Perlengkapan Kerja",
                }
            ):

                if current_text:
                    current_text += "\n" + heading_text
                else:
                    current_text = heading_text

                continue

            save_chunk()

            current_section = heading_text
            current_subsection = None

            continue

            # ==================================
            # SUBSECTION
            # ==================================

            if heading_text in subsection_titles:

                save_chunk()

                current_subsection = heading_text

                continue

        # ======================================
        # Heading tanpa tanda #
        # ======================================

        # ======================================
        # Heading tanpa tanda #
        # ======================================

        if clean_line in section_titles:

            # Nama SOP di dalam Lampiran tetap
            # dianggap sebagai isi Lampiran.
            if (
                current_section == "Lampiran Matriks Keputusan"
                and clean_line in {
                    "SOP Permintaan Akses dan Akun",
                    "SOP Gangguan Layanan dan Eskalasi",
                    "SOP Fasilitas dan Perlengkapan Kerja",
                }
            ):

                if current_text:
                    current_text += "\n" + clean_line
                else:
                    current_text = clean_line

                continue

            save_chunk()

            current_section = clean_line
            current_subsection = None

            continue

         # ======================================
        # SUBSECTION tanpa tanda #
        # ======================================

        if clean_line in subsection_titles:

            save_chunk()

            current_subsection = clean_line

            continue

        # ======================================
        # Jangan membuat chunk sebelum
        # section pertama ditemukan
        # ======================================

        if current_section is None:
            continue

        # ======================================
        # Tambahkan teks
        # ======================================

        if current_text:
            current_text += "\n" + clean_line
        else:
            current_text = clean_line

        # ======================================
        # Pecah berdasarkan ukuran
        # ======================================

        if len(current_text) >= chunk_size:

            save_chunk()

    # ==========================================
    # Simpan chunk terakhir
    # ==========================================

    save_chunk()

    return chunks


# ==========================================
# LOAD KNOWLEDGE BASE
# ==========================================

def load_knowledge_base():

    if not DOCUMENT_PATH.exists():

        raise FileNotFoundError(
            f"Dokumen tidak ditemukan: {DOCUMENT_PATH}"
        )

    # Baca dokumen
    text = DOCUMENT_PATH.read_text(
        encoding="utf-8"
    )

    # Ambil metadata
    metadata = extract_metadata(text)

    # Buat chunk
    chunks = create_chunks(text)

    # Tambahkan metadata ke setiap chunk
    for chunk in chunks:

        chunk["doc_id"] = metadata.get(
            "doc_id",
            "NC-OPS-001"
        )

        chunk["doc_title"] = metadata.get(
            "doc_title",
            "Panduan Operasional Layanan Internal NusantaraCare"
        )

        chunk["doc_version"] = metadata.get(
            "doc_version",
            "2.0"
        )

        chunk["effective_date"] = metadata.get(
            "effective_date",
            "2026-07-01"
        )

        chunk["is_active"] = metadata.get(
            "is_active",
            True
        )

    return chunks


# ==========================================
# TEST KNOWLEDGE BASE
# ==========================================

if __name__ == "__main__":

    chunks = load_knowledge_base()

    print("=" * 60)
    print("KNOWLEDGE BASE BERHASIL DIMUAT")
    print("=" * 60)

    print(f"Jumlah chunk : {len(chunks)}")

    if chunks:

        # ==========================================
        # CONTOH CHUNK PERTAMA
        # ==========================================

        print("\nContoh chunk pertama:")
        print("-" * 60)

        print(f"Chunk ID       : {chunks[0]['chunk_id']}")
        print(f"Section        : {chunks[0]['section_title']}")
        print(
            f"Subsection     : "
            f"{chunks[0]['subsection_title'] or '-'}"
        )
        print(f"Doc ID         : {chunks[0]['doc_id']}")
        print(f"Doc Version    : {chunks[0]['doc_version']}")
        print(f"Is Active      : {chunks[0]['is_active']}")

        print("\nIsi:")
        print(chunks[0]["text"])

        # ==========================================
        # DAFTAR SECTION DAN SUBSECTION
        # ==========================================

        print("\n")
        print("=" * 60)
        print("DAFTAR SECTION DAN SUBSECTION")
        print("=" * 60)

        for chunk in chunks:

            subsection = chunk["subsection_title"]

            if subsection:

                print(
                    chunk["chunk_id"],
                    "->",
                    chunk["section_title"],
                    "->",
                    subsection
                )

            else:

                print(
                    chunk["chunk_id"],
                    "->",
                    chunk["section_title"]
                )

    else:

        print("\nPERINGATAN:")
        print("Tidak ada chunk yang berhasil dibuat.")