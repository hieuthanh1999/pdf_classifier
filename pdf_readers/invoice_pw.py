
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

@time_execution
def classifier_invoice_pw(pages):
    try:
        page_data = {}
        key_data = {}
        list_table = []
        inv = Invoice()
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):

                if "Invoice Number" in line:
                    try:
                        match = re.search(r"Invoice Number:\s*(.*)", line)
                        if match:
                            page_data['invoice_number'] = match.group(1).strip()
                    except:
                        page_data['invoice_number'] = ''

                elif "Invoice Date" in line:
                    try:
                        match = re.search(r"Invoice Date:\s*(.*)", line)
                        if match:
                            page_data['invoice_date'] = match.group(1).strip()
                    except:
                        page_data['invoice_date'] = ''

                elif "Document No" in line:
                    try:
                        match = re.search(r"Document No\.\s*:\s*(.*)", line)
                        if match:
                            page_data['document_no'] = match.group(1).strip()
                    except:
                        page_data['document_no'] = ''
                elif "EA" in line and "$" in line:
                    parts = line.split()
                    detail = Details()
                    try:
                        detail.description = f"{parts[0]} {parts[1]}"
                    except:
                        detail.description = ""
                    try:
                        detail.condition = " ".join(parts[2:-4])
                    except:
                        detail.condition = " "
                    try:
                        detail.quantity = parts[-4]
                    except:
                        detail.quantity = 0
                    try:
                        detail.unit_price = parts[-3]
                    except:
                        detail.unit_price = 0
                    try:
                        detail.net_price = parts[-1]
                    except:
                        detail.net_price = 0
                    list_table.append(detail.to_dict())
                elif "Total amount due" in line:
                    try:
                        total_match = re.search(r"Total amount due\s+\$(\d+,\d+\.\d+)", line)
                        if total_match:
                            page_data['total_amount'] = to_float(total_match.group(1).strip())
                    except:
                        page_data['total_amount'] = 0

        page_data['table'] = list_table
        if "table" not in page_data or not page_data["table"]:
            return classifier_repair_invoice(pages)
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
