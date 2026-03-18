"""
hummingbird/logic/qr_generator.py
QR code generation per output tier.
URLs loaded from config/qr_urls.json.
"""

import io
import json
from pathlib import Path

import qrcode

CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_qr_urls() -> dict:
    with open(CONFIG_DIR / "qr_urls.json") as f:
        return json.load(f)


def generate_qr_bytes(tier: str) -> bytes:
    urls = _load_qr_urls()
    url = urls.get(tier, urls.get("default", "https://www.nhs.uk/conditions/bowel-cancer/"))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0E9B8A", back_color="#112233")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
