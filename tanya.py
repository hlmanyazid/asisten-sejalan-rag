import re
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from google import genai
from google.genai import types

DAFTAR_MODEL = ["gemini-3.7-flash", "gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-lite-latest"]
JUMLAH_BARANG = 3
BOBOT_KATA = 0.1

# ---------- 1. Siapkan data dan pencarian ----------
df = pd.read_excel("data/data_barang.xlsx", sheet_name="barang").fillna("")
teks = (df["nama_barang"] + ". " + df["kategori"] + ". "
        + df["merek"] + ". " + df["keterangan"]).tolist()

model_cari = SentenceTransformer("intfloat/multilingual-e5-small")
vektor_barang = model_cari.encode(["passage: " + t for t in teks],
                                  convert_to_tensor=True, normalize_embeddings=True)

def pecah_kata(kalimat):
    return set(re.findall(r"\w+", kalimat.lower()))

kata_barang = [pecah_kata(t) for t in teks]

def cari_barang(tanya):
    vektor_tanya = model_cari.encode("query: " + tanya,
                                     convert_to_tensor=True, normalize_embeddings=True)
    skor_makna = util.cos_sim(vektor_tanya, vektor_barang)[0].cpu()
    kata_tanya = pecah_kata(tanya)
    skor_kata = torch.tensor([len(kata_tanya & k) / len(kata_tanya) for k in kata_barang])
    skor_akhir = skor_makna + BOBOT_KATA * skor_kata
    return [int(i) for i in skor_akhir.argsort(descending=True)[:JUMLAH_BARANG]]

# ---------- 2. Siapkan Gemini ----------
klien = genai.Client()

ATURAN = """Anda adalah asisten toko Sejalan, penyedia material elektrikal dan baja industri.
Jawab pertanyaan pembeli dalam bahasa Indonesia yang ramah, singkat, dan jelas.
Aturan:
1. Jawab HANYA berdasarkan DATA BARANG yang diberikan. Jangan menambah barang atau
   spesifikasi yang tidak tertulis di data.
2. Jika tidak ada barang yang cocok, katakan terus terang bahwa barang itu belum
   tercatat, lalu sarankan pembeli menghubungi toko.
3. Jangan menyebut harga. Untuk harga dan stok, arahkan pembeli menghubungi toko.
4. Sebutkan nama barang yang Anda sarankan beserta alasannya."""

def susun_jawaban(tanya, daftar_nomor):
    data = "\n".join(f"- {teks[i]}" for i in daftar_nomor)
    pesan = f"DATA BARANG:\n{data}\n\nPERTANYAAN PEMBELI:\n{tanya}"
    galat_terakhir = None
    for nama_model in DAFTAR_MODEL:
        try:
            hasil = klien.models.generate_content(
                model=nama_model,
                contents=pesan,
                config=types.GenerateContentConfig(system_instruction=ATURAN, temperature=0.2),
            )
            return hasil.text + f"\n\n[model: {nama_model}]"
        except Exception as galat:
            galat_terakhir = galat
            print(f"({nama_model} sedang penuh, mencoba model berikutnya...)")
    raise galat_terakhir

# ---------- 3. Tanya jawab ----------
print("Asisten Sejalan siap. Ketik pertanyaan (tekan Enter tanpa isi untuk keluar).")
while True:
    tanya = input("\nPertanyaan: ").strip()
    if not tanya:
        break
    nomor = cari_barang(tanya)
    try:
        print("\nJawaban:\n" + susun_jawaban(tanya, nomor))
    except Exception as galat:
        print("\nGemini sedang tidak bisa dihubungi. Coba lagi sebentar.")
        print("Rincian:", str(galat)[:200])
    print("\n(Sumber: " + ", ".join(df["nama_barang"][i] for i in nomor) + ")")