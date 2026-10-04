# pedaree-data-pipeline — Event Stok menjadi Sinyal Permintaan TitipO

Divisi **Pedaree (Smart Pantry)**, org **Coding-Skuy**. Opsi A.

TownHall: https://github.com/Coding-Skuy/Pedaree-TownHall

## Ringkasan

Pipeline yang mengubah event stok Pedaree (stok menipis, kedaluwarsa dekat)
menjadi sinyal permintaan untuk TitipO (modul titip belanja). TitipO memakai
sinyal ini untuk menawarkan jasa titip belanja bahan pengganti.

## Modul pantry-resep

Kontrak lintas divisi (detail: `docs/MODUL-PANTRY-RESEP.md`):

- **Pemilik modul:** Pawonee.
- **Konsumen modul:** Pedaree (pipeline menyertakan `recipe_id` Pawonee pada
  sinyal agar TitipO tahu bahan pengganti dipakai untuk resep apa).
- Pipeline tidak mengubah definisi resep; hanya meneruskan rujukan.

## Aliran data

```text
backend pedaree (event mutasi_stok)
  -> topik kafka pedaree.stok.v1
  -> pekerja sinyal (python)
  -> webhook TitipO /sinyal-permintaan
```

## Teknologi (versi dikunci)

- Python 3.12.8
- Apache Kafka 3.9.0 (kompatibel Redpanda)
- confluent-kafka 2.8.0
- pydantic 2.10.6
- PostgreSQL 16.6 (sumber baca)

Lihat `requirements.txt` sebagai sumber kebenaran versi Python.

## Cara jalan

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.pekerja_sinyal
```

## CI

Workflow `.github/workflows/ci.yml` menjalankan lint dan uji skema event.
