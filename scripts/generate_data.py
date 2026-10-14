"""Generate data sintetis Batik Kinanthi."""
import os, random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
fake = Faker("id_ID")
random.seed(42)
Faker.seed(42)

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}"
    f"/{os.getenv('DB_NAME')}"
)
engine = create_engine(DB_URL)

# --- 1. Tabel Pelanggan (500 baris) ---
kota_list = ["Surakarta", "Yogyakarta", "Semarang", "Jakarta", "Surabaya",
             "Bandung", "Malang", "Denpasar", "Medan", "Makassar"]
pelanggan = pd.DataFrame({
    "id_pelanggan": range(1, 501),
    "nama": [fake.name() for _ in range(500)],
    "kota": [random.choice(kota_list) for _ in range(500)],
    "tanggal_daftar": [fake.date_between(start_date="-2y", end_date="today")
                       for _ in range(500)]
})

# --- 2. Tabel Produk (60 baris) ---
motif = ["Parang", "Kawung", "Mega Mendung", "Truntum", "Sekar Jagad",
         "Sogan", "Sidomukti", "Ceplok", "Gringsing", "Tambal"]
kategori = ["Kain", "Kemeja", "Dress", "Syal", "Taplak", "Tas"]
produk = pd.DataFrame({
    "id_produk": range(1, 61),
    "nama": [f"{random.choice(motif)} - {random.choice(kategori)} {i}"
             for i in range(1, 61)],
    "kategori": [random.choice(kategori) for _ in range(60)],
    "harga": [random.randint(50, 500) * 1000 for _ in range(60)]
})

# Buat dictionary harga agar lebih cepat dan tidak error
harga_dict = dict(zip(produk["id_produk"], produk["harga"]))

# --- 3. Tabel Transaksi (5000 baris) ---
kanal_list = ["toko", "web", "marketplace"]
kanal_bobot = [0.4, 0.35, 0.25]
start_date = datetime(2024, 1, 1)
transaksi_rows = []
for i in range(1, 5001):
    tgl = start_date + timedelta(days=random.randint(0, 364))
    kanal = random.choices(kanal_list, weights=kanal_bobot, k=1)
    transaksi_rows.append({
        "id_transaksi": i,
        "id_pelanggan": random.randint(1, 500),
        "tanggal": tgl.date(),
        "kanal": kanal,
        "total": 0
    })
transaksi = pd.DataFrame(transaksi_rows)

# --- 4. Tabel Detail Transaksi ---
detail_rows = []
detail_id = 1
total_per_transaksi = {}

for i in range(1, 5001):
    n_item = random.randint(1, 5)
    total_trx = 0
    produk_sample = random.sample(range(1, 61), n_item)
    for pid in produk_sample:
        jumlah = random.randint(1, 3)
        harga_satuan = harga_dict[pid]
        subtotal = jumlah * harga_satuan
        total_trx += subtotal
        detail_rows.append({
            "id_detail": detail_id,
            "id_transaksi": i,
            "id_produk": pid,
            "jumlah": jumlah,
            "harga_satuan": harga_satuan,
            "subtotal": subtotal
        })
        detail_id += 1
    total_per_transaksi[i] = total_trx

transaksi["total"] = transaksi["id_transaksi"].map(total_per_transaksi)
detail_transaksi = pd.DataFrame(detail_rows)

# --- Tulis ke PostgreSQL ---
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS detail_transaksi CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS transaksi CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS produk CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS pelanggan CASCADE"))

pelanggan.to_sql("pelanggan", engine, if_exists="replace", index=False)
produk.to_sql("produk", engine, if_exists="replace", index=False)
transaksi.to_sql("transaksi", engine, if_exists="replace", index=False)
detail_transaksi.to_sql("detail_transaksi", engine, if_exists="replace", index=False)

print("Data berhasil dibuat:")
print(f"   Pelanggan       : {len(pelanggan)} baris")
print(f"   Produk          : {len(produk)} baris")
print(f"   Transaksi       : {len(transaksi)} baris")
print(f"   Detail Transaksi: {len(detail_transaksi)} baris")
