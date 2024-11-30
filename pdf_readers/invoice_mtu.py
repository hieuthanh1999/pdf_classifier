
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
            lines = data.splitlines()
            for i, text in enumerate(lines):
                # logger.info("data: %s", str(text))

                if key.customer_po in text and key.order_date in text:
                    pattern = r'CUSTOMER\sP\.O\.\s*[:\-]?\s*([^\n]+)\s*ORDER\sDATE\s*[:\-]?\s*([^\n]+)'
                    match = re.search(pattern, text)
                    if match:
                        customer_po = match.group(1).strip() if match.group(1) else "" 
                        order_date = match.group(2).strip()  if match.group(2) else "" 
                        inv[key.customer_po] = customer_po
                        inv[key.order_date] = order_date
                    else:
                        inv[key.customer_po] = ""
                        inv[key.order_date] = ""
                if key.mtu_wo in text and key.date_shipped in text:
                    pattern = r"MTU W\.O\.: (\d+)\s+DATE SHIPPED:\s*(\S*)"                   
                    match = re.search(pattern, text)
                    if match:
                        mtu_wo = match.group(1).strip() if match.group(1) else "" 
                        date_shipped = match.group(2).strip() if match.group(2) else "" 
                        inv[key.mtu_wo] = mtu_wo
                        inv[key.date_shipped] = date_shipped
                    else:
                        inv[key.mtu_wo] = ""
                        inv[key.date_shipped] = ""
                if key.invoice_no in text and key.invoice_date in text:
        
                    pattern = r"INVOICE NO\.?:\s*(\d+\.\d+)\s*INVOICE DATE:\s*([\d\-A-Za-z]+)"
                    match = re.search(pattern, text)
                    if match:
                        invoice_no = match.group(1) if match.group(1) else "" 
                        invoice_date = match.group(2)  if match.group(2) else "" 
                        inv[key.invoice_no] = invoice_no
                        inv[key.invoice_date] = invoice_date
                    else:
                        inv[key.invoice_no] = ""
                        inv[key.invoice_date] = ""

                if key.remarks in text and key.exchange_rate in text:
                    pattern_remarks = r"REMARKS:\s*([\w\d]+).*?EXCHANGE RATE:\s*([\d\.]+)"
                    match = re.search(pattern_remarks, text)
                    if match:
                        remarks = match.group(1) if match.group(1) else "" 
                        exchange_rate = match.group(2)  if match.group(2) else "" 
                        inv[key.remarks] = remarks
                        inv[key.exchange_rate] = exchange_rate
                    else:
                        inv[key.remarks] = ""
                        inv[key.exchange_rate] = ""
                        
                if key.cost_estimation in text:
                    pattern_cost_estimation = r"COST ESTIMATION\s*([\d,]+\.\d{2})\s*USS"
                    match = re.search(pattern_cost_estimation, text)
                    if match:
                        cost_estimation = match.group(1) if match.group(1) else "" 
                        inv[key.cost_estimation] = cost_estimation
                    else:
                        inv[key.cost_estimation] = ""
                if key.fixed_price in text:
                    pattern_price = r"Fixed price\s*([\d,]+\.\d{2})"
                    match = re.search(pattern_price, text)
                    if match:
                        fixed_price = match.group(1) if match.group(1) else "" 
                        inv[key.fixed_price] = fixed_price
                    else:
                        inv[key.fixed_price] = ""
                if key.materials in text:
                    pattern_materials = r"Materials\s*([\d,]+\.\d{2})"
                    match = re.search(pattern_materials, text)
                    if match:
                        materials = match.group(1) if match.group(1) else "" 
                        inv[key.materials] = materials
                    else:
                        inv[key.materials] = ""
                if key.outside_vendor_charges in text:
                    pattern_vendor_charges = r"Outside vendor charges\s*([\d,]+\.\d{2})"
                    match = re.search(pattern_vendor_charges, text)
                    if match:
                        outside_vendor_charges = match.group(1) if match.group(1) else "" 
                        inv[key.outside_vendor_charges] = outside_vendor_charges
                    else:
                        inv[key.outside_vendor_charges] = ""

                if key.inhouse_repair in text:
                    pattern_inhouse_repair = r"Inhouse repair\s*([\d,]+\.\d{2})"
                    match = re.search(pattern_inhouse_repair, text)
                    if match:
                        inhouse_repair = match.group(1) if match.group(1) else "" 
                        inv[key.inhouse_repair] = inhouse_repair
                    else:
                        inv[key.inhouse_repair] = ""
                
                if key.actual_to_pay in text:
                    pattern_actual_to_pay = r"Actual to pay:\s*([\d,]+\.\d{2})\s*USS"
                    match = re.search(pattern_actual_to_pay, text)
                    if match:
                        actual_to_pay = match.group(1) if match.group(1) else "" 
                        inv[key.actual_to_pay] = actual_to_pay
                    else:
                        inv[key.actual_to_pay] = ""
                    
                
        print(json.dumps(inv, indent=4))  
       
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
