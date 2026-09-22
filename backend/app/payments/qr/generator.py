"""
QR Code Generator for Bolivia QR Simple format (EMVCo-like).
Generates QR codes compatible with Bolivian banking apps (BISA, BCP, etc.).
"""
from dataclasses import dataclass
from io import BytesIO

import crcmod
import qrcode


@dataclass
class QRStaticData:
    """Data for static QR (merchant info only, no amount)."""
    merchant_id: str
    merchant_name: str
    merchant_city: str
    account: str  # Bank account / QR ID
    currency: str = "BOB"
    country_code: str = "BO"


@dataclass
class QRDynamicData:
    """Data for dynamic QR (includes amount and reference)."""
    merchant_id: str
    merchant_name: str
    merchant_city: str
    account: str
    amount: float
    reference: str
    currency: str = "BOB"
    country_code: str = "BO"
    description: str = ""


class QRSimpleBolivia:
    """
    QR Simple Bolivia format (EMVCo-like).
    Based on Banco Central de Bolivia QR Simple specification.
    """

    # EMVCo Tag IDs
    TAG_PAYLOAD_FORMAT = "00"
    TAG_POI_METHOD = "01"
    TAG_MERCHANT_ACCOUNT = "26"  # Merchant Account Information
    TAG_MERCHANT_CATEGORY = "52"
    TAG_COUNTRY_CODE = "58"
    TAG_MERCHANT_NAME = "59"
    TAG_MERCHANT_CITY = "60"
    TAG_TRANSACTION_CURRENCY = "53"
    TAG_TRANSACTION_AMOUNT = "54"
    TAG_TIP_TYPE = "55"
    TAG_REFERENCE_LABEL = "61"
    TAG_ADDITIONAL_DATA = "62"
    TAG_CRC = "63"

    # Sub-tags for Merchant Account Information (26)
    SUB_TAG_GLOBALLY_UNIQUE = "00"  # AID
    SUB_TAG_MERCHANT_ID = "01"      # Merchant ID
    SUB_TAG_ACCOUNT = "02"          # Account/QR ID

    def __init__(self):
        self.crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)

    def _format_tlv(self, tag: str, value: str) -> str:
        """Format TLV (Tag-Length-Value) - Length is 2 digits."""
        length = f"{len(value):02d}"
        return f"{tag}{length}{value}"

    def _build_merchant_account(self, merchant_id: str, account: str) -> str:
        """Build Merchant Account Information (tag 26)."""
        parts = []
        # AID for Bolivia QR Simple (example: "PY.01" for Paraguay, "BO.01" for Bolivia)
        parts.append(self._format_tlv(self.SUB_TAG_GLOBALLY_UNIQUE, "BO.01"))
        parts.append(self._format_tlv(self.SUB_TAG_MERCHANT_ID, merchant_id))
        parts.append(self._format_tlv(self.SUB_TAG_ACCOUNT, account))
        merchant_account = "".join(parts)
        return self._format_tlv(self.TAG_MERCHANT_ACCOUNT, merchant_account)

    def _calculate_crc(self, payload: str) -> str:
        """Calculate CRC16 for payload."""
        crc_payload = payload + self.TAG_CRC + "04"
        crc = self.crc16(crc_payload.encode('utf-8'))
        return f"{crc:04X}"

    def build_static_qr(self, data: QRStaticData) -> str:
        """Build static QR payload (merchant info only, no amount)."""
        parts = [
            self._format_tlv(self.TAG_PAYLOAD_FORMAT, "01"),  # Payload format indicator
            self._format_tlv(self.TAG_POI_METHOD, "12"),       # Static QR
            self._build_merchant_account(data.merchant_id, data.account),
            self._format_tlv(self.TAG_MERCHANT_CATEGORY, "5999"),  # Miscellaneous
            self._format_tlv(self.TAG_COUNTRY_CODE, data.country_code),
            self._format_tlv(self.TAG_MERCHANT_NAME, data.merchant_name),
            self._format_tlv(self.TAG_MERCHANT_CITY, data.merchant_city),
        ]
        payload = "".join(parts)
        crc = self._calculate_crc(payload)
        return payload + self._format_tlv(self.TAG_CRC, crc)

    def build_dynamic_qr(self, data: QRDynamicData) -> str:
        """Build dynamic QR payload (includes amount and reference)."""
        parts = [
            self._format_tlv(self.TAG_PAYLOAD_FORMAT, "01"),
            self._format_tlv(self.TAG_POI_METHOD, "11"),  # Dynamic QR
            self._build_merchant_account(data.merchant_id, data.account),
            self._format_tlv(self.TAG_MERCHANT_CATEGORY, "5999"),
            self._format_tlv(self.TAG_COUNTRY_CODE, data.country_code),
            self._format_tlv(self.TAG_MERCHANT_NAME, data.merchant_name),
            self._format_tlv(self.TAG_MERCHANT_CITY, data.merchant_city),
            self._format_tlv(self.TAG_TRANSACTION_CURRENCY, "068"),  # BOB = 068
            self._format_tlv(self.TAG_TRANSACTION_AMOUNT, f"{data.amount:.2f}"),
            self._format_tlv(self.TAG_REFERENCE_LABEL, data.reference),
        ]
        if data.description:
            parts.append(self._format_tlv(self.TAG_ADDITIONAL_DATA, data.description))

        payload = "".join(parts)
        crc = self._calculate_crc(payload)
        return payload + self._format_tlv(self.TAG_CRC, crc)


def generate_qr_svg(payload: str, box_size: int = 10, border: int = 4) -> str:
    """Generate QR code as SVG string."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to SVG string
    buffer = BytesIO()
    img.save(buffer, format="SVG")
    return buffer.getvalue().decode("utf-8")


def generate_qr_png_base64(payload: str, box_size: int = 10, border: int = 4) -> str:
    """Generate QR code as base64-encoded PNG."""
    import base64
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# Convenience functions
def build_static_qr_payload(
    merchant_id: str,
    merchant_name: str,
    merchant_city: str,
    account: str,
) -> str:
    """Build static QR payload for merchant."""
    qr = QRSimpleBolivia()
    data = QRStaticData(
        merchant_id=merchant_id,
        merchant_name=merchant_name,
        merchant_city=merchant_city,
        account=account,
    )
    return qr.build_static_qr(data)


def build_dynamic_qr_payload(
    merchant_id: str,
    merchant_name: str,
    merchant_city: str,
    account: str,
    amount: float,
    reference: str,
    description: str = "",
) -> str:
    """Build dynamic QR payload with amount and reference."""
    qr = QRSimpleBolivia()
    data = QRDynamicData(
        merchant_id=merchant_id,
        merchant_name=merchant_name,
        merchant_city=merchant_city,
        account=account,
        amount=amount,
        reference=reference,
        description=description,
    )
    return qr.build_dynamic_qr(data)


def generate_static_qr_svg(
    merchant_id: str,
    merchant_name: str,
    merchant_city: str,
    account: str,
) -> str:
    """Generate static QR as SVG."""
    payload = build_static_qr_payload(merchant_id, merchant_name, merchant_city, account)
    return generate_qr_svg(payload)


def generate_dynamic_qr_svg(
    merchant_id: str,
    merchant_name: str,
    merchant_city: str,
    account: str,
    amount: float,
    reference: str,
    description: str = "",
) -> str:
    """Generate dynamic QR as SVG."""
    payload = build_dynamic_qr_payload(
        merchant_id, merchant_name, merchant_city, account,
        amount, reference, description
    )
    return generate_qr_svg(payload)


def generate_dynamic_qr_png_base64(
    merchant_id: str,
    merchant_name: str,
    merchant_city: str,
    account: str,
    amount: float,
    reference: str,
    description: str = "",
) -> str:
    """Generate dynamic QR as base64 PNG."""
    payload = build_dynamic_qr_payload(
        merchant_id, merchant_name, merchant_city, account,
        amount, reference, description
    )
    return generate_qr_png_base64(payload)
