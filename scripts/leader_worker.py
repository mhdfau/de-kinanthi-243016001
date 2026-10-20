import time
import os
from concurrent.futures import ProcessPoolExecutor

TOTAL_ITERASI = 10_000_000

def pekerjaan_berat(n):
    """Simulasi CPU-bound: hitung jumlah kuadrat sebanyak n iterasi."""
    total = 0
    for i in range(n):
        total += i * i
    return total

def ukur_speedup(jumlah_worker):
    """Bagi pekerjaan ke sejumlah worker, ukur waktu eksekusi."""
    bagian = TOTAL_ITERASI // jumlah_worker
    sisa = TOTAL_ITERASI % jumlah_worker

    # Bagi iterasi ke setiap worker
    tugas = [bagian] * jumlah_worker
    tugas[-1] += sisa  # worker terakhir dapat sisa

    mulai = time.perf_counter()

    if jumlah_worker == 1:
        # Tanpa multiprocessing untuk baseline
        hasil = [pekerjaan_berat(tugas[0])]
    else:
        with ProcessPoolExecutor(max_workers=jumlah_worker) as executor:
            hasil = list(executor.map(pekerjaan_berat, tugas))

    selesai = time.perf_counter()
    waktu = selesai - mulai
    return waktu, sum(hasil)

def main():
    print("=" * 65)
    print("  LEADER-WORKER: ProcessPoolExecutor Speedup Benchmark")
    print(f"  Total iterasi: {TOTAL_ITERASI:,}")
    print(f"  CPU tersedia : {os.cpu_count()} core")
    print("=" * 65)

    daftar_worker = [1, 2, 4, 8]
    hasil = {}
    waktu_baseline = None

    print(f"\n{'Worker':<10} {'Waktu (s)':<15} {'Speedup':<12} {'Efisiensi':<12}")
    print("-" * 50)

    for w in daftar_worker:
        waktu, total = ukur_speedup(w)
        if w == 1:
            waktu_baseline = waktu
        speedup = waktu_baseline / waktu
        efisiensi = speedup / w * 100
        hasil[w] = {"waktu": waktu, "speedup": speedup, "efisiensi": efisiensi}
        print(f"{w:<10} {waktu:<15.3f} {speedup:<12.2f} {efisiensi:<11.1f}%")

    # === ANALISIS ===
    print(f"\n{'=' * 65}")
    print("  ANALISIS: Mengapa Percepatan TIDAK Linear?")
    print("=" * 65)
    print("""
1. OVERHEAD PROSES (Process Spawning)
   - Setiap worker adalah proses baru yang harus dibuat oleh OS.
   - Membuat proses butuh waktu: alokasi memori, duplikasi environment,
     inisialisasi Python interpreter di setiap proses.
   - Untuk 8 worker, overhead ini terjadi 8 kali.

2. OVERHEAD KOMUNIKASI (IPC - Inter-Process Communication)
   - Leader harus mengirim data tugas ke setiap worker (serialisasi).
   - Worker harus mengirim hasil kembali ke leader (deserialisasi).
   - Proses ini menggunakan pickle, yang memakan waktu CPU dan memori.

3. HUKUM AMDAHL (Amdahl's Law)
   - Tidak semua bagian program bisa diparalelkan.
   - Bagian serial: pembagian tugas, pengumpulan hasil, print output.
   - Jika 5% program bersifat serial, speedup maksimum = 1/0.05 = 20x,
     tidak peduli berapa banyak worker yang ditambahkan.
   - Rumus: Speedup = 1 / (S + P/N)
     S = fraksi serial, P = fraksi paralel, N = jumlah worker

4. RESOURCE CONTENTION (Persaingan Sumber Daya)
   - Semua worker berbagi CPU cache, bus memori, dan bandwidth I/O.
   - Jika jumlah worker > jumlah CPU core fisik, terjadi context switching
     yang justru memperlambat eksekusi.

5. GIL (Global Interpreter Lock) — TIDAK berlaku di sini
   - ProcessPoolExecutor menggunakan proses terpisah (bukan thread),
     sehingga GIL tidak menjadi hambatan.
   - Tapi jika kita menggunakan ThreadPoolExecutor, GIL akan membuat
     CPU-bound task tidak mendapat percepatan sama sekali.

KESIMPULAN:
   Speedup ideal (linear) = jumlah worker. Misal 4 worker -> 4x lebih cepat.
   Kenyataan: selalu kurang dari ideal karena overhead di atas.
   Efisiensi menurun seiring bertambahnya worker karena overhead
   tumbuh lebih cepat daripada keuntungan paralelisasi.
""")

if __name__ == "__main__":
    main()

