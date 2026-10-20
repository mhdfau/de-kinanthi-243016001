def hitung_skor(pola, bobot, skor):
    """Hitung skor total berbobot untuk setiap pola arsitektur."""
    hasil = {}
    for nama in pola:
        total = sum(bobot[k] * skor[nama][k] for k in bobot)
        hasil[nama] = round(total, 2)
    return hasil

def cetak_matriks(pola, kriteria, bobot, skor, hasil, judul="UTAMA"):
    """Cetak matriks keputusan dalam format tabel."""
    print(f"\n{'=' * 90}")
    print(f"  MATRIKS KEPUTUSAN BERBOBOT — {judul}")
    print(f"  Konteks: Batik Kinanthi (UMKM, 3 kanal, tim kecil)")
    print(f"{'=' * 90}")

    # Header
    header = f"{'Kriteria':<22} {'Bobot':<8}"
    for nama in pola:
        header += f" {nama:<14}"
    print(header)
    print("-" * 90)

    # Baris per kriteria
    for k in kriteria:
        baris = f"{k:<22} {bobot[k]:<8.0%}"
        for nama in pola:
            baris += f" {skor[nama][k]:<14}"
        print(baris)

    # Skor berbobot
    print("-" * 90)
    baris_skor = f"{'SKOR TOTAL':<22} {'':8}"
    for nama in pola:
        baris_skor += f" {hasil[nama]:<14.2f}"
    print(baris_skor)

    # Ranking
    ranking = sorted(hasil.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  RANKING:")
    for i, (nama, s) in enumerate(ranking, 1):
        medal = ["🥇", "🥈", "🥉", "4.", "5."][i-1]
        print(f"    {medal} {nama}: {s:.2f}")

    return ranking

def main():
    # === Definisi ===
    pola = ["Warehouse", "Lakehouse", "Modern DS", "Lambda/Kappa", "Data Mesh"]

    kriteria = [
        "biaya",         # biaya implementasi dan operasional
        "kompleksitas",  # kemudahan implementasi dan maintenance
        "skalabilitas",  # kemampuan menangani pertumbuhan data
        "real_time",     # kemampuan proses data real-time/streaming
        "tim_kecil",     # kesesuaian untuk tim kecil (UMKM)
    ]

    # Bobot utama (konteks UMKM Batik Kinanthi)
    bobot_utama = {
        "biaya":        0.30,   # 30% - UMKM sangat sensitif biaya
        "kompleksitas": 0.25,   # 25% - tim kecil, harus sederhana
        "skalabilitas": 0.15,   # 15% - penting tapi belum prioritas
        "real_time":    0.10,   # 10% - nice to have, bukan keharusan
        "tim_kecil":    0.20,   # 20% - sangat relevan untuk UMKM
    }

    # Skor setiap pola (1-5, semakin tinggi semakin baik)
    # Perspektif: Batik Kinanthi, UMKM di Surakarta
    skor = {
        "Warehouse": {
            "biaya":        3,  # managed warehouse (BigQuery/Redshift) lumayan mahal
            "kompleksitas": 4,  # konsep matang, banyak dokumentasi
            "skalabilitas": 4,  # baik untuk analitik batch
            "real_time":    2,  # tidak dirancang untuk real-time
            "tim_kecil":    4,  # managed service, tim kecil bisa pakai
        },
        "Lakehouse": {
            "biaya":        3,  # perlu object storage + compute terpisah
            "kompleksitas": 3,  # konsep lebih baru, learning curve sedang
            "skalabilitas": 5,  # sangat skalabel (batch + streaming)
            "real_time":    4,  # Delta Lake/Iceberg mendukung streaming
            "tim_kecil":    2,  # butuh keahlian lebih banyak
        },
        "Modern DS": {
            "biaya":        4,  # banyak opsi open-source/SaaS terjangkau
            "kompleksitas": 5,  # tools plug-and-play (dbt, Airbyte, dsb)
            "skalabilitas": 3,  # bergantung pada tools yang dipilih
            "real_time":    2,  # umumnya batch-oriented
            "tim_kecil":    5,  # sangat cocok untuk tim kecil
        },
        "Lambda/Kappa": {
            "biaya":        2,  # harus maintain 2 layer (Lambda) atau Kafka
            "kompleksitas": 1,  # paling kompleks, butuh banyak komponen
            "skalabilitas": 5,  # dirancang untuk skala besar
            "real_time":    5,  # keunggulan utama: real-time processing
            "tim_kecil":    1,  # tidak cocok untuk tim kecil sama sekali
        },
        "Data Mesh": {
            "biaya":        2,  # butuh investasi besar di organisasi
            "kompleksitas": 2,  # perubahan organisasi + teknis
            "skalabilitas": 5,  # sangat skalabel secara organisasional
            "real_time":    3,  # tergantung implementasi tiap domain
            "tim_kecil":    1,  # butuh banyak tim domain-oriented
        },
    }

    # === Hitung dan cetak matriks utama ===
    hasil_utama = hitung_skor(pola, bobot_utama, skor)
    ranking_utama = cetak_matriks(pola, kriteria, bobot_utama, skor, hasil_utama, "UTAMA")

    # =============================================================
    #                  UJI SENSITIVITAS BOBOT
    # =============================================================
    print(f"\n\n{'#' * 90}")
    print(f"  UJI SENSITIVITAS BOBOT")
    print(f"  Tujuan: melihat apakah ranking berubah jika prioritas bisnis berubah")
    print(f"{'#' * 90}")

    skenario = {
        "Skenario 1: Fokus Hemat Biaya (UMKM baru mulai)": {
            "biaya":        0.45,
            "kompleksitas": 0.25,
            "skalabilitas": 0.05,
            "real_time":    0.05,
            "tim_kecil":    0.20,
        },
        "Skenario 2: Fokus Real-Time (flash sale marketplace)": {
            "biaya":        0.15,
            "kompleksitas": 0.15,
            "skalabilitas": 0.20,
            "real_time":    0.35,
            "tim_kecil":    0.15,
        },
        "Skenario 3: Fokus Skalabilitas (Kinanthi berkembang nasional)": {
            "biaya":        0.15,
            "kompleksitas": 0.15,
            "skalabilitas": 0.35,
            "real_time":    0.15,
            "tim_kecil":    0.20,
        },
        "Skenario 4: Bobot Merata (tanpa prioritas khusus)": {
            "biaya":        0.20,
            "kompleksitas": 0.20,
            "skalabilitas": 0.20,
            "real_time":    0.20,
            "tim_kecil":    0.20,
        },
    }

    ringkasan = {"UTAMA": ranking_utama[0][0]}

    for nama_skenario, bobot_alt in skenario.items():
        hasil_alt = hitung_skor(pola, bobot_alt, skor)
        ranking_alt = cetak_matriks(pola, kriteria, bobot_alt, skor, hasil_alt, nama_skenario)
        ringkasan[nama_skenario.split(":")[0]] = ranking_alt[0][0]

    # === Ringkasan sensitivitas ===
    print(f"\n\n{'=' * 90}")
    print("  RINGKASAN UJI SENSITIVITAS")
    print("=" * 90)
    print(f"\n{'Skenario':<50} {'Pemenang':<20}")
    print("-" * 70)
    for sk, pemenang in ringkasan.items():
        print(f"{sk:<50} {pemenang:<20}")

    # === Kesimpulan ===
    pemenang_list = list(ringkasan.values())
    paling_sering = max(set(pemenang_list), key=pemenang_list.count)
    frekuensi = pemenang_list.count(paling_sering)

    print(f"\n  KESIMPULAN SENSITIVITAS:")
    print(f"  '{paling_sering}' menang di {frekuensi}/{len(ringkasan)} skenario.")

    if frekuensi >= 3:
        print(f"  -> Keputusan ROBUST: '{paling_sering}' konsisten menang")
        print(f"     meskipun bobot diubah-ubah. Cocok untuk Batik Kinanthi.")
    else:
        print(f"  -> Keputusan SENSITIF terhadap bobot: pemenang berubah-ubah.")
        print(f"     Perlu diskusi lebih lanjut dengan stakeholder tentang prioritas.")

    print(f"\n  REKOMENDASI untuk Batik Kinanthi (UMKM, tim kecil, 3 kanal):")
    print(f"  Gunakan '{ranking_utama[0][0]}' karena:")
    print(f"  - Skor tertinggi ({ranking_utama[0][1]:.2f}) dengan bobot UMKM")
    print(f"  - Sesuai dengan keterbatasan tim dan anggaran")
    print(f"  - Bisa di-upgrade ke arsitektur lain jika bisnis berkembang")
    print(f"    (ini termasuk two-way door — mudah diubah)")

if __name__ == "__main__":
    main()

