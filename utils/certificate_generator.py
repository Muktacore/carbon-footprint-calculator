from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import datetime
import os

def generate_certificate(username, score, output_path='static/certificates'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    filename = f"{output_path}/{username}_certificate.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Background or border (optional: you can draw a badge or border here)

    # Title
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 100, "Certificate of Eco Achievement")

    # Subtitle
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2, height - 140, f"Presented to")

    # Username
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0.2, 0.6, 0.3)
    c.drawCentredString(width / 2, height - 180, username)

    # Achievement message
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 220,
        f"For achieving an eco-friendly carbon footprint score of {score} kg CO₂")

    # Date
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width / 2, height - 270, f"Issued on {datetime.date.today().strftime('%B %d, %Y')}")

    # Footer or signature
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Carbon Footprint Calculator Project - Go Green! 🌿")

    c.save()
    return filename
