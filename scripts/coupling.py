stok, analitik = [], []

def kurangi_stok(e):    stok.append(e["id"])
def catat_analitik(e):  analitik.append(e["id"])
def kirim_email(e):
    if e["id"] == 2:
        raise ConnectionError("layanan email down")

# --- Desain A: tightly coupled ---
def buat_pesanan_tight(e):
    kurangi_stok(e); kirim_email(e); catat_analitik(e)

# --- Desain B: loosely coupled ---
class Router:
    def __init__(self):
        self.pelanggan, self.dlq = {}, []

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

router = Router()
for h in (kurangi_stok, kirim_email, catat_analitik):
    router.subscribe("pesanan_baru", h)

# Tambahan: consumer cek_fraud tanpa ubah producer
def cek_fraud(e):
    if e["id"] % 2 == 0:
        print(f"  PERINGATAN: pesanan {e['id']} perlu dicek (id genap)")
router.subscribe("pesanan_baru", cek_fraud)

print("== Desain A (Tight Coupling) ==")
for i in (1, 2, 3):
    try:
        buat_pesanan_tight({"id": i}); print(f"pesanan {i}: sukses")
    except Exception as err:
        print(f"pesanan {i}: GAGAL ({err})")
print("stok:", stok, "| analitik:", analitik)

stok.clear(); analitik.clear()

print("")
print("== Desain B (Loose Coupling + DLQ) ==")
for i in (1, 2, 3):
    router.publish("pesanan_baru", {"id": i}); print(f"pesanan {i}: diterima")
print("stok:", stok, "| analitik:", analitik)
print("dead-letter:", router.dlq)
