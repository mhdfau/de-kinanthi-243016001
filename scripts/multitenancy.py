import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}"
    f"/{os.getenv('DB_NAME')}"
)
engine = create_engine(DB_URL)

def buat_view_tenant():
    """
    Membuat 2 view tenant berdasarkan kanal penjualan.
    Setiap view hanya menampilkan transaksi milik kanal tertentu.

    Konsep Multitenancy:
    Multitenancy adalah arsitektur di mana satu sistem/database melayani
    banyak "tenant" (penyewa/pengguna) sekaligus, tapi setiap tenant
    hanya bisa melihat datanya sendiri.

    Implementasi di sini menggunakan "View-Based Row-Level Filtering":
    - Data fisik ada di satu tabel (transaksi)
    - Setiap tenant punya view yang hanya menampilkan barisnya
    - Tenant "toko" tidak bisa lihat data "marketplace", dan sebaliknya
    """
    with engine.begin() as conn:
        # View untuk tenant TOKO
        conn.execute(text("""
            CREATE OR REPLACE VIEW view_tenant_toko AS
            SELECT id_transaksi, id_pelanggan, tanggal, kanal, total
            FROM transaksi
            WHERE kanal = 'toko';
        """))

        # View untuk tenant MARKETPLACE
        conn.execute(text("""
            CREATE OR REPLACE VIEW view_tenant_marketplace AS
            SELECT id_transaksi, id_pelanggan, tanggal, kanal, total
            FROM transaksi
            WHERE kanal = 'marketplace';
        """))

    print("View tenant berhasil dibuat:")
    print("  - view_tenant_toko (hanya transaksi kanal 'toko')")
    print("  - view_tenant_marketplace (hanya transaksi kanal 'marketplace')")

def uji_kebocoran():
    """
    Fungsi uji kebocoran data antar tenant.

    Tujuan: memastikan tenant A tidak bisa melihat data tenant B.

    Mekanisme pengujian:
    1. Query view_tenant_toko -> hitung kanal unik -> harus hanya 'toko'
    2. Query view_tenant_marketplace -> hitung kanal unik -> harus hanya 'marketplace'
    3. Jika ada kanal lain muncul di view -> KEBOCORAN TERDETEKSI!
    """
    print(f"\n{'=' * 60}")
    print("  UJI KEBOCORAN DATA ANTAR TENANT")
    print("=" * 60)

    kebocoran = False

    # === Uji tenant TOKO ===
    df_toko = pd.read_sql("SELECT * FROM view_tenant_toko", engine)
    kanal_toko = df_toko["kanal"].unique().tolist()
    jumlah_toko = len(df_toko)

    print(f"\n[Tenant TOKO]")
    print(f"  Jumlah transaksi : {jumlah_toko}")
    print(f"  Kanal yang muncul: {kanal_toko}")

    if kanal_toko == ["toko"]:
        print(f"  Status: AMAN - hanya data 'toko' yang terlihat")
    else:
        print(f"  Status: KEBOCORAN TERDETEKSI!")
        print(f"  Kanal asing ditemukan: {[k for k in kanal_toko if k != 'toko']}")
        kebocoran = True

    # === Uji tenant MARKETPLACE ===
    df_mp = pd.read_sql("SELECT * FROM view_tenant_marketplace", engine)
    kanal_mp = df_mp["kanal"].unique().tolist()
    jumlah_mp = len(df_mp)

    print(f"\n[Tenant MARKETPLACE]")
    print(f"  Jumlah transaksi : {jumlah_mp}")
    print(f"  Kanal yang muncul: {kanal_mp}")

    if kanal_mp == ["marketplace"]:
        print(f"  Status: AMAN - hanya data 'marketplace' yang terlihat")
    else:
        print(f"  Status: KEBOCORAN TERDETEKSI!")
        print(f"  Kanal asing ditemukan: {[k for k in kanal_mp if k != 'marketplace']}")
        kebocoran = True

    # === Uji silang: pastikan tidak ada overlap ===
    id_toko = set(df_toko["id_transaksi"])
    id_mp = set(df_mp["id_transaksi"])
    overlap = id_toko & id_mp

    print(f"\n[Uji Silang]")
    print(f"  ID transaksi toko       : {jumlah_toko}")
    print(f"  ID transaksi marketplace: {jumlah_mp}")
    print(f"  ID yang overlap         : {len(overlap)}")

    if len(overlap) == 0:
        print(f"  Status: AMAN - tidak ada transaksi yang muncul di kedua tenant")
    else:
        print(f"  Status: KEBOCORAN! {len(overlap)} transaksi muncul di kedua view!")
        kebocoran = True

    # === Bandingkan dengan total data ===
    df_semua = pd.read_sql("SELECT COUNT(*) as total FROM transaksi", engine)
    total_semua = df_semua["total"].iloc[0]
    df_web = pd.read_sql(
        "SELECT COUNT(*) as total FROM transaksi WHERE kanal = 'web'", engine
    )
    total_web = df_web["total"].iloc[0]

    print(f"\n[Ringkasan]")
    print(f"  Total transaksi semua kanal : {total_semua}")
    print(f"  Tenant toko                 : {jumlah_toko}")
    print(f"  Tenant marketplace          : {jumlah_mp}")
    print(f"  Kanal web (bukan tenant)    : {total_web}")
    print(f"  Jumlah cek                  : {jumlah_toko + jumlah_mp + total_web} "
          f"(harus = {total_semua})")

    if jumlah_toko + jumlah_mp + total_web == total_semua:
        print(f"  Validasi: COCOK - semua transaksi terpartisi dengan benar")
    else:
        print(f"  Validasi: TIDAK COCOK - ada data hilang atau ganda!")

    # === Kesimpulan ===
    print(f"\n{'=' * 60}")
    if not kebocoran:
        print("  KESIMPULAN: TIDAK ADA KEBOCORAN DATA ANTAR TENANT")
        print("  View-based multitenancy bekerja dengan benar.")
    else:
        print("  KESIMPULAN: KEBOCORAN TERDETEKSI! Perlu perbaikan.")
    print("=" * 60)

if __name__ == "__main__":
    buat_view_tenant()
    uji_kebocoran()

