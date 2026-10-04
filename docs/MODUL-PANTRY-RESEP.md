# Modul pantry-resep — Kontrak Pawonee (pemilik) dan Pedaree (konsumen)

TownHall Pedaree: https://github.com/Coding-Skuy/Pedaree-TownHall

## Kedudukan

- **Pemilik:** Pawonee.
- **Konsumen:** Pedaree data-pipeline (meneruskan `recipe_id` ke sinyal TitipO).

## Aturan konsumen (berlaku untuk data-pipeline)

1. Setiap sinyal permintaan memuat `recipe_id` Pawonee bila pemicu berkaitan
   dengan resep (contoh: bahan resep favorit menipis).
2. Skema event `pedaree.stok.v1` mencantumkan `recipe_id` opsional.
3. Pipeline tidak mengubah definisi resep; hanya meneruskan rujukan ke TitipO.
4. Konsumen hilir (TitipO) memakai rujukan untuk menawarkan bahan pengganti
   yang sesuai resep.
