import re
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# 1. Baca data barang
df = pd.read_excel("data/data_barang.xlsx", sheet_name="barang").fillna("")
teks = (df["nama_barang"] + ". " + df["kategori"] + ". "
        + df["merek"] + ". " + df["keterangan"]).tolist()

# 2a. Pencarian makna: ubah teks barang menjadi deretan angka (vector)
model = SentenceTransformer("intfloat/multilingual-e5-small")
vektor_barang = model.encode(["passage: " + t for t in teks],
                             convert_to_tensor=True, normalize_embeddings=True)

# 2b. Pencocokan kata: simpan kumpulan kata dari setiap barang
def pecah_kata(kalimat):
    return set(re.findall(r"\w+", kalimat.lower()))

kata_barang = [pecah_kata(t) for t in teks]
BOBOT_KATA = 0.1   # seberapa besar pengaruh pencocokan kata

print("Siap. Ketik pertanyaan (tekan Enter tanpa isi untuk keluar).")

# 3. Cari 3 barang dengan skor gabungan tertinggi
while True:
    tanya = input("\nPertanyaan: ").strip()
    if not tanya:
        break

    vektor_tanya = model.encode("query: " + tanya,
                                convert_to_tensor=True, normalize_embeddings=True)
    skor_makna = util.cos_sim(vektor_tanya, vektor_barang)[0].cpu()

    kata_tanya = pecah_kata(tanya)
    skor_kata = torch.tensor([len(kata_tanya & k) / len(kata_tanya) for k in kata_barang])

    skor_akhir = skor_makna + BOBOT_KATA * skor_kata

    for i in skor_akhir.argsort(descending=True)[:3]:
        i = int(i)
        print(f"  {float(skor_akhir[i]):.2f}  (makna {float(skor_makna[i]):.2f}, "
              f"kata {float(skor_kata[i]):.2f})  {df['nama_barang'][i]}")