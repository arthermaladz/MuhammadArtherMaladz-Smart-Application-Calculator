"""Common offline unit conversions for the calculator."""

from __future__ import annotations

from decimal import Decimal


UNITS: dict[str, dict[str, Decimal]] = {
    "Panjang": {
        "mm": Decimal("0.001"), "cm": Decimal("0.01"), "m": Decimal(1),
        "km": Decimal(1000), "in": Decimal("0.0254"), "ft": Decimal("0.3048"),
        "mi": Decimal("1609.344"),
    },
    "Massa": {
        "mg": Decimal("0.000001"), "g": Decimal("0.001"), "kg": Decimal(1),
        "ton": Decimal(1000), "oz": Decimal("0.028349523125"), "lb": Decimal("0.45359237"),
    },
    "Volume": {
        "mL": Decimal("0.001"), "L": Decimal(1), "m³": Decimal(1000),
        "tsp": Decimal("0.00492892159375"), "cup": Decimal("0.24"), "gal (US)": Decimal("3.785411784"),
    },
    "Luas": {
        "cm²": Decimal("0.0001"), "m²": Decimal(1), "km²": Decimal(1_000_000),
        "ha": Decimal(10_000), "ft²": Decimal("0.09290304"), "acre": Decimal("4046.8564224"),
    },
    "Kecepatan": {
        "m/s": Decimal(1), "km/jam": Decimal(Decimal(1000) / Decimal(3600)),
        "mph": Decimal("0.44704"), "kn": Decimal("0.514444444444444444"),
    },
    "Waktu": {
        "ms": Decimal("0.001"), "detik": Decimal(1), "menit": Decimal(60),
        "jam": Decimal(3600), "hari": Decimal(86400),
    },
}


def convert(value: Decimal, category: str, from_unit: str, to_unit: str) -> Decimal:
    if category == "Suhu":
        return _convert_temperature(value, from_unit, to_unit)
    try:
        units = UNITS[category]
        return value * units[from_unit] / units[to_unit]
    except KeyError as error:
        raise ValueError("Kategori atau satuan tidak dikenal") from error


def _convert_temperature(value: Decimal, from_unit: str, to_unit: str) -> Decimal:
    to_celsius = {
        "°C": lambda x: x,
        "°F": lambda x: (x - 32) * Decimal(5) / Decimal(9),
        "K": lambda x: x - Decimal("273.15"),
    }
    from_celsius = {
        "°C": lambda x: x,
        "°F": lambda x: x * Decimal(9) / Decimal(5) + 32,
        "K": lambda x: x + Decimal("273.15"),
    }
    try:
        result = from_celsius[to_unit](to_celsius[from_unit](value))
    except KeyError as error:
        raise ValueError("Satuan suhu tidak dikenal") from error
    if to_unit == "K" and result < 0:
        raise ValueError("Suhu di bawah nol mutlak")
    return result


def categories() -> dict[str, list[str]]:
    result = {name: list(units) for name, units in UNITS.items()}
    result["Suhu"] = ["°C", "°F", "K"]
    return result
