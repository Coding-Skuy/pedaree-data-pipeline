# ADR-0001 — Fondasi teknis pedaree-data-pipeline

Status: Diterima | Tanggal: 2026-10-14

## Konteks

Template pipeline memakai topik Kafka dan webhook `/sinyal-permintaan`, tidak selaras dengan penerima TitipO `POST /sinyal/pedaree-stok`. Sumber kebenaran: Pedaree-TownHall `platform/versions/v1.0.0` (https://github.com/Coding-Skuy/Pedaree-TownHall/tree/main/platform/versions/v1.0.0), beku 2026-10-07; lintas divisi: [KONTEKS-LINTAS-DIVISI.md](https://github.com/Coding-Skuy/ChefGenie-TownHall/blob/main/KONTEKS-LINTAS-DIVISI.md). Tiket fondasi: PDR-DATA-001 (issue #1).

## Keputusan

1. Python + pydantic untuk pipa; pengiriman ke TitipO lewat HTTP `POST /sinyal/pedaree-stok` dengan `X-Service-Key` (bukan webhook `/sinyal-permintaan`).
2. Kontrak bilateral `pedaree.stok.v1`: 3 jenis, payload `item/sisa/satuan/kedaluwarsa/recipe_id`, kunci idempoten konsumen `item_id + tanggal`, relevansi 48 jam.
3. Dedup produsen maks 1 sinyal per item per 24 jam (BR-301); retry 3× lalu DLQ.
4. `pedaree.stok.v1` bukan bagian registry 11 event Titeny; jalur evolusi event ke-12 bila Titeny butuh (KONTEKS §3.1).
5. DB per service: pipa hanya membaca DB `pedaree` dan tidak menulis ke DB divisi lain.

## Konsekuensi

- Dependensi Kafka (`confluent-kafka`) ditinjau ulang; transportasi dipilih lewat ADR setelah penerima TitipO dipastikan HTTP.
- Perubahan payload memerlukan bump versi + dual-read 30 hari bersama TitipO.
- Agregat metrik menjadi sumber angka dasbor web.
