# Pemetaan Peran - Batik Kinanthi

| No | Kebutuhan Pemilik Batik Kinanthi | Peran Utama | Alasan Singkat | Tahap Lifecycle |
|----|----------------------------------|-------------|----------------|-----------------|
| 1 | Data penjualan dari toko, web, dan marketplace dikumpulkan ke satu tempat setiap malam | Data Engineer | Memindahkan dan menyatukan data dari banyak sumber secara otomatis | Ingestion |
| 2 | Dashboard omzet harian per kanal | Data Analyst | Membuat visualisasi data penjualan untuk monitoring bisnis harian | Serving |
| 3 | Prediksi kebutuhan stok kain bulan depan | Data Scientist | Membangun model prediksi berdasarkan data historis penjualan | Serving (ML) |
| 4 | Tabel pelanggan tidak boleh berisi data ganda | Data Engineer | Menjaga kualitas data dengan deduplikasi di pipeline | Storage |
| 5 | Laporan motif terlaris per kota untuk rapat bulanan | Data Analyst | Menganalisis dan menyajikan insight penjualan per wilayah | Serving |
| 6 | Rekomendasi produk untuk pelanggan di situs web | Data Scientist | Membangun sistem rekomendasi menggunakan algoritma ML | Serving (ML) |
| 7 | Data transaksi lama tetap tersimpan aman dan hemat biaya | Data Engineer | Merancang arsitektur penyimpanan dengan strategi tiering (hot/cold storage) | Storage |
| 8 | Analisis penyebab penurunan penjualan marketplace bulan lalu | Data Analyst | Investigasi data untuk menemukan faktor penurunan dan menyajikan insight | Serving |

## Pertanyaan: Dependensi Antar Peran

Data Analyst dan Data Scientist sangat bergantung pada Data Engineer. Tanpa pipeline yang andal dari Data Engineer, data tidak akan tersedia atau tidak bersih untuk dianalisis oleh Data Analyst maupun digunakan untuk melatih model oleh Data Scientist. Ketiga peran ini membentuk rantai ketergantungan: DE menyiapkan data di hulu, DA dan DS memanfaatkan data di hilir.
