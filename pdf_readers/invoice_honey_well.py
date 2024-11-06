
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

def process_table_row(row):
    # Kiểm tra và thay thế các cột trống bằng giá trị phù hợp (ví dụ: "N/A")
    return [cell if cell is not None and cell.strip() != '' else 'N/A' for cell in row]
    
@time_execution
def classifier_honey_well_invoice(pages):
    try:
        page_data = {}
        invoice = Invoice()
        data_page_quote_totals = []
        is_quote_totals = False
        key = keyword(honey_well)
        for p_idx, page in enumerate(pages):
            page_name = ''
            text = page.extract_text().split('\n')
            details = {}
            start_idx = None
            end_idx = None
            for i, line_row in enumerate(text):
                if key.quote_totals in line_row:
                    if start_idx is None:
                        start_idx = i
                    end_idx = i 
            if start_idx is not None and end_idx is not None and end_idx > start_idx:
                result_lines = text[start_idx:end_idx+1]
                for line in result_lines:
                    pattern = re.compile(r'(.+?)\s(\$)\s+(-?\(?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\)?)')
                    match = pattern.search(line)
                    if match:
                        title = match.group(1).strip()
                        currency = match.group(2).strip()
                        amount = to_float_regex(match.group(3).strip())
                        model =  Details()
                        model.title = title
                        model.currency = currency
                        model.amount = amount
                        data_page_quote_totals.append(model.to_dict())
                        #logger.info("%s", data_page_quote_totals)
                        is_quote_totals = True

                        # logger.info("%s", title)
                        # logger.info("%s", currency)
                        # logger.info("%s", amount)
                        
                                    
            for p_idx, page in enumerate(pages):
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        processed_row = process_table_row(row)
                        logger.info("%s", processed_row)
        if len(data_page_quote_totals) > 0:
            page_name = 'quote_totals'
        if page_name and is_quote_totals:
            page_data[page_name] = data_page_quote_totals 
        elif page_name and not is_quote_totals:
            page_data[page_name] = details


        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))     
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
