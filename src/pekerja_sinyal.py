"""Pekerja sinyal: event stok Pedaree -> sinyal permintaan TitipO."""
from datetime import date

from pydantic import BaseModel


class EventStok(BaseModel):
    event: str
    item: str
    sisa: float
    satuan: str
    kedaluwarsa: date
    recipe_id: str | None = None


class SinyalPermintaan(BaseModel):
    item: str
    alasan: str
    recipe_id: str | None = None


BATAS_MENIPIS_ML = 250.0
HARI_SEGERA = 3


def ubah_jadi_sinyal(event: EventStok, hari_ini: date) -> SinyalPermintaan | None:
    sisa_hari = (event.kedaluwarsa - hari_ini).days
    if event.sisa <= 0:
        return SinyalPermintaan(item=event.item, alasan="habis", recipe_id=event.recipe_id)
    if event.sisa < BATAS_MENIPIS_ML:
        return SinyalPermintaan(item=event.item, alasan="menipis", recipe_id=event.recipe_id)
    if sisa_hari <= HARI_SEGERA:
        return SinyalPermintaan(
            item=event.item, alasan="kedaluwarsa-dekat", recipe_id=event.recipe_id
        )
    return None
