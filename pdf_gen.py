from fpdf import FPDF
import os
import sys

pdf = FPDF()

QR_SIZE = 80

images = [image for image in os.listdir('img') if image.endswith('.png')]

for i in range(0, len(images), 6):
    pdf.add_page()
    pdf.image('img/' + images[i], 10, 10, QR_SIZE)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(10, QR_SIZE) 
    pdf.cell(QR_SIZE, 10, txt=images[i].split('.')[0], ln=1, align='C')

    if i + 1 < len(images):
        pdf.image('img/' + images[i+1], QR_SIZE + 10, 10, QR_SIZE)
        pdf.set_xy(QR_SIZE + 10, QR_SIZE)
        pdf.cell(QR_SIZE, 10, txt=images[i+1].split('.')[0], ln=1, align='C')

    if i + 2 < len(images):
        pdf.image('img/' + images[i+2], 10, QR_SIZE + 10, QR_SIZE)
        pdf.set_xy(10, QR_SIZE * 2)
        pdf.cell(QR_SIZE, 10, txt=images[i+2].split('.')[0], ln=1, align='C')

    if i + 3 < len(images):
        pdf.image('img/' + images[i+3], QR_SIZE + 10, QR_SIZE + 10, QR_SIZE)
        pdf.set_xy(QR_SIZE + 10, QR_SIZE * 2)
        pdf.cell(QR_SIZE, 10, txt=images[i+3].split('.')[0], ln=1, align='C')
    
    if i + 4 < len(images):
        pdf.image('img/' + images[i+4], 10, QR_SIZE * 2 + 10, QR_SIZE)
        pdf.set_xy(10, QR_SIZE * 3)
        pdf.cell(QR_SIZE, 10, txt=images[i+4].split('.')[0], ln=1, align='C')

    if i + 5 < len(images):
        pdf.image('img/' + images[i+5], QR_SIZE + 10, QR_SIZE * 2 + 10, QR_SIZE)
        pdf.set_xy(QR_SIZE + 10, QR_SIZE * 3)
        pdf.cell(QR_SIZE, 10, txt=images[i+5].split('.')[0], ln=1, align='C')

pdf.output('out.pdf', 'F')