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
from datetime import datetime

@time_execution
def classifier_invoice_lufthansa(pages):
    try:
        page_data = {}
        sumary = {}
        list_table_sumary = []
        list_text = []
        list_table_partial_invoice_value = []
        invoice_no = False
        partial_invoice_value= False
        extract_sumary = False
        regex_sumary = r"(\d*)\s+([\w\s,./()-]+)\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s+\((\d+|\d{1,3}(?:\.\d{3})*,\d{2})\)"
        regex_partial_invoice_value = r'(.+?)\s+(\d+)\s+(\w+)\s+([\d.,-]+)\s+([\d.,-]+)\s+([\d.,-]+)'
        key = keyword(lufthansa)
        for p_idx, page in enumerate(pages):
            logger.info("%s", page)
            text = page.extract_text().split('\n')
            for i, line_row in enumerate(text):
                #line_row = line_row.strip()
                list_text.append(line_row)
                #print(line_row)
                if key.invoice_number in line_row and not invoice_no:
                    extract_sumary = True
                    match = re.search(r'Invoice\s+(\d+)', line_row)
                    if match:
                        invoice_no = True
                        sumary[key.invoice_number] = match.group(1)
                if extract_sumary:
                    line_row = line_row.strip()
                    match = re.search(regex_sumary, line_row)
                    if match:
                        model = Details()
                        model.description = match.group(2)
                        model.amount = to_float(match.group(3))
                        model.vat = to_float(match.group(4))
                        list_table_sumary.append(model.to_dict())
                if key.net_amount in line_row:
                    extract_sumary = False
                    line_row = line_row.replace('_', '')
                    sumary[key.net_amount] = extract_value(line_row, key.net_amount)
                if key.gross_amount in line_row:
                    line_row = line_row.replace('_', '')
                    sumary[key.gross_amount] = extract_value(line_row, key.gross_amount)
                if key.partial_invoice_value in line_row:
                    print(line_row)
                    partial_invoice_value = True
                    sumary[key.partial_invoice_value] = extract_value(line_row, key.partial_invoice_value)
                # print('out')
                if partial_invoice_value:
                    if '*' in line_row and not key.invoice_number in line_row:
                        partial_invoice_value = False
                    else:
                        print(line_row)
                        match = re.search(regex_partial_invoice_value, line_row)
                        if match:
                            
                            model = Details()
                            model.description = match.group(1)
                            model.quantity = match.group(2)
                            model.unit = match.group(3)
                            model.rate = to_float(match.group(4))
                            model.amount = to_float(match.group(5))
                            list_table_partial_invoice_value.append(model.to_dict())
                            print(model.to_dict())
                logger.info("%s", line_row)
        page_data['text'] = list_text
        write_json_to_file(page_data)
        #print(json.dumps(page_data, indent=4))
        #print(invoice.to_string())
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
@time_execution
def extract_value(line_row, key):
    try:
        line_row = line_row.replace(' ', '')
        return float(re.findall(r'\d{1,3}(?:.\d{3})*(?:\,\d+)?', line_row)[0].replace(',', ''))
    except IndexError:
        return 0