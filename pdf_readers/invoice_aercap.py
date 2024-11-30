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
def classifier_invoice_aercap(pages):
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
                        model.date = match.group('date') if match.group('date') else ""
                        model.transaction_type = match.group('transaction_type') if match.group('transaction_type') else ""
                        model.amount = to_float(match.group('amount')) if match.group('amount') else ""
                        list_table.append(model.to_dict())
                    if 'Credit Note Total' in line:
                        extracting_data = False
                        total_match = re.search(r'Credit Note Total\s+([\d,]+\.\d{2})', line)
                        if total_match:
                            page_data['total'] = to_float(total_match.group(1))
                        else:
                            page_data['total'] = 0
        page_data['table'] = list_table
        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))          

        #print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None