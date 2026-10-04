# Arsitektur pedaree-data-pipeline

TownHall: https://github.com/Coding-Skuy/Pedaree-TownHall

## Lapisan

1. Produsen: backend menerbitkan `PantryStockEvent` ke `pedaree.stok.v1`.
2. Pekerja: `src/pekerja_sinyal.py` memakai aturan ambang (stok di bawah
   batas, kedaluwarsa kurang dari 3 hari).
3. Penyalur: sinyal `DemandSignal` dikirim ke webhook TitipO.

## Skema event

```json
{
  "event": "stok.menipis",
  "item": "minyak goreng",
  "sisa": 200,
  "satuan": "ml",
  "kedaluwarsa": "2026-11-20",
  "recipe_id": "pawonee-resep-ayam-goreng-001"
}
```

## Keputusan

- Kafka 3.9.0 sebagai tulang punggung event; pekerja Python tanpa status.
- Sinyal bersifat anjuran; TitipO memutuskan penawaran akhir ke pengguna.
