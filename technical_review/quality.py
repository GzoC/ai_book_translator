import math
import re
from collections import Counter

NUMBER = re.compile(r"(?<![\w])[-+]?\d+(?:[.,]\d+)*(?:[eE][-+]?\d+)?")
UNIT = re.compile(
    r"(?<![A-Za-z])(?:kWh|kW|kV|mA|Hz|bar|MPa|Pa|mm|cm|rpm|Nm|ms|°C|V|A|W|m|s|%)(?![A-Za-z])"
)
GLOSSARY = {
    "circuit breaker": "interruptor automático",
    "pressure sensor": "sensor de presión",
    "rated voltage": "tensión nominal",
    "power supply": "fuente de alimentación",
}


def validate_bbox(bbox, width, height):
    if len(bbox) != 4 or not all(
        isinstance(v, (int, float)) and math.isfinite(v) for v in bbox
    ):
        raise ValueError("Missing or invalid bounding box")
    x0, y0, x1, y1 = bbox
    if not (0 <= x0 < x1 <= width + 0.01 and 0 <= y0 < y1 <= height + 0.01):
        raise ValueError("Bounding box outside page or empty")
    return [float(v) for v in bbox]


def check_translation(source, target, glossary=None):
    flags = []
    if not target.strip():
        flags.append("empty_translation")
    if Counter(NUMBER.findall(source)) != Counter(NUMBER.findall(target)):
        flags.append("number_mismatch")
    if Counter(UNIT.findall(source)) != Counter(UNIT.findall(target)):
        flags.append("unit_mismatch")
    for term, preferred in (GLOSSARY if glossary is None else glossary).items():
        if re.search(
            r"\b" + re.escape(term) + r"\b", source, re.IGNORECASE
        ) and not re.search(
            r"\b" + re.escape(preferred) + r"\b", target, re.IGNORECASE
        ):
            flags.append("glossary:" + term)
    return flags
