
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
from pdf_readers import *
import pandas as pd
from pdf2image import convert_from_path

@time_execution
def classifier_lc_ameco(path, poppler_path, pytesseract):
    try:
        key = keyword(lc_mtu)
        pages = convert_from_path(path, poppler_path=poppler_path)
        inv = dict()
        custom_config = r'-l eng -c tessedit_char_whitelist' \
                        r'="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-:., " '
        custom_config += r'--psm 6'
        page_data = {}
        dict_total = {}
        list_table = []
        extracting = False
        total_amount = None
        for p_idx, page in enumerate(pages):
            text = pytesseract.image_to_string(page, config=custom_config)
            # for i, text in enumerate(data):
            #     logger.info("data: %s", str(text))
            for i, line_row in enumerate(text.split('\n')):
                line_row = line_row.strip()

                if 'Description Amount' in line_row:
                    extracting = True
                    continue
                if 'Total amount' in line_row:
                    logger.info("%s", line_row)
                    extracting = False
                    total_pattern = r'Total amount[:\uFF1A]?\s([\d,]+\.\d{2})\s(USD|EUR|GBP|JPY|CNY)'

                    total_match = re.search(total_pattern, line_row)
                    if total_match:
                        total_amount = to_float(total_match.group(1)) if total_match.group(1) else ""
                        currency = total_match.group(2) if total_match.group(2) else ""
                        dict_total['amount'] = total_amount
                        dict_total['currency'] = currency
                        page_data['total_amount'] = dict_total
                    break
                if extracting:
                    charge_pattern = r'(.+?)\s([\d,]+\.\d{2})\s(USD|EUR|GBP|JPY|CNY)'
                    charge_match = re.search(charge_pattern, line_row)
                    if charge_match:
                        print(charge_match.groups())
                        
                        model =  Details()
                        description = charge_match.group(1).strip() if charge_match.group(1) else ""
                        total = to_float(charge_match.group(2)) if charge_match.group(2) else ""
                        currency = charge_match.group(3) if charge_match.group(3) else ""

                        model.description = description
                        model.total = total
                        model.currency = currency
                        
                        list_table.append(model.to_dict())
        page_data['description'] = list_table

        print(json.dumps(page_data, indent=4))  
       
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None


@time_execution
def classifier_invoice_lc_ameco(pages):
    try:
        page_data = {}
        dict_total = {}
        list_table = []
        extracting = False
        charges = []
        total_amount = None
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            logger.info("text %s", text)

            for i, line_row in enumerate(text):
                logger.info("%s", line_row)
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
    
@time_execution
def classifier_invoice_ameco(pages):
    try:
        page_data = {}
        dict_total = {}
        list_table = []
        extracting = False
        total_amount = None
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line_row in enumerate(text):
                line_row = line_row.strip()

                if 'Description Amount' in line_row:
                    extracting = True
                    continue
                if 'Total amount' in line_row:
                    logger.info("%s", line_row)
                    extracting = False
                    total_pattern = r'Total amount[:\uFF1A]?\s([\d,]+\.\d{2})\s(USD|EUR|GBP|JPY|CNY)'

                    total_match = re.search(total_pattern, line_row)
                    if total_match:
                        total_amount = to_float(total_match.group(1)) if total_match.group(1) else ""
                        currency = total_match.group(2) if total_match.group(2) else ""
                        dict_total['amount'] = total_amount
                        dict_total['currency'] = currency
                        page_data['total_amount'] = dict_total
                    break
                if extracting:
                    charge_pattern = r'(-.*? NTE [\d,]+\.\d{2} USD)'
                    charge_match = re.search(charge_pattern, line_row)
                    if charge_match:
                        pattern = r'-(.*?)\s([\d,]+\.\d{2})\s(USD|EUR|GBP|JPY|CNY)'
                        match = re.search(pattern, charge_match.group(0))
                        
                        if match:
                            model =  Details()
                            description = match.group(1).strip() if match.group(1) else ""
                            total = to_float(match.group(2)) if match.group(2) else ""
                            currency = match.group(3) if match.group(3) else ""

                            model.description = description
                            model.total = total
                            model.currency = currency
                            
                            list_table.append(model.to_dict())
        page_data['description'] = list_table
        # write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
    
@time_execution
def classifier_invoice_ameco_3(pages):
    try:
        page_data = {}
        rpl_total = {}
        crpl_total = {}
        lru_total = {}
        llp_total = {}
        list_table_item = []
        list_table_rpl = []
        list_table_crpl = []
        list_table_lru = []
        list_table_llp = []
        
        key = keyword(ameco)
        replacable_parts_list = False
        contract_repair_part_list = False
        lru_list = False
        llp_list = False
        
        for p_idx, page in enumerate(pages):
            
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                """Extracting data from Replacable Parts List"""
                try:
                    if 'Replacable Parts List' in line:
                        replacable_parts_list = True
                    pass
                except: pass
                if replacable_parts_list:
                        if 'A1--小计/SUBTOTAL (USD) :' in line:
                            values = line.split('$')
                            sub_total_total_price = to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                            sub_total_handling = to_float(to_string(values[2]).replace(' ', '')) if values[2] else 0
                            rpl_total['sub_total_total_price'] = sub_total_total_price
                            rpl_total['sub_total_handling'] = sub_total_handling
                        elif 'A3—合计TOTAL (USD)' in line:
                            values = line.split('$')
                            total = to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                            rpl_total['total'] = total
                            replacable_parts_list = False
                        else:
                            pattern = r"(\d+)\s+([\w-]+)\s+([A-Za-z0-9\s,/-]+?)\s+(\d+)\s+(\w+)\s*\$?\s*([\d,]+\.\d{2})\s*\$?\s*([\d,]+\.\d{2})\s*\$?\s*([\d,]+\.\d{2})\s*\$?\s*([\d,]+\.\d{2})?\s+([A-Za-z\s]+)?"
                            match = re.search(pattern, line)
                            if match:
                                model = Details()
                                model.item = to_int(match.group(1)) if match.group(1) else 0
                                model.part_number = match.group(2) if match.group(2) else ""
                                model.description = match.group(3) if match.group(3) else ""
                                model.quantity = to_int(match.group(4)) if match.group(4) else 0
                                model.unit = match.group(5) if match.group(5) else ""
                                model.clp = to_float(match.group(6)) if match.group(6) not in [None, ''] else 0
                                model.unit_price = to_float(match.group(7)) if match.group(7) not in [None, ''] else 0
                                model.total_price = to_float(match.group(8)) if match.group(8) not in [None, ''] else 0
                                model.handling = to_float(match.group(9)) if match.group(9) not in [None, ''] else 0
                                model.remark = match.group(10) if match.group(10) else ""
                                list_table_rpl.append(model.to_dict())
                """
                Extracting data from Contract repair Parts List
                """
                try:
                    if 'Contract repair Parts List' in line:
                        contract_repair_part_list = True
                    pass
                except: pass
                if contract_repair_part_list:
                    if 'B1--小计/SUBTOTAL (USD) :' in line:
                        values = line.split('$')
                        sub_total_total_price =to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        sub_total_subcontract_fee = to_float(to_string(values[2]).replace(' ', '')) if values[2] else 0
                        crpl_total['sub_total_total_price'] = sub_total_total_price
                        crpl_total['sub_total_subcontract_fee'] = sub_total_subcontract_fee
                    elif 'B3—合计TOTAL (USD)' in line:
                        values = line.split('$')
                        total = to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        crpl_total['total'] = total
                        contract_repair_part_list = False
                    else:
                        pattern = r"(\d+)\s+(\d{7}-\d+)\s+([\w\s,/\-()]+)\s+(\d+)\s+(\w+)\s+(?:([\d,]+(?:\.\d+)?)|\/)\s+\$\s+([\d,]+(?:\.\d+)?)\s+\$\s+([\d,]+(?:\.\d+)?)\s+\$\s+([\d,]+(?:\.\d+)?)?\s*([\w\s]*)?"
                        match = re.search(pattern, line)
                        if match:
                            model = Details()
                            model.item = to_int(match.group(1)) if match.group(1) else 0
                            model.part_number = match.group(2) if match.group(2) else ""
                            model.description = match.group(3) if match.group(3) else ""
                            model.quantity = to_int(match.group(4)) if match.group(4) else 0
                            model.unit = match.group(5) if match.group(5) else ""
                            model.cunit = to_float(match.group(6)) if match.group(6) not in [None, ''] else 0
                            model.usdunit = to_float(match.group(7)) if match.group(7) not in [None, ''] else 0
                            model.total_price = to_float(match.group(8)) if match.group(8) not in [None, ''] else 0
                            model.subcontract_fees = to_float(match.group(9)) if match.group(9) not in [None, ''] else 0
                            model.remarks = match.group(10) if match.group(10) else ""
                            list_table_crpl.append(model.to_dict())
                """Extracting data from LRU List"""
                try:
                    if 'LRU List' in line:
                        lru_list = True  
                    pass
                except: pass
                if lru_list:
                    if 'C1--小计/SUBTOTAL (USD) :' in line:
                        values = line.split('$')
                        sub_total_total_price =to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        sub_total_handling = to_float(to_string(values[2]).replace(' ', '')) if values[2] else 0
                        lru_total['sub_total_total_price'] = sub_total_total_price
                        lru_total['sub_total_handling_fee'] = sub_total_handling
                    elif 'C2--Testing fees测试费用 (USD)' in line:
                        values = line.split('$')
                        handling_fee = to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        lru_total['testing_fee'] = handling_fee
                    elif 'C3--Subcontract修理费用 (USD)' in line:
                        values = line.split('$')
                        sub_total_subcontract_fee = to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        lru_total['sub_total_subcontract_fee'] = sub_total_subcontract_fee
                    elif 'C5—合计TOTAL (USD)' in line:
                        values = line.split('$')
                        total = to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        lru_total['total'] = total
                        lru_list = False
                    else:
                        pattern = r'(\d+)\s+([A-Za-z0-9-]+)\s+(.+?)\s+(\d+)\s+(EA|SET)\s+\$\s+([\d,]+\.\d{2})\s+\$\s+([\d,]+\.\d{2})(?:\s+\$\s+([\d,]+\.\d{2}))?\s*(.+)?'
                        match = re.search(pattern, line)
                        if match:
                            model = Details()
                            model.item = to_int(match.group(1)) if match.group(1) else ""
                            model.part_number = match.group(2) if match.group(2) else ""
                            model.description = match.group(3) if match.group(3) else ""
                            model.quantity = to_int(match.group(4)) if match.group(4) else 0
                            model.unit = match.group(5) if match.group(5) else ""
                            model.usdunit = to_float(match.group(6)) if match.group(6) not in [None, ''] else 0
                            model.total_price = to_float(match.group(7)) if match.group(7) not in [None, ''] else 0
                            model.handling = to_float(match.group(8)) if match.group(8) not in [None, ''] else 0
                            model.remarks = match.group(9) if match.group(9) else ""
                            list_table_lru.append(model.to_dict()) 
                """Extracting data from LLP List"""
                try:
                    if 'LLP List' in line:
                        llp_list = True
                    pass
                except: pass
                if llp_list:
                    if 'D1--小计/SUBTOTAL (USD) :' in line:
                        values = line.split('$')
                        sub_total_total_price =to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        sub_total_handling = to_float(to_string(values[2]).replace(' ', '')) if values[2] else 0
                        llp_total['sub_total_total_price'] = sub_total_total_price
                        llp_total['sub_total_handling'] = sub_total_handling
                    elif 'D3—合计TOTAL (USD)' in line:
                        values = line.split('$')
                        total = to_float(to_string(values[1].replace(' ', ''))) if values[1] else 0
                        llp_total['total'] = total
                        llp_list = False
                    else:
                        pattern = r"(\d+)\s+(\w+-\d+)\s+([\w\s,/\-()]+)\s+(\d+)\s+(\w+)\s+\$\s*([\d,]+(?:\.\d+)?)\s+\$\s*([\d,]+(?:\.\d+)?)\s+\$\s*([\d,]+(?:\.\d+)?)\s*\$\s*([\d,]+(?:\.\d+)?)?\s*([\w\s]*)?"
                        match = re.search(pattern, line)
                        if match:
                            model = Details()
                            model.item = to_int(match.group(1)) if match.group(1) else 0
                            model.part_number = match.group(2) if match.group(2) else ""
                            model.description = match.group(3) if match.group(3) else ""
                            model.quantity = to_int(match.group(4)) if match.group(4) else 0
                            model.unit = match.group(5) if match.group(5) else ""
                            model.clp = to_float(match.group(6)) if match.group(6) not in [None, ''] else 0
                            model.usdunit = to_float(match.group(7)) if match.group(7) not in [None, ''] else 0
                            model.total_price = to_float(match.group(8)) if match.group(8) not in [None, ''] else 0
                            model.handling = to_float(match.group(9)) if match.group(9) not in [None, ''] else 0
                            model.remark = match.group(10) if match.group(10) else ""
                            list_table_llp.append(model.to_dict())       
            tables = page.extract_tables()
            for table in tables:
                header = None
                for row in table:
                    if "Amount" in row:
                        header = row
                    elif header and any(row):
                        data_row = {header[i]: row[i] for i in range(len(header)) if header[i] is not None and header[i] != ''}
                        # Clean "Items" value
                        if "Items" in data_row:
                            cleaned_item_lines = [''.join(line.split()) for line in data_row["Items"].split('\n')]
                            cleaned_item_values = '\n'.join(cleaned_item_lines)
                            data_row["Items"] = cleaned_item_values
                        # Process "Amount" value
                        if "Amount" in data_row:
                            amount_value = data_row["Amount"]
                            if amount_value:
                                # Remove the first character and convert to float
                                cleaned_amount_value = to_float(amount_value[1:])
                                data_row["Amount"] = cleaned_amount_value
                        if data_row["Items"] == '':
                            page_data['total_items_price'] = data_row["Amount"]
                        list_table_item.append(data_row)
        page_data['table_items'] = list_table_item
        page_data['table_rpl'] = list_table_rpl
        page_data['rpl_total'] = rpl_total
        page_data['table_crpl'] = list_table_crpl
        page_data['crpl_total'] = crpl_total
        page_data['table_lru'] = list_table_lru
        page_data['lru_total'] = lru_total
        page_data['table_llp'] = list_table_llp
        page_data['llp_total'] = llp_total
        # write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))

    except Exception as e:
        logger.error("Error invoice credit %s", str(e))
        return None