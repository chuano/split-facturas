import tkinter as tk
import xlsxwriter
import os
from tkinter import filedialog as fd
from tkinter import messagebox
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime

root = tk.Tk()
root.title("Split Facturas")
root.resizable(False, False)
root.geometry('300x150')

def clean_filename(filename):
    return filename.strip().replace(" ","_").replace(".","_").replace(",","_").replace("/","_")

def get_bill_number(text):
    return text.split("\n")[1].strip()

def get_account_number(text):
    return text.split("\n")[5].strip()

def get_customer_name(text):
    parts = text.split("\n")
    return parts[10].strip()

def get_bill_date(text):
    date = text.split("\n")[3].strip()
    return date.split("/")[2] + date.split("/")[1] + date.split("/")[0]

def get_bill_amount(text):
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if "Total Neto" in line:
            return float(lines[index + 1].strip())

def get_bill_vat(text):
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if "IVA @" in line:
            return float(lines[index + 1].strip())

def get_bill_total_with_vat(text):
    lines = text.split("\n")
    for index, line in enumerate(lines):
        if "Total Vencido :" in line:
            return float(lines[index + 1].strip())

def get_has_international(text):
    lines = text.split("\n")[40:]
    for line in lines:
        if line[:2] == "ES" and len(line.strip()) == 12 and line.strip()[4:].isdigit():
            return True
    return False

def split_bills(filename):
    # get current date as yyyy-mm-dd-hh-mm-ss
    
    dir_name = os.path.dirname(os.path.abspath(filename)) +  "/facturas-" + datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    os.mkdir(dir_name)
    reader = PdfReader(filename)
    workbook = xlsxwriter.Workbook(dir_name + '/facturas.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    worksheet.write(0, 0, "Factura", bold)
    worksheet.write(0, 1, "Cuenta", bold)
    worksheet.write(0, 2, "Cliente", bold)
    worksheet.write(0, 3, "Total neto", bold)
    worksheet.write(0, 4, "IVA", bold)
    worksheet.write(0, 5, "Total", bold)
    worksheet.write(0, 6, "Internacionales", bold)

    new_file = None
    bill_text = ""
    row = 0

    for page in reader.pages:
        text = page.extract_text()
        if text[:9] == "Factura :":
            if new_file != None:
                bill_number = get_bill_number(bill_text)
                account_number = get_account_number(bill_text)
                customer_name = get_customer_name(bill_text)
                total = get_bill_amount(bill_text)
                vat = get_bill_vat(bill_text)
                total_with_vat = get_bill_total_with_vat(bill_text)
                bill_date = get_bill_date(bill_text)
                has_international = get_has_international(bill_text)

                new_file.write(dir_name + "/" + clean_filename(f"{account_number}_{customer_name}_{bill_date}") + ".pdf")
                bill_text = ""
                row += 1
                worksheet.write(row, 0, bill_number)
                worksheet.write(row, 1, account_number)
                worksheet.write(row, 2, customer_name)
                worksheet.write(row, 3, total)
                worksheet.write(row, 4, vat)
                worksheet.write(row, 5, total_with_vat)
                worksheet.write(row, 6, has_international)
            new_file = PdfWriter()

        bill_text += text
        new_file.add_page(page)

    new_file.write(dir_name + "/" + clean_filename(f"{account_number}_{customer_name}_{bill_date}") + ".pdf")
    worksheet.write(row, 0, bill_number)
    worksheet.write(row, 1, account_number)
    worksheet.write(row, 2, customer_name)
    worksheet.write(row, 3, total)
    worksheet.write(row, 4, vat)
    worksheet.write(row, 5, total_with_vat)
    worksheet.write(row, 6, get_has_international(bill_text))

    workbook.close()

def select_file():
    filetypes = (
        ('text files', '*.pdf'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)
    
    split_bills(filename)

    messagebox.showinfo(title="Facturas separadas", message="Las facturas se han separado correctamente.")
    root.quit()

# open button
open_button = tk.Button(
    root,
    text='Buscar facturas',
    command=select_file
)
open_button.pack(expand=True)

root.mainloop()