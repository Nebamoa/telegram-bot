from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


async def generate_certificate(name, date, user_id, filename):
    # Создание объекта canvas (холст) с указанным именем файла
    c = canvas.Canvas(filename, pagesize=landscape(letter))

    # Загрузка шрифта Arial
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
    # c.drawImage("background1.jpg", 0, 0, width=841.89, height=615)
    c.drawImage("data/bckg.png", 0, 0, width=792, height=230)
    c.setFillColorRGB(0.745, 0.741, 0.76)
    c.rect(0, 558.28, 792, 5, fill=1, stroke=0)


    c.setFillColorRGB(0.114, 0.278, 0.478)
    # Нанесение текста на сертификат
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

    # Рамка

    # Логотип
    c.drawImage("data/logo1.png", 365, 100, width=100, height=100, mask='auto')

    # Завершение создания PDF
    c.save()

# Пример использования функции для создания сертификата
# generate_certificate("Хабибуллин Мурад Уралович", "08.05.2024", "certificate.pdf")
