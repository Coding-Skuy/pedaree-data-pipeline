> Versi: v1.0.0 | Status: disetujui | Menggantikan: -

# ARSITEKTUR-AI-DEV — Stack terkunci dan batas context (pedaree-data-pipeline)

Mengacu: Pedaree-TownHall `platform/versions/v1.0.0` (https://github.com/Coding-Skuy/Pedaree-TownHall/tree/main/platform/versions/v1.0.0), beku 2026-10-07. Dokumen ini MELENGKAPI `versions/v1.0.0/docs/40-TECHSTACK.md` dan `versions/v1.0.0/docs/60-BLAST-RADIUS.md` (keduanya beku v1.0.0 dan tidak diedit; isinya hanya ringkasan satu paragraf). Tidak menduplikasi BRD/PRD/FRD/FSD/SRS.

Baris Pedaree townhall-roadmap §2: point of concern "FEFO; stockout <8%; waste <1.500 g/Rp50.000/bln"; batas context "13 satuan baku; konsumen modul `pantry-resep` milik Pawonee". Rujukan lintas divisi: KONTEKS §3.1, §6, §8, §9.

## 1. Matriks stack

| Komponen | Kondisi saat ini (tercatat dari manifes/README) | Target terkunci v1.0.0 |
|---|---|---|
| Python | 3.12.8 | 3.12.x (pin eksak saat kickoff) |
| Transport | Kafka 3.9.0 + confluent-kafka 2.8.0 (topik `pedaree.stok.v1`) | HTTP `POST /sinyal/pedaree-stok` + `X-Service-Key`; keputusan broker di ADR baru |
| Penerima | webhook TitipO `/sinyal-permintaan` | TitipO `/sinyal/pedaree-stok` |
| HTTP klien | httpx 0.28.1 | httpx |
| DB | psycopg 3.2.4 (PostgreSQL 16.6) | psycopg 3.x, baca-saja ke DB `pedaree` |
| Skema | `schemas/event-stok-v1.json` (field `event`) | skema selaras payload TitipO (`jenis`, `item_id`, `tanggal`) |
| Lint/uji | ruff 0.8.9, pytest 8.3.4 | ruff + pytest |

## 2. Drift yang tercatat

- `schemas/event-stok-v1.json` memakai field `event` dan tidak memuat `item_id`/`tanggal` (kunci idempoten TitipO); diselaraskan lewat PDR-DATA-003.
- Jenis sinyal di skema sudah tiga (`stok.menipis`, `stok.habis`, `kedaluwarsa.dekat`) — sesuai kontrak.
- README mengarahkan ke webhook `/sinyal-permintaan`; penerima resmi TitipO adalah `POST /sinyal/pedaree-stok` (PDR-DATA-002).

## 3. Boleh disentuh repo ini

- `src/`, `schemas/`, konfigurasi jadwal pipa.
- Membaca DB `pedaree`; memanggil TitipO `POST /sinyal/pedaree-stok`.

## 4. Dilarang

- Menulis ke DB TitipO, Pawonee, atau divisi lain.
- Mengirim jenis sinyal di luar 3 jenis terkunci.
- Membuat atau mengonfirmasi pesanan TitipO.
- Menyentuh DB divisi lain (DB per service; Titeny hanya read-only ke DB sumber).
- Membuat pesanan TitipO otomatis dari sinyal stok (hanya anjuran, relevansi 48 jam).
- Mengubah modul `:shared:pantry-resep` (milik Pawonee), daftar 13 satuan, ambang kedaluwarsa, atau audiens JWT tanpa PR TownHall + ADR.

## 5. Kontrak yang diproduksi

- Sinyal `pedaree.stok.v1` ke TitipO (anjuran restock).
- Agregat stockoutRate, wasteGram, wasteRupiah, waktuMenipisKeHabis; event analitik `stok_menipis`, `stok_habis`, `buang_catat`, `sinyal_titipo`, `pakai_dari_resep`.

## 6. Kontrak yang dikonsumsi

- Event mutasi/stok dari `pedaree-backend-service`.
- Kontrak penerima TitipO (`titipo-backend-service/docs/api/openapi.yaml`).

## 7. Dampak bila berubah

- Perubahan payload atau dedup memengaruhi daftar saran di aplikasi vendor TitipO.
- Perubahan agregat memengaruhi dasbor web dan target metrik.

## Batasan

- Dokumen ini hanya mencatat stack dan batas; tidak mengubah manifes atau kode. Kondisi saat ini dicatat apa adanya.
- Versi dikunci eksak di manifes saat kickoff coding; perubahan dicatat lewat ADR baru.
- JWT audiens `pedaree`, DB logis `pedaree`, dan kepemilikan Pawonee atas `:shared:pantry-resep` tidak berubah oleh dokumen ini.
