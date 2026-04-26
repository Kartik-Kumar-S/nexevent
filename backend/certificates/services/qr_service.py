import io
import qrcode  
from django.conf import settings


class QRService:
    """Generates QR codes for certificate verification."""

    def generate_verification_qr(self, certificate) -> io.BytesIO:
        verification_url = (
            f"{settings.FRONTEND_URL}/certificates/verify/"
            f"{certificate.verification_hash}"
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
