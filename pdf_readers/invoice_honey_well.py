
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
        list_table_new_or_replace_parts = []
        list_table_repair_or_overhaul_parts = []
        list_table_over_and_above_nor_parts = []
        list_table_over_and_above_roo_parts = []
        regex_nor = re.compile(r"(\d+)\s+(\S+)\s*(.*?)\s{2,}(.+?)\s{2,}(\S*?)\s*(\S*?)\s+(\d+\.\d+)\s+\$\s+([\d,]*\.\d+)\s+\$\s+([\d,]*\.\d+)\s+\$\s+([\d,]*\.\d+)")
        regex_roo = re.compile(r"(\d+)\s+(\S+)\s*(.*?)\s{2,}(.+?)\s{2,}(\S*?)\s*(\S*?)\s{2,}(Repair|Overhaul|)\s{2,}+(\d+\.\d+)\s+\$\s+([\d,]*\.\d+)\s+\$\s+([\d,]*\.\d+)")
        key = keyword(honey_well)
        new_or_replace_parts = False
        repair_or_overhaul_parts = False
        over_and_above_nor_parts = False
        over_and_above_roo_parts = False
        for p_idx, page in enumerate(pages):
            page_name = ''
            text = page.extract_text().split('\n')
            details = {}
            start_idx = None
            end_idx = None
            for i, line_row in enumerate(text):
                logger.info("%s", line_row)
                # print(line_row)
                if key.quote_totals in line_row:
                    if start_idx is None:
                        start_idx = i
                    end_idx = i 
                try:
                    if 'NEW/REPLACED PARTS' in line_row and 'OVER & ABOVE' not in line_row and 'TOTAL' not in line_row:
                        new_or_replace_parts = True
                    pass
                except: pass
                if new_or_replace_parts:
                    if 'TOTAL NEW/REPLACED PARTS' in line_row:
                        values = line_row.split('$')
                        total_new_or_replace_parts = to_float(values[1].strip())
                        page_data['total_new_or_replace_parts'] = total_new_or_replace_parts
                        new_or_replace_parts = False
                    else:
                        match = regex_nor.search(line_row)
                        if match:
                            list_table_new_or_replace_parts.append(put_data_to_table_nor(match))
                try:
                    if 'REPAIR/OVERHAUL PARTS' in line_row and 'OVER & ABOVE' not in line_row and 'TOTAL' not in line_row:
                        repair_or_overhaul_parts = True
                    pass
                except: pass
                if repair_or_overhaul_parts:
                    if 'TOTAL REPAIR/OVERHAUL PARTS' in line_row:
                        values = line_row.split('$')
                        total_repair_or_overhaul_parts = to_float(values[1].strip())
                        page_data['total_repair_or_overhaul_parts'] = total_repair_or_overhaul_parts
                        repair_or_overhaul_parts = False
                    else:
                        match = regex_roo.search(line_row)
                        if match:
                            list_table_repair_or_overhaul_parts.append(put_data_to_table_roo(match))
                try:
                    if 'OVER & ABOVE NEW/REPLACED PARTS' in line_row:
                        over_and_above_nor_parts = True
                    pass   
                except: pass
                if over_and_above_nor_parts:
                    if 'TOTAL NEW/REPLACED PARTS' in line_row:
                        values = line_row.split('$')
                        total_over_and_above_nor_parts = to_float(values[1].strip())
                        page_data['total_over_and_above_nor_parts'] = total_over_and_above_nor_parts
                        over_and_above_nor_parts = False
                    else:
                        match = regex_nor.search(line_row)
                        if match:
                            list_table_over_and_above_nor_parts.append(put_data_to_table_nor(match)) 
                try:
                    if 'OVER & ABOVE REPAIR/OVERHAUL PARTS' in line_row:
                        over_and_above_roo_parts = True
                    pass
                except: pass
                if over_and_above_roo_parts:
                    if 'TOTAL REPAIR/OVERHAUL PARTS' in line_row:
                        values = line_row.split('$')
                        total_over_and_above_roo_parts = to_float(values[1].replace(' ', ''))
                        page_data['total_over_and_above_roo_parts'] = total_over_and_above_roo_parts
                        over_and_above_roo_parts = False
                    else:
                        match = regex_roo.search(line_row)
                        if match:
                            list_table_over_and_above_roo_parts.append(put_data_to_table_roo(match))
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
                        
        if len(data_page_quote_totals) > 0:
            page_name = 'quote_totals'
        if page_name and is_quote_totals:
            page_data[page_name] = data_page_quote_totals 
        elif page_name and not is_quote_totals:
            page_data[page_name] = details
        page_data['new_or_replace_parts'] = list_table_new_or_replace_parts
        page_data['repair_or_overhaul_parts'] = list_table_repair_or_overhaul_parts
        page_data['over_and_above_nor_parts'] = list_table_over_and_above_nor_parts
        page_data['over_and_above_roo_parts'] = list_table_over_and_above_roo_parts
        #  write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))     
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
    
# @time_execution
def put_data_to_table_roo(match):
    try:    
        model = Details()
        model.item = match.group(1) if match.group(1) else ""
        model.part_number = match.group(2) if match.group(2) else ""
        model.part_no_out = match.group(3) if match.group(3) else ""
        model.description = match.group(4) if match.group(4) else ""
        model.service_bulletin = match.group(5) if match.group(5) else ""
        model.defect_description = match.group(6) if match.group(6) else "" 
        model.repair_or_overhaul_description = match.group(7) if match.group(7) else ""
        model.quantity = to_float(match.group(8)) if match.group(8) else ""
        model.unit_price = to_float(match.group(9)) if match.group(9) else ""
        model.extend_price = to_float(match.group(10)) if match.group(10) else ""
        return model.to_dict()
    except Exception as e:
        print(f"Error: {e}")
        return None   
# @time_execution
def put_data_to_table_nor(match):
    try:
        model = Details()
        model.item = match.group(1) if match.group(1) else ""
        model.part_number = match.group(2) if match.group(2) else ""
        model.part_no_out = match.group(3) if match.group(3) else ""
        model.description = match.group(4) if match.group(4) else ""
        model.service_bulletin = match.group(5) if match.group(5) else ""
        model.defect_description = match.group(6) if match.group(6) else ""
        model.quantity = to_float(match.group(7)) if match.group(7) else ""
        model.unit_price = to_float(match.group(8)) if match.group(8) else ""
        model.mhf = to_float(match.group(9)) if match.group(9) else ""
        model.extend_price = to_float(match.group(10)) if match.group(10) else ""
        return model.to_dict()
    except Exception as e:
        print(f"Error: {e}")
        return None