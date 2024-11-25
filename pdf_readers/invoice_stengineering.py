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
def classifier_invoice_stengineering(pages):
    try:
        page_data = {}
        dict_total = {}
        list_table = []
        list_gst = []
        extracting = False
        extract_gst = False
        charges = []
        total_amount = None
        key = keyword(rolls_royce)
        pattern = r"(\d+)\s(\d{2}-\w{3}-\d{4})\s+([\w\s\d]+)\s+(\d{2}-\w{3}-\d{4})"
        pattern_table = r"(.+?)\s+([\d,]*\.\d{2})?\s+([\d,]+\.\d{2})"
        pattern_total_rate = r"(.+?)\s+(\([\d.,@ ]+\))?\s*([\d,]+\.\d{2})"
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line_row in enumerate(text):
                logger.info("%s", line_row)
                if 'Invoice Number' in line_row:
                    page_data['invoice_number'] = text[i+1]
                    match = re.search(pattern, text[i+1])
                    if match:
                        page_data['invoice_number'] = match.group(1)
                        page_data['invoice_date'] = match.group(2)
                        page_data['invoice_due_date'] = match.group(4)
                if 'Description' in line_row and 'Amount' in line_row:
                    extracting = True
                if extracting:
                    match = re.search(pattern_table, line_row)
                    if match:
                        model = Details()
                        model.description = match.group(1) + " " + (match.group(2) if match.group(2) else '')
                        model.amount = to_float(match.group(3))
                        list_table.append(model.to_dict())
                    # if 'Total Amount' in line_row:
                    #     total_amount = text[i+1]
                    #     break
                if 'FOR GST PURPOSES ONLY' in line_row:
                    extracting = False
                    extract_gst = True
                if extract_gst:
                    
                    match = re.search(pattern_total_rate, line_row)
                    if 'Total amount' in line_row:
                        total_amount = match.group(3)
                    if match:
                        model = Details()
                        if 'GST' in match.group(1):
                            model.description = match.group(1) + ' ' + total_amount
                        else:
                            model.description = match.group(1)
                        model.exchange_rate = match.group(2) if match.group(2) else 'N/A'
                        model.amount = to_float(match.group(3))
                        list_gst.append(model.to_dict())
        page_data['table'] = list_table
        page_data['gst'] = list_gst     
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None