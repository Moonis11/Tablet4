from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal, Dict
import streamlit as st

def _to_int(val: Decimal, rounding_100: bool = False) -> int:
    if rounding_100:
        val = (val / 100).to_integral_value(ROUND_HALF_UP) * 100
    return int(val)

def format_narx(narx: int) -> str:
    return f"{narx:,}"





def foydalanuvchi_uchun_narx(
    masofa_km: float,
    soat: int | None = None,
    kun_turi: Literal["ish kuni", "dam olish"] = "ish kuni",
    yomgir: bool = False,
    ogirlik_kg: float = 0,
    yuk_kategoriya: Literal["kichik", "orta", "katta"] = "kichik",
    rounding_100: bool = False,
) -> Dict[str, int | float | str]:


    soat = soat if soat is not None else datetime.now().hour
    soat = min(max(soat, 0), 23)

    # Masofaga qarab xavfsizlik foizini belgilash
    if masofa_km <= 1.5:
        xavfsizlik_foizi = Decimal("0.50")   # 50%
    elif masofa_km <= 11:
        xavfsizlik_foizi = Decimal("0.12")   # 12%
    else:
        xavfsizlik_foizi = Decimal("0.10")   # 10%

    bazaviy = Decimal("12000") if masofa_km <= 11 else Decimal("10000")
    km_rate = Decimal("2500")

    km_bonus = Decimal(str(masofa_km)) * km_rate
    pik_bonus = Decimal("12000") if (7 <= soat <= 10) or (13 <= soat <= 14) or (17 <= soat <= 20) else Decimal("0")
    dam_bonus = Decimal("5000") if kun_turi == "dam olish" else Decimal("0")
    rain_bonus = Decimal("5000") if yomgir else Decimal("0")
    weight_bonus = Decimal(max(0, ogirlik_kg - 5)) * Decimal("1000")
    size_bonus = {"kichik": Decimal("0"), "orta": Decimal("3000"), "katta": Decimal("6000")}[yuk_kategoriya]

    total_asosiy = bazaviy + km_bonus + pik_bonus + dam_bonus + rain_bonus + weight_bonus + size_bonus

    soliq_foizi = Decimal("0.04")
    payme_foizi = Decimal("0.015")

    xavfsizlik = total_asosiy * xavfsizlik_foizi
    soliq = total_asosiy * soliq_foizi
    payme = total_asosiy * payme_foizi

    total = total_asosiy + xavfsizlik + soliq + payme

    foydalanuvchiga_narx_int = _to_int(total, rounding_100)

    return {
        "bazaviy_narx": _to_int(bazaviy, rounding_100),
        "km_bonus": _to_int(km_bonus, rounding_100),
        "pik_bonus": _to_int(pik_bonus, rounding_100),
        "dam_olish_bonus": _to_int(dam_bonus, rounding_100),
        "yomgir_bonus": _to_int(rain_bonus, rounding_100),
        "ogirlik_bonus": _to_int(weight_bonus, rounding_100),
        "yuk_bonus": _to_int(size_bonus, rounding_100),
        "asosiy_narx": _to_int(total_asosiy, rounding_100),
        "xavfsizlik_zaxirasi": _to_int(xavfsizlik, rounding_100),
        "soliq": _to_int(soliq, rounding_100),
        "payme_komissiya": _to_int(payme, rounding_100),
        "foydalanuvchiga_narx": foydalanuvchiga_narx_int,
        "foydalanuvchiga_narx_str": format_narx(foydalanuvchiga_narx_int),
        "jami_foiz": float(round(xavfsizlik_foizi + soliq_foizi + payme_foizi, 3))
    }
