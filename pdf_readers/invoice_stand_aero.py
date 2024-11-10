
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
def classifier_invoice_stand_aero(pages):
    try:
        page_data = {}
        dict_total = {}
        list_table = []
        list_table_description = []
        extracting = False
        charges = []
        total_amount = None
        key = keyword(stand_aero)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line_row in enumerate(text):
                line_row = line_row.strip()
                #print(line_row)
                if key.labor in line_row:
                    list_table_description[key.labor] = extract_value(line_row, key.labor)
                if key.component_repair in line_row:
                    list_table_description[key.component_repair] = extract_value(line_row, key.component_repair)
                if key.replacement_parts in line_row:
                    list_table_description[key.replacement_parts] = extract_value(line_row, key.replacement_parts)
                if key.rotable_or_special_processes in line_row:
                    list_table_description[key.rotable_or_special_processes] = extract_value(line_row, key.rotable_or_special_processes)
                if key.test_cell_fee in line_row:
                    list_table_description[key.test_cell_fee] = extract_value(line_row, key.test_cell_fee)
                if key.packing_and_preservation in line_row:
                    list_table_description[key.packing_and_preservation] = extract_value(line_row, key.packing_and_preservation)
                if key.bulk_issue in line_row:
                    list_table_description[key.bulk_issue] = extract_value(line_row, key.bulk_issue)
                if key.inclusive_of_pandwc in line_row:
                    list_table_description[key.inclusive_of_pandwc] = extract_value(line_row, key.inclusive_of_pandwc)
                if key.sub_total in line_row:
                    list_table_description[key.sub_total] = extract_value(line_row, key.sub_total)
                if key.shipping in line_row:
                    list_table_description[key.shipping] = extract_value(line_row, key.shipping)
                if key.TOTAL in line_row:
                    list_table_description[key.TOTAL] = extract_value(line_row, key.TOTAL)
                if key.invoice_number in line_row:
                    line_row = line_row.replace(' ', '')
                    match = re.search(r'Invoice#:(\d+)', line_row)
                    if match:
                        page_data[key.invoice_number] = match.group(1)
                if key.date in line_row:
                    print(line_row)
                    line_row = line_row.replace(' ', '')
                    match = re.search(r'Date:\s*(\d{4}-[A-Za-z]{3}-\d{2})', line_row)
                    if match:
                        date_value = match.group(1)
                        page_data[key.date] = date_value
                        
                #print(line_row)
                logger.info("%s", line_row)
        print(page_data)       
        #print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
@time_execution
def extract_value(line_row, key):
    try:
        line_row = line_row.replace(' ', '')
        return float(re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?', line_row)[0].replace(',', ''))
    except IndexError:
        return 0
