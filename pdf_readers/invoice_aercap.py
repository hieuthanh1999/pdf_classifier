import configparser
import json
import re
import os
import sys
import pdfplumber
from model import *
from type import  *
import time
from common import *
from pdf_readers import *
import pandas as pd
from pdf_readers import *
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

@time_execution
def classifier_invoice_aercap(pages, path, poppler_path, pytesseract):
    try:
        page_data = {}
        list_table = []
        extracting_data = False
        pattern = re.compile(r'(?P<date>\d{2}-\w{3}-\d{4})\s+Credit\s+Note\s+Number\s+:\s+(?P<credit_note_number>\d+)')
        list_pattern = re.compile(r'(?P<date>\d{2}-\w{3}-\d{4})\s+(?P<transaction_type>[\w\s]+)\s+(?P<amount>\d{1,3}(?:,\d{3})*\.\d{2})')
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                logger.info("Line: %s", line)
                match = pattern.search(line)
                if match:
                    page_data['date'] = match.group('date')
                    page_data['credit_note_number'] = match.group('credit_note_number')
                if 'Effective Date' in line:
                    extracting_data = True
                    continue
                if extracting_data:
                    match = list_pattern.search(line)
                    if match:
                        model = Details()
                        model.date = match.group('date')
                        model.transaction_type = match.group('transaction_type')
                        model.amount = to_float(match.group('amount'))
                        list_table.append(model.to_dict())
                    if 'Credit Note Total' in line:
                        extracting_data = False
                        total_match = re.search(r'Credit Note Total\s+([\d,]+\.\d{2})', line)
                        if total_match:
                            page_data['total'] = to_float(total_match.group(1))
        page_data['table'] = list_table
        if "table" not in page_data or not page_data["table"]:
            return classifier_invoice_aercap_2(path, poppler_path, pytesseract)
        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))

        #print(invoice.to_string())
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None



@time_execution
def classifier_invoice_aercap_2(path, poppler_path, pytesseract):
    try:
        logger.info("Found start at line %s", "dsadsadsa")

        page_data = {}
        pages = convert_from_path(path, poppler_path=poppler_path)
        inv = dict()
        custom_config = r'-l eng -c tessedit_char_whitelist' \
                        r'="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-:., " '
        for p_idx, page in enumerate(pages):
            data = pytesseract.image_to_string(page, config=custom_config)
            lines = data.splitlines()
            for i, text in enumerate(lines):
                logger.info("Text from page %d: %s", p_idx + 1, text)
        # dict_total = {}
        # table = []
        # key = keyword(rolls_royce)
        # for p_idx, page in enumerate(pages):
        #     text = page.extract_text().split('\n')
        #     collecting_description = False
        #     description_data = []
        #     model = Details()
        #     for i, line in enumerate(text):
        #         logger.info("Found start at line %s", line)
        #         if re.search(r'Description\s+Amount\s\(USD\)', line):
        #             collecting_description = True
        #             logger.info("Found start at line %d: %s", i, line)
        #             continue

        #         if re.search(r'Tax Rate', line):
        #             collecting_description = False
        #             logger.info("Found end at line %d: %s", i, line)
        #             continue

        #         if "Invoice Number" in line or "Date of Issue" in line:
        #             pattern = r"Invoice Number:\s+([\w-]+)\s+Date of Issue:\s+([\w-]+)"
        #             match = re.search(pattern, line)
        #             if match:
        #                 invoice_number = match.group(1)
        #                 page_data['invoice_number'] = invoice_number
        #                 date_of_issue = match.group(2)
        #                 page_data['date_of_issue'] = date_of_issue
        #         if "Due for Payment" in line :
        #             pattern = r"Due for Payment:\s+([\w-]+)"
        #             match = re.search(pattern, line)
        #             if match:
        #                 page_data['date_of_payment'] = match.group(1)

        #         invoice_total_line = re.search(r'Invoice Total\s+([\d,.]+)', line)
        #         if invoice_total_line:
        #             invoice_total = invoice_total_line.group(1)
        #             page_data['invoice_total'] = to_float(invoice_total)
        #         if collecting_description:
        #             description_data.append(line.strip())

        #     if description_data:
        #         model = Details()
        #         description_string = '\n'.join(description_data)
        #         #page_data['description'] = description_string
        #         for line in description_data:
        #             amount_match = re.search(r'[\d,.]+\.\d{2}', line)
        #             if amount_match:
        #                 amount = amount_match.group(0)
        #                 model.amount = amount

        #         if model.amount :
        #             line_description = description_string.replace(model.amount, '').strip()
        #             model.amount  = to_float(model.amount)
        #         model.description = line_description
        #         table.append(model.to_dict())



        # page_data['table'] = table
        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
