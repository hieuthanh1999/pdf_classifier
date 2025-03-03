
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
def classifier_invoice_wlfc(pages):
    try:
        logger.info("%s", 'classifier_invoice_wlfc')
        total_amount_regex = r"Total Amount Due \([A-Za-z]{3}\):\s*(\d{1,3}(?:,\d{3})*\.\d{2})"
        regex = r"([A-Za-z\s]+)\s+(Upon\sreceipt|\d{1,2}\s+[A-Za-z]+\s+\d{1,2},\s+\d{4})\s+([A-Za-z]{3})\s+([\d,]+\.\d{2})"
        page_data = {}
        list_table = []
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                #logger.info("%s", line)
                if "Invoice No" in line:
                    try:
                        match = re.search(r"Invoice No:\s*(.*)", line)
                        if match:
                            page_data['invoice_no'] = match.group(1).strip()
                    except:
                        page_data['invoice_no'] = ''

                elif "Invoice Date" in line:
                    try:
                        match = re.search(r"Invoice Date:\s*(.*)", line)
                        if match:
                            page_data['invoice_date'] = match.group(1).strip()
                    except:
                        page_data['invoice_date'] = ''
                elif "Engine Model" in line:
                    try:
                        match = re.search(r"Engine Model:\s*(.*)", line)
                        if match:
                            page_data['engine_model'] = match.group(1).strip()
                    except:
                        page_data['engine_model'] = ''
                elif "Serial Number" in line:
                    try:
                        match = re.search(r"Serial Number:\s*(.*)", line)
                        if match:
                            page_data['serial_number'] = match.group(1).strip()
                    except:
                        page_data['serial_number'] = ''

                else:
                    line = re.sub(r'(\d)\s+(\d)', r'\1\2', line)
                    item_match = re.search(regex,line.strip())

                    if item_match:
                        detail = Details()
                        try:
                            detail.description = item_match.group(1).strip()
                        except:
                            detail.description = ""

                        try:
                            detail.payment_due_date = item_match.group(2).strip()
                        except:
                            detail.payment_due_date = ""
                        try:
                            detail.currency = item_match.group(3).strip()
                        except:
                            detail.currency = "USD"
                        try:
                            detail.amount_due = to_float(item_match.group(4).strip())
                        except:
                            detail.amount_due = 0

                        list_table.append(detail.to_dict())

                try:
                    total_amount_match = re.search(total_amount_regex, line)
                    if total_amount_match:
                        page_data["total_amount_due"] = to_float(total_amount_match.group(1).strip())
                except:
                    page_data["total_amount_due"] = 0
        page_data['table'] = list_table
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
