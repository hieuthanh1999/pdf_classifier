
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
        charges = []
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
                    #logger.info("%s", line_row)
                    extracting = False
                    total_pattern = r'Total amount[:\uFF1A]?\s([\d,]+\.\d{2})\s(USD|EUR|GBP|JPY|CNY)'

                    total_match = re.search(total_pattern, line_row)
                    if total_match:
                        total_amount = to_float(total_match.group(1))
                        #logger.info("%s", total_match.group(1))
                        currency = total_match.group(2) 
                        #logger.info("%s ==== %s", total_amount, currency)
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
                            description = match.group(1).strip()
                            total = to_float(match.group(2))
                            currency = match.group(3)

                            model.description = description
                            model.total = total
                            model.currency = currency
                            
                            list_table.append(model.to_dict())
        page_data['description'] = list_table
        write_json_to_file(page_data)
        #print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
    
@time_execution
def classifier_invoice_ameco_3(pages):
    try:
        page_data = {}
        key_data = {}
        list_table_item = []
        list_table_rpl = []
        
        key = keyword(ameco)
        rpl = False
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            table_data = []
            invoice_no = None
            page_name = None
            details = {}
            
            for i, line in enumerate(text):
                # model = None;
                # if 'Replacable Parts List' in line:
                #     model = Details("")
                #     print(text[i+1])
                # pattern = r'P/N:(P-\d+)'
                # match = re.search(pattern, line)
                # if match:
                #     invoice_no = match.group(1)
                #print(line)
                
                try:
                    if 'Replacable Parts List' in line:
                        rpl = True
                        page_name = 'rpl'
                    pass
                except: pass
                if rpl:
                    if 'A1--小计/SUBTOTAL (USD) :' in line:
                        values = line.split('$')
                        sub_total_total_price =to_float(to_string(values[1].replace(' ', '')))
                        sub_total_handling = to_float(to_string(values[2]).replace(' ', ''))
                    elif 'A2—Handling fees手续费(=A1*0.05)' in line:
                        values = line.split('$')
                        handling_fee = to_float(to_string(values[1].replace(' ', '')))
                    elif 'A3—Total Total总计(=A1+A2)' in line:
                        values = line.split('$')
                        total = to_float(to_string(values[1].replace(' ', '')))
                        rpl = False
                    else:
                        pattern = r"(\d+)\s+([\w-]+)\s+([A-Za-z0-9\s,/-]+?)\s+(\d+)\s+(\w+)\s*\$?\s*([\d,]+\.\d{2})\s*\$?\s*([\d,]+\.\d{2})\s*\$?\s*([\d,]+\.\d{2})\s*\$?\s*([\d,]+\.\d{2})\s+([A-Za-z\s]+)?"
                        match = re.search(pattern, line)
                        if match:
                            model = Details("")
                            model.item = match.group(1)
                            model.part_number = match.group(2)
                            model.description = match.group(3)
                            model.quantity = match.group(4)
                            model.unit = match.group(5)
                            model.clp = match.group(6)
                            model.unit_price = match.group(7)
                            model.total_price = match.group(8)
                            model.handling = match.group(9)
                            model.remark = match.group(10)
                            list_table_rpl.append(model.to_dict())
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
            # match = re.search()   
        page_data['table_items'] = list_table_item
        page_data['table_rpl'] = list_table_rpl
        write_json_to_file(page_data)

    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None