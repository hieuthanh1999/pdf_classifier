
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

def is_amount(text):
    return bool(re.search(r"\d{1,3}(,\d{3})*(\.\d{2})?$", text.strip()))

@time_execution
def classifier_invoice_celestial(pages):
    try:
        page_data = {}
        dict_total = {}
        table = []
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            collecting_description = False
            description_data = []
            model = Details()
            for i, line in enumerate(text):
                if re.search(r'Description\s+Amount\s\(USD\)', line):
                    collecting_description = True
                    #logger.info("Found start at line %d: %s", i, line)
                    continue

                if re.search(r'Tax Rate', line):
                    collecting_description = False
                    #logger.info("Found end at line %d: %s", i, line)
                    continue

                if "Invoice Number" in line or "Date of Issue" in line:
                    pattern = r"Invoice Number:\s+([\w-]+)\s+Date of Issue:\s+([\w-]+)"
                    match = re.search(pattern, line)
                    if match:
                        invoice_number = match.group(1)
                        page_data['invoice_number'] = invoice_number
                        date_of_issue = match.group(2)
                        page_data['date_of_issue'] = date_of_issue
                if "Due for Payment" in line :
                    pattern = r"Due for Payment:\s+([\w-]+)"
                    match = re.search(pattern, line)
                    if match:
                        page_data['date_of_payment'] = match.group(1)

                invoice_total_line = re.search(r'Invoice Total\s+([\d,.]+)', line)
                if invoice_total_line:
                    invoice_total = invoice_total_line.group(1)
                    page_data['invoice_total'] = to_float(invoice_total)
                if collecting_description:
                    description_data.append(line.strip())

            if description_data:
                model = Details()
                description_string = '\n'.join(description_data)
                #page_data['description'] = description_string
                for line in description_data:
                    amount_match = re.search(r'[\d,.]+\.\d{2}', line)
                    if amount_match:
                        amount = amount_match.group(0)
                        model.amount = amount

                if model.amount :
                    line_description = description_string.replace(model.amount, '').strip()
                    model.amount  = to_float(model.amount)
                model.description = line_description
                table.append(model.to_dict())



        page_data['table'] = table
        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
