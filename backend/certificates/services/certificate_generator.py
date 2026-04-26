import io
import hashlib
import logging
from datetime import datetime

from django.template import Template, Context
from django.conf import settings
from weasyprint import HTML  # pip install weasyprint

logger = logging.getLogger(__name__)


class CertificateGeneratorService:
    """Handles the actual PDF generation from template + data."""

    def generate_pdf(self, certificate) -> io.BytesIO:
        """
        Takes a Certificate model instance,
        renders the HTML template with data, converts to PDF.
        """
        # 1. Build context data
        context_data = {
            'student_name': certificate.student.get_full_name(),
            'student_email': certificate.student.email,
            'event_name': certificate.event.title,
            'event_date': certificate.event.date.strftime('%B %d, %Y'),
            'event_category': certificate.event.get_category_display(),
            'organizer_name': certificate.event.organizer.get_full_name(),
            'certificate_number': certificate.certificate_number,
            'certificate_type': certificate.get_certificate_type_display(),
            'issued_date': datetime.now().strftime('%B %d, %Y'),
            'verification_url': f"{settings.FRONTEND_URL}/verify/{certificate.verification_hash}",
            # Extra data like rank, score
            **certificate.additional_data,
        }

        # 2. Get HTML template
        if certificate.template and certificate.template.html_template:
            html_content = certificate.template.html_template
        else:
            html_content = self._get_default_template()

        # 3. Render template
        template = Template(html_content)
        rendered_html = template.render(Context(context_data))

        # 4. Convert to PDF
        pdf_buffer = io.BytesIO()
        HTML(string=rendered_html).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        return pdf_buffer

    def _get_default_template(self) -> str:
        """Fallback HTML template if no custom template is assigned."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @page { size: A4 landscape; margin: 0; }
                body {
                    font-family: 'Georgia', serif;
                    text-align: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                    margin: 0;
                    padding: 40px;
                }
                .certificate-container {
                    background: white;
                    border: 3px solid #d4af37;
                    border-radius: 10px;
                    padding: 60px;
                    margin: 20px;
                    min-height: 500px;
                    position: relative;
                }
                .title { 
                    font-size: 36px; color: #1a365d; 
                    margin-bottom: 10px; 
                }
                .subtitle { 
                    font-size: 18px; color: #666; 
                    margin-bottom: 40px; 
                }
                .recipient { 
                    font-size: 32px; color: #2d3748; 
                    font-weight: bold; margin: 20px 0; 
                    border-bottom: 2px solid #d4af37;
                    display: inline-block; padding-bottom: 5px;
                }
                .event-name { 
                    font-size: 22px; color: #4a5568; 
                    margin: 15px 0; 
                }
                .details { 
                    font-size: 14px; color: #718096; 
                    margin-top: 40px; 
                }
                .cert-number { 
                    font-size: 11px; color: #a0aec0; 
                    position: absolute; bottom: 20px; left: 40px; 
                }
                .verify-url {
                    font-size: 11px; color: #a0aec0;
                    position: absolute; bottom: 20px; right: 40px;
                }
            </style>
        </head>
        <body>
            <div class="certificate-container">
                <div class="title">Certificate of {{ certificate_type }}</div>
                <div class="subtitle">This is proudly presented to</div>
                <div class="recipient">{{ student_name }}</div>
                <div class="event-name">
                    for successfully attending<br>
                    <strong>{{ event_name }}</strong>
                </div>
                <div class="details">
                    <p>Date: {{ event_date }}</p>
                    <p>Organized by: {{ organizer_name }}</p>
                    <p>Issued on: {{ issued_date }}</p>
                </div>
                <div class="cert-number">{{ certificate_number }}</div>
                <div class="verify-url">Verify: {{ verification_url }}</div>
            </div>
        </body>
        </html>
        """