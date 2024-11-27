
import configparser
import json
import re
import os
import sys
from model import *
from type import  *
import time
from common import *
from pdf_readers import *
import pandas as pd
from pdf2image import convert_from_path

def process_table_row(row):
    return [cell if cell is not None and cell.strip() != '' else 'N/A' for cell in row]
    
@time_execution
def classifier_lc_mtu_invoice(path, poppler_path, pytesseract):
    try:
        key = keyword(lc_mtu)
        pages = convert_from_path(path, poppler_path=poppler_path)
        inv = dict()
        custom_config = r'-l eng -c tessedit_char_whitelist' \
                        r'="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-:., " '
        for p_idx, page in enumerate(pages):
            data = pytesseract.image_to_string(page, config=custom_config)
            for i, text in enumerate(data):
                logger.info("data: %s", str(text))

                if key.customer_po in text and key.order_date in text:
                    pattern = r'CUSTOMER\sP\.O\.\s*[:\-]?\s*([^\n]+)\s*ORDER\sDATE\s*[:\-]?\s*([^\n]+)'
                    match = re.search(pattern, text)
                    if match:
                        customer_po = match.group(1).strip()
                        order_date = match.group(2).strip() 
                        inv[key.customer_po] = customer_po
                        inv[key.order_date] = order_date
                if key.mtu_wo in text and key.date_shipped in text:
                    pattern = r"MTU W\.O\.: (\d+)\s+DATE SHIPPED:"
                    match = re.search(pattern, text)
                    if match:
                        mtu_wo = match.group(1).strip()
                        # date_shipped = match.group(2).strip()  
                        inv[key.mtu_wo] = mtu_wo
                        #inv[key.date_shipped] = date_shipped
                if key.invoice_no in text and key.invoice_date in text:
                    pattern = r"INVOICE NO\.: (\d+\.\d+)\s+INVOICE DATE\.: (\d{2}-[A-Za-z]{3}-\d{2})"
                    match = re.search(pattern, text)
                    if match:
                        invoice_no = match.group(1)
                        invoice_date = match.group(2) 
                        inv[key.invoice_no] = invoice_no
                        inv[key.invoice_date] = invoice_date
                        #inv[key.date_shipped] = date_shipped
                    pass
                
        print(json.dumps(inv, indent=4))  
       
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
