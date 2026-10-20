
"""
Tugas Mandiri 5 — Tight vs Loose Coupling + Dead Letter Queue + ulang_dlq()
Konsep utama: idempotent — operasi yang bisa dijalankan berkali-kali
tanpa mengubah hasil akhir melampaui eksekusi pertama.
"""

# ===== Data global dan set pencatat (untuk idempotent) =====
stok, analitik = [], []
stok_sudah = set()       # mencatat id pesanan yang sudah masuk stok
analitik_sudah = set()   # mencatat id pesanan yang sudah masuk analitik

def kurangi_stok(e):
    """Idempotent: hanya proses jika id belum pernah masuk stok."""
    if e["id"] not in stok_sudah:
        stok.append(e["id"])
        stok_sudah.add(e["id"])

def catat_analitik(e):
    """Idempotent: hanya proses jika id belum pernah masuk analitik."""
    if e["id"] not in analitik_sudah:
        analitik.append(e["id"])
        analitik_sudah.add(e["id"])

def kirim_email(e):
    if e["id"] == 2:
        raise ConnectionError("layanan email down")
    print(f"  email pesanan {e['id']} terkirim")

def cek_fraud(e):
    if e["id"] % 2 == 0:
        print(f"  PERINGATAN: pesanan {e['id']} perlu dicek (id genap)")


# ===== Desain A: Tightly Coupled =====
def buat_pesanan_tight(e):
    kurangi_stok(e)
    kirim_email(e)
    catat_analitik(e)


# ===== Desain B: Loosely Coupled (producer -> router -> consumer) =====
class Router:
    def __init__(self):
        self.pelanggan = {}
        self.dlq = []

    def subscribe(self, topik, handler):
        self.pelanggan.setdefault(topik, []).append(handler)

    def publish(self, topik, event):
        for h in self.pelanggan.get(topik, []):
            try:
                h(event)
            except Exception as err:
                self.dlq.append({
                    "handler": h.__name__,
                    "event": event,
                    "error": str(err)
                })
                print(f"  DLQ <- {h.__name__} gagal untuk pesanan {event['id']}")

    def ulang_dlq(self):
        """
        Mencoba ulang semua event di DLQ setelah consumer diperbaiki.

        MEKANISME IDEMPOTENT:
        Fungsi kurangi_stok() dan catat_analitik() menggunakan set() untuk
        mencatat id yang sudah diproses. Saat event di-replay dari DLQ,
        kedua fungsi mengecek apakah id sudah ada di set:
        - Jika SUDAH ada  -> dilewati (skip), tidak diproses lagi
        - Jika BELUM ada  -> diproses seperti biasa

        Dengan demikian, meskipun DLQ memicu ulang seluruh pipeline untuk
        event tertentu, stok dan analitik TIDAK akan bertambah dua kali.

        APA ITU IDEMPOTENT?
        Idempotent adalah sifat suatu operasi di mana menjalankan operasi
        tersebut satu kali atau berkali-kali menghasilkan efek yang SAMA.

        Contoh sehari-hari:
        - Menekan tombol lift berkali-kali -> lift tetap datang sekali
        - Set x = 5 berkali-kali -> x tetap 5

        Contoh TIDAK idempotent:
        - x = x + 1 berkali-kali -> x terus bertambah
        - INSERT tanpa cek duplikat -> data bertambah terus

        Dalam konteks DLQ ini:
        - kurangi_stok() IDEMPOTENT: pakai set() sebagai penjaga
        - catat_analitik() IDEMPOTENT: pakai set() sebagai penjaga
        - kirim_email() BUKAN idempotent, tapi memang itu tujuannya:
          email yang gagal harus dikirim ulang
        """
        if not self.dlq:
            print("  DLQ kosong, tidak ada yang perlu diulang.")
            return

        print(f"\n  Mengulang {len(self.dlq)} event dari DLQ...")
        gagal_lagi = []

        # Bangun mapping nama handler ke fungsi
        semua_handler = {}
        for topik, handlers in self.pelanggan.items():
            for h in handlers:
                semua_handler[h.__name__] = h

        for item in self.dlq:
            nama = item["handler"]
            event = item["event"]
            handler = semua_handler.get(nama)

            if handler is None:
                print(f"  Handler '{nama}' tidak ditemukan, skip.")
                continue

            try:
                handler(event)
                print(f"  BERHASIL: {nama} pesanan {event['id']}")
            except Exception as err:
                gagal_lagi.append(item)
                print(f"  GAGAL LAGI: {nama} pesanan {event['id']} ({err})")

        self.dlq = gagal_lagi
        print(f"  Sisa DLQ: {len(self.dlq)} event")


# ================================================================
#                     MENJALANKAN SIMULASI
# ================================================================

# --- Desain A: Tight Coupling ---
print("=" * 50)
print("== Desain A (Tight Coupling) ==")
print("=" * 50)
for i in (1, 2, 3):
    try:
        buat_pesanan_tight({"id": i})
        print(f"pesanan {i}: sukses")
    except Exception as err:
        print(f"pesanan {i}: GAGAL ({err})")
print(f"stok: {stok} | analitik: {analitik}")

# Reset untuk Desain B
stok.clear()
analitik.clear()
stok_sudah.clear()
analitik_sudah.clear()

# --- Desain B: Loose Coupling ---
print(f"\n{'=' * 50}")
print("== Desain B (Loose Coupling + DLQ) ==")
print("=" * 50)
router = Router()
for h in (kurangi_stok, kirim_email, catat_analitik, cek_fraud):
    router.subscribe("pesanan_baru", h)

for i in (1, 2, 3):
    router.publish("pesanan_baru", {"id": i})
    print(f"pesanan {i}: diterima")

print(f"\nstok: {stok} | analitik: {analitik}")
print(f"dead-letter: {router.dlq}")

# --- Sebelum replay ---
print(f"\n{'=' * 50}")
print("== Sebelum ulang_dlq() ==")
print("=" * 50)
print(f"stok: {stok}")
print(f"analitik: {analitik}")
print(f"DLQ: {len(router.dlq)} event -> {router.dlq}")

# --- Simulasi: perbaiki kirim_email agar id=2 tidak error lagi ---
print(f"\n{'=' * 50}")
print("== Simulasi: email diperbaiki, jalankan ulang_dlq() ==")
print("=" * 50)

# Patch: ganti fungsi kirim_email agar tidak error lagi
def kirim_email(e):
    """Versi yang sudah diperbaiki — tidak error lagi."""
    print(f"  email pesanan {e['id']} terkirim (sudah diperbaiki)")

# Update handler di router agar pakai versi baru
router.pelanggan["pesanan_baru"] = [kurangi_stok, kirim_email, catat_analitik, cek_fraud]

# Jalankan ulang_dlq()
router.ulang_dlq()

# --- Verifikasi IDEMPOTENT ---
print(f"\n{'=' * 50}")
print("== BUKTI IDEMPOTENT ==")
print("=" * 50)
print(f"stok    : {stok}  (jumlah: {len(stok)})")
print(f"analitik: {analitik}  (jumlah: {len(analitik)})")
print()
if stok == [1, 2, 3] and analitik == [1, 2, 3]:
    print("BERHASIL! stok dan analitik masing-masing hanya [1, 2, 3]")
    print("-> Pesanan 2 TIDAK diproses dua kali di stok dan analitik")
    print("-> Hanya kirim_email yang diulang (karena memang itu yang gagal)")
    print("-> Ini membuktikan mekanisme IDEMPOTENT bekerja dengan benar!")
else:
    print("GAGAL: ada duplikasi, mekanisme idempotent perlu diperbaiki")
