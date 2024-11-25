
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
def classifier_invoice_deposit_rolls_royce(pages):
    try:
        page_data = {}
        key_data = {}
        list_table = []
        extracting = False
        key = keyword(rolls_royce)
        pattern = r"(.*?)\s*([\d,]+\.\d{2})"
        for p_idx, page in enumerate(pages):
            texts = page.extract_text().split('\n')
            for i, line in enumerate(texts):
                logger.info("Line %s: %s", i, line)
                if 'Invoice No:' in line:
                    page_data['invoice_no'] = line.split(':')[1].strip()
                if 'Date:' in line:
                    page_data['date'] = line.split(':')[1].strip()
                if 'Due Date:' in line:
                    page_data['due_date'] = line.split(':')[1].strip()
                if 'Description' in line:
                    extracting = True
                    continue
                if extracting:
                    if 'Payment Instructions' in line:
                        extracting = False
                        continue
                    match = re.search(pattern, line)
                    if match:
                        model = Details()
                        if not match.group(1):
                            model.description = texts[i+1]
                        else:
                            model.description = match.group(1)
                        model.goods_value = to_float(match.group(2))
                        list_table.append(model.to_dict())
                if 'Net Total' in line:
                    match = re.search(r'[\d,]+\.\d{2}', line)
                    key_data['net_total'] = to_float(match.group(0)) if match else None
                if 'VAT' in line:
                    match = re.search(r'VAT\s*@\s*([\d.]+)\s*%\s*([\d,]+\.\d{2})', line)
                    key_data['vat_percentage'] = to_float(match.group(1)) if match else None
                    key_data['vat_total'] = to_float(match.group(2)) if match else None
                if 'Total' in line and ('Payable' in texts[i+1] or 'Payable' in texts[i+2]):
                    match = re.search(r'[\d,]+\.\d{2}', line)
                    if match:
                        key_data['total_payable'] = to_float(match.group(0))
                    else:
                        match = re.search(r'[\d,]+\.\d{2}', texts[i+1])
                        if match:
                            key_data['total_payable'] = to_float(match.group(0))
                        else:
                            match = re.search(r'[\d,]+\.\d{2}', texts[i+2])
                            key_data['total_payable'] = to_float(match.group(0)) if match else None
        key_data['table'] = list_table
        page_data['invoice'] = key_data
        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None

@time_execution
def classifier_invoice_credit_rolls_royce(pages):
    try:
        list_table = []
        page_data = {}
        for p_idx, page in enumerate(pages):
            tables = page.extract_tables()
            for table in tables:
                header = None
                for row in table:
                    if "DESCRIPTION" in row:
                        header = row
                    elif header and any(row):
                        model = Details()
                        for i in range(len(header)):
                            if header[i] is not None and row[i] is not None:
                                if "GOODS VALUE" in header[i].upper() or "GOODS VALUE" in header[i].upper():
                                    model.goods_value = to_float(row[i])
                                else:
                                    model.description  = row[i]
                        list_table.append(model.to_dict())
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                match_total = re.search(r'TOTAL EXCLUDING VAT\s([\d,]+\.\d{2})', line)
                if match_total:
                    page_data['total_excluding_vat'] = to_float(match_total.group(1))
                match_vat = re.search(r'VAT\s*@\s*([\d.]+)\s*%\s*([\d.]+)', line)
                if match_vat:
                    page_data['vat_percentage'] = to_percentage(match_vat.group(1))  # Giá trị phần trăm
                    page_data['vat_total'] = to_float(match_vat.group(2))  # Giá trị tiề 
                match = re.search(r'TOTAL USD\s+CREDIT\s+([\d,]+\.\d{2})', line)
                if match:
                    page_data['total_usd_credit'] = to_float(match.group(1))
               

        page_data['table'] = list_table
        print(json.dumps(page_data, indent=4))
        # write_json_to_file(page_data)

    except Exception as e:
        print(f"Error: {e}")
        return None

                        
               
        #print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
    
@time_execution
def classifier_invoice_rolls_royce(pages):
    try:
        page_data = {}
        key_data = {}
        list_table = []
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):
            tables = page.extract_tables()
            for table in tables:
                header = None
                for row in table:
                    if key.item in row:
                        header = row
                    elif header and any(row):
                        data_row = {header[i]: row[i] for i in range(len(header)) if header[i] is not None}
                        if key.qty in data_row:
                            values = data_row[key.qty]
                            data_row[key.qty] = to_int(values[0])
                        if key.unit_price_usd in data_row and "\n"+key.subtotal in data_row[key.unit_price_usd]:
                            values = data_row[key.unit_price_usd].split("\n")
                            if len(values) == 2:
                                data_row[key.unit_price_usd] = to_float(values[0])
                                data_row[key.subtotal] = to_float(values[0])
                        if key.goods_value in data_row and "\n" in data_row[key.goods_value]:
                            values = data_row[key.goods_value].split("\n")
                            data_row[key.goods_value] = to_float(values[0])
                        list_table.append(data_row)

                    row_text = ' '.join([str(cell) for cell in row if cell])
        
                    #'TOTAL EXCLUDING VAT'
                    if key.total_excluding_vat in row_text or key.total_excluding_va_t in row_text:
                        total_excluding_vat = re.search(r'[\d,]+\.\d{2}', row_text)
                        total_excluding_vat = total_excluding_vat.group(0) if total_excluding_vat else None
                        key_data['total_excluding_vat'] = total_excluding_vat
                    #'TOTAL USD PAYABLE'
                    if key.total_usd_payable in row_text:
                        total_usd_payable = re.search(r'[\d,]+\.\d{2}', row_text)
                        total_usd_payable = total_usd_payable.group(0) if total_usd_payable else None
                        key_data['total_usd_payable'] = total_usd_payable

        key_data['table'] = list_table
        page_data['invoice'] = key_data
        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))          
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
