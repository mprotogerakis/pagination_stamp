import os
import PyPDF2
import io
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import red

path = "/Users/proto/Dropbox/Familienbereich/_Ablage_Inbox/2023"


def remove_extension(file_name):
    return file_name.rsplit('.', 1)[0]

file_counter = 0

#find out maximum used file_counter so far in this directory
for filename in os.listdir(path):
    if filename.endswith(".pdf"):
        pattern = re.compile(r'(\d+)#_(\d{4})-(\d{2})-(\d{2})--.*')
        # those have already been processed
        match = re.search(pattern, filename)
        if match:
            number = int(match.group(1))
            if number > file_counter:
                file_counter = number
if file_counter == 0:
    file_counter = 20230000
file_counter = file_counter + 1
print ("File Counter Start: " + str(file_counter))

# now start processing new files
for filename in os.listdir(path):
    if filename.endswith(".pdf"):
        pattern = re.compile(r'(\d+)#_(\d{4})-(\d{2})-(\d{2})--.*')
        # those have already been processed
        match = re.search(pattern, filename)
        if not match:
            pattern = re.compile(r"(\d{4})-(\d{2})-(\d{2}).*((_rechnung)|(steuer)|(beleg)).*")
            match = re.search(pattern, filename)
            if match:
                print("Processing File: " + filename)
                pdf_file = open(path + "/" + filename, "rb")
                pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
                pdf_writer = PyPDF2.PdfWriter()
                page = pdf_reader.pages[0]
                page.merge_page(pdf_reader.pages[0])
                page.compress_content_streams()

                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)
                can.setFont("Helvetica", 8)
                can.setFillColor(red)
                can.drawString(10, 10, str(file_counter)+ "#_" + remove_extension(filename)+".pdf")
                can.save()
                new_pdf = PyPDF2.PdfReader(packet)
                page.merge_page(new_pdf.pages[0])

                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=A4)
                can.setFont("Helvetica", 20)
                can.setFillColor(red)
                can.drawString(450, 800, str(file_counter))
                can.save()
                new_pdf = PyPDF2.PdfReader(packet)
                page.merge_page(new_pdf.pages[0])

                pdf_writer.add_page(page)
                for i in range(1, len(pdf_reader.pages)):
                    page = pdf_reader.pages[i]
                    pdf_writer.add_page(page)
                output_file = open(path + "/" + str(file_counter)+ "#_" + remove_extension(filename)+".pdf", "wb")
                os.remove(path + "/" + filename)
                pdf_writer.write(output_file)
                pdf_file.close()
                output_file.close()
                file_counter += 1

print("All PDF files processed!")
