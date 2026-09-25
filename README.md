# Asisten Sejalan: Asisten Tanya Jawab Barang Berbasis RAG

Asisten yang menjawab pertanyaan pembeli tentang material elektrikal dan baja industri
di toko Sejalan (Sejalan Elektrik dan Sejalan Baja). Jawaban disusun oleh model AI
**hanya berdasarkan data barang toko**, sehingga AI tidak mengarang barang atau spesifikasi.

Dibuat oleh Dibuat oleh **Hilman Yazid Vasla**.

## Masalah bisnis yang diselesaikan

Pembeli material industri sering bertanya dengan bahasa sehari-hari, misalnya
"kabel buat mesin yang sering dipindah", bukan dengan nama teknis barang.
Asisten ini menerjemahkan kebutuhan pembeli menjadi saran barang yang tepat,
lengkap dengan alasannya.

## Cara kerja (RAG)

1. **Data**: keterangan 20 barang disimpan di `data/data_barang.xlsx`.
2. **Pencarian gabungan (hybrid search)**:
   - *Pencarian makna*: setiap keterangan barang diubah menjadi vektor (deretan angka
     yang mewakili makna) dengan model `intfloat/multilingual-e5-small`.
   - *Pencocokan kata*: menghitung berapa banyak kata pertanyaan yang muncul di keterangan barang.
   - Skor akhir = skor makna + 0,1 × skor kata. Tiga barang dengan skor tertinggi dipilih.
3. **Penyusunan jawaban**: keterangan tiga barang itu dikirim ke Google Gemini bersama
   pertanyaan, dengan aturan (*prompt*) agar menjawab hanya dari data, jujur bila barang
   tidak tersedia, dan tidak menyebut harga.
4. **Model cadangan**: bila satu model Gemini sedang penuh, program otomatis mencoba model berikutnya.

## Temuan selama pengembangan

- Pencarian makna saja gagal menemukan kabel yang tepat untuk pertanyaan
  "kabel buat mesin yang sering dipindah", karena kata "kabel" muncul di banyak barang.
- Setelah ditambah pencocokan kata (*hybrid search*), barang yang tepat
  (Kabel Titanex H07RN-F) naik ke urutan pertama.

| Pertanyaan | Hasil |
|---|---|
| kabel buat mesin yang sering dipindah | Kabel Titanex H07RN-F |
| baut yang nggak gampang karatan | Baut dan mur SUS |
| tempat naruh kabel biar rapi | Cable tray |
| ada jual lampu LED? | Dijawab jujur: belum tercatat di data |

## Teknologi

Python, pandas, sentence-transformers, Google Gemini API (`google-genai`).

## Cara menjalankan

1. Buat virtual environment dan pasang pustaka:
```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
```
2. Buat kunci API di Google AI Studio, lalu simpan sebagai variabel lingkungan:
```
   setx GEMINI_API_KEY "KUNCI_ANDA"
```
3. Buka jendela Command Prompt baru, aktifkan lagi `.venv`, lalu jalankan:
```
   python tanya.py
```
   Untuk menguji bagian pencarian saja: `python cari.py`.

## Catatan data

Data barang adalah contoh untuk keperluan portofolio. Ukuran yang tercantum adalah ukuran
umum di pasaran, bukan data stok. Harga sengaja tidak dicantumkan.

## Rencana pengembangan

- Tampilan web sederhana agar bisa dipakai lewat browser.
- Menyimpan vektor ke basis data agar tidak dihitung ulang setiap kali program dijalankan.
- Menambah dokumen lain, seperti panduan pemasangan dan lembar spesifikasi pabrikan.
