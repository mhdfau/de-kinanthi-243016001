# Reversibilitas Keputusan Arsitektur

| No | Keputusan | One-way / Two-way | Alasan | Cara Membuatnya Lebih Reversible |
|----|-----------|-------------------|--------|----------------------------------|
| 1 | Menyimpan seluruh data kampus dalam format tertutup milik satu vendor | One-way door | Data terkunci dalam format proprietary, migrasi ke format lain sangat mahal dan berisiko kehilangan data | Gunakan format terbuka seperti CSV, Parquet, atau JSON agar data bisa dibaca oleh tools apapun |
| 2 | Menulis ulang SIAKAD kampus sekaligus (big-bang rewrite) | One-way door | Jika gagal, tidak bisa kembali ke sistem lama karena sudah ditinggalkan sepenuhnya | Gunakan strangler pattern yaitu migrasi bertahap modul per modul sambil sistem lama masih berjalan |
| 3 | Menandatangani kontrak cloud 3 tahun dengan komitmen biaya | One-way door | Komitmen finansial jangka panjang yang sulit dibatalkan, vendor lock-in tinggi | Mulai dengan kontrak pendek (1 tahun) atau pay-as-you-go, evaluasi berkala sebelum komitmen panjang |
| 4 | Memilih Parquet sebagai format penyimpanan data analitik | Two-way door | Parquet adalah format terbuka, mudah dikonversi ke CSV, ORC, atau format lain kapan saja | Sudah cukup reversible karena formatnya terbuka dan banyak tools yang mendukung |

## Pertanyaan

### 1. Mengapa keputusan two-way door boleh diambil lebih cepat?
Karena jika ternyata salah, keputusan tersebut mudah diubah atau dibalik tanpa biaya besar dan tanpa dampak signifikan. Risiko rendah memungkinkan tim bergerak cepat tanpa harus analisis berlebihan.

### 2. Strangler pattern pada proyek brownfield termasuk strategi apa?
Strangler pattern adalah strategi untuk mengubah keputusan one-way door menjadi two-way door. Dengan migrasi bertahap, setiap langkah kecil bisa di-rollback secara independen tanpa mengganggu keseluruhan sistem.
