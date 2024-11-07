
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
def classifier_invoice_invoice_epcor(pages):
    try:
        list_table = []
        page_data = {}
        regex = r"([A-Za-z ]+)\s+([A-Za-z ]+)\s+(\d+\.\d{2})\s+(-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d{1,3}(?:,\d{3})*\.\d{2})"
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                logger.info("%s", line)
                if "Invoice #:" in line:
                    try:
                        match = re.search(r"Invoice #:\s*(.*)", line)
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
                elif "Customer Reference #:" in line:
                    try:
                        match = re.search(r"Customer Reference #:\s*(.*)", line)
                        if match:
                            page_data['customer_reference'] = match.group(1).strip()
                    except: 
                        page_data['engine_model'] = ''
                elif "Work Order #:" in line:
                    try:
                        match = re.search(r"Work Order #:\s*(.*)", line)
                        if match:
                            page_data['work_order'] = match.group(1).strip()
                    except: 
                        page_data['serial_number'] = ''
                elif "Net amount" in line:
                    try:
                        match = re.search(r"Net amount\s*(\d{1,3}(?:,\d{3})*\.\d{2})", line)
                        if match:
                            page_data['net_amount'] = to_float(match.group(1).strip())
                    except: 
                        page_data['net_amount'] = 0
                elif "Total amount" in line:
                    print(line)
                    try:
                        match = re.search(r'Total amount incl\. VAT (\d{1,3}(?:,\d{3})*(?:\.\d{2})?) USD', line)
                        if match:
                            page_data['total_amount'] = to_float(match.group(1).strip())
                    except: 
                        page_data['total_amount'] = 0
                elif "VAT" in line:
                    try:
                        match = re.search(r'VAT\s(\d+\.\d{2})\s%\s(\d+\.\d{2})\sUSD', line)
                        if match:
                            page_data['vat_percent'] = to_float(match.group(1).strip())
                            page_data['vat'] = to_float(match.group(2).strip())
                    except: 
                        page_data['vat'] = 0
                        page_data['vat_percent'] = 0
                else:
                    match = re.search(regex,line.strip())
                    if match:
                        detail = Details()
                        try:
                            detail.category = match.group(1).strip()
                        except:
                            detail.category = ''
                        try:
                            detail.description = match.group(2).strip()
                        except:
                            detail.description = ''
                        try:
                            detail.quantity =to_int(match.group(3).strip())
                        except:
                            detail.quantity = 0
                        try:
                            detail.unit_price = to_float(match.group(4).strip())
                        except:
                            detail.unit_price = 0
                        try:
                            detail.total_price = to_float(match.group(5).strip())
                        except:
                            detail.total_price = 0
                        list_table.append(detail.to_dict())
            page_data['table'] = list_table

        write_json_to_file(page_data)    
    except Exception as e:
        print(f"Error: {e}")
        return None