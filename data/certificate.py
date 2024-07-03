from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from os import path

certificate_path = path.realpath(path.dirname(__file__))
font_arial_path = path.join(certificate_path, 'fonts/Arial.ttf')
font_arialbd_path = path.join(certificate_path, 'fonts/arialbd.ttf')
async def generate_certificate(name, date, user_id, filename):
    c = canvas.Canvas(filename, pagesize=landscape(letter))
    pdfmetrics.registerFont(TTFont('Arial', font_arial_path))
    pdfmetrics.registerFont(TTFont('Arial-Bold', font_arialbd_path))
    c.drawImage("data/bckg.png", 0, 0, width=792, height=230)
    c.setFillColorRGB(0.745, 0.741, 0.76)
    c.rect(0, 558.28, 792, 5, fill=1, stroke=0)
    c.setFillColorRGB(0.114, 0.278, 0.478)
    c.setFont("Arial-Bold", 46)
    c.drawCentredString(415, 420, f"СЕРТИФИКАТ")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Arial", 16)
    c.drawCentredString(415, 390, f"О ПРОХОЖДЕНИИ КУРСА")
    c.setFont("Arial", 16)
    c.drawCentredString(415, 360, f"Сетификат подтверждает, что")
    c.setFont("Arial-Bold", 22)
    c.drawCentredString(415, 330, f"{name}")
    c.setFont("Arial", 16)
    c.drawCentredString(415, 300, f'Прошёл курс по программе «Морские нефтегазовые сооружения»')
    c.drawCentredString(415, 270, f"В объеме 108 (Сто восемь) академических часов")
    c.drawString(540, 160, f"Регистрационный номер: {user_id}")
    c.drawString(540, 130, f"Дата выдачи: {date}")
    c.drawImage("data/logo1.png", 365, 100, width=100, height=100, mask='auto')
    c.save()

# Пример использования функции для создания сертификата
# generate_certificate("Хабибуллин Мурад Уралович", "08.05.2024", "certificate.pdf")