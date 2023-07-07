import openpyxl
from config import *


def read_only():
    workbook = openpyxl.load_workbook(excel_file)

    sheet = workbook.active

    data = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        data.append(list(row))

    return data
