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
        item = {}
        object_lv = {}
        object_root = {}
        sumary = {}
        have_sub = False
        list_object_root = []
        list_object = []
        list_table_sumary = []
        list_text = []
        list_table_partial_invoice_value = []
        list_table_miscellaneous = []
        list_table_fixed_price = []
        list_table_material_consumption = []
        list_table_labour = []
        invoice_no = False
        fixed_price = False
        material_consumption = False
        labour = False
        partial_invoice_value= False
        miscellaneous = False
        extract_sumary = False
        extracting_data = False
        fixed_price_parts_repair = False
        list_table_fixed_price_parts_repair = []
        regex_sumary = r"(\d*)\s+([\w\s,./()-]+)\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s+\((\d+|\d{1,3}(?:\.\d{3})*,\d{2})\)"
        regex_partial_invoice_value = r'(.+?)\s+(\d+)\s+(\w+)\s+([\d.,-]+)\s+([\d.,-]+)\s+([\d.,-]+)'
        regex_fixed_price = r'^(.*?)\s+(\d+)\s+(\w+)\s+([\d.,]+)\s+([\d.,]+)$'
        regex_miscellaneous = r'(.+?)\s+([\d.,-]+)\s+([\d.,-]+)'
        regex_fixed_price_parts_repair = r'^(\S+)\s+(.+?)\s+(\w{3})\s+(\d+)\s+(\w+)\s+([\d.,]+)\s+([\d.,]+)$'
        regex_material_consumption = r'^(\S+)\s+(.+?)\s+(\d+)\s+(\w+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)$'
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
                    partial_invoice_value = True
                    sumary[key.partial_invoice_value] = extract_value(line_row, key.partial_invoice_value)
                elif partial_invoice_value:
                    if '*' in line_row and not key.invoice_number in line_row:
                        partial_invoice_value = False
                    else:
                        match = re.search(regex_partial_invoice_value, line_row)
                        if match:
                            model = Details()
                            model.description = match.group(1)
                            model.quantity = match.group(2)
                            model.unit = match.group(3)
                            model.rate = to_float(match.group(4))
                            model.amount = to_float(match.group(5))
                            list_table_partial_invoice_value.append(model.to_dict())
                if key.miscellaneous in line_row:
                    sumary[key.miscellaneous] = extract_value(line_row, key.miscellaneous)
                    miscellaneous = True
                elif miscellaneous:
                    if '*' in line_row:
                        miscellaneous = False
                    else:
                        match = re.search(regex_miscellaneous, line_row)
                        if match:
                            print('in misc', match.groups())
                            model = Details()
                            model.description = match.group(1)
                            model.amount = to_float(match.group(2))
                            list_table_miscellaneous.append(model.to_dict())
                if line_row.count('*') == 1 and not key.partial_invoice_value in line_row and not key.miscellaneous in line_row:
                    have_sub = False
                    fixed_price = False
                    fixed_price_parts_repair = False
                    object_root = {}
                    list_object = []
                    match = re.search(r'\* ([^\d,]+)', line_row)
                    if match:
                        object_root['name'] = match.group(1).strip()
                    if text[i+1].count('*') == 2 and text[i+2].count('*') == 3:
                        have_sub = True
                    else:
                        pass
                    list_object_root.append(object_root)     
                    page_data['sumarys'] = list_object_root
                    #print('in')
                if have_sub:
                    if line_row.count('*') == 2:
                        object_lv = {}
                        object_lv['name'] = re.search(r'\* ([^\d,]+)', line_row).group(1).strip()
        
                match = re.search(r'\* ([^\d,]+)', line_row)
                name = ''
                if match:
                    name = match.group(1).strip()
                if name == key.fixed_price: 
                    fixed_price = True    
                elif fixed_price:
                    #print(line_row)
                    match = re.search(regex_fixed_price, line_row)
                    if match:
                        model = Details()
                        model.description = match.group(1)
                        model.quantity =to_int(match.group(2))
                        model.unit = match.group(3)
                        model.unit_price = to_float(match.group(4))
                        model.total_price = to_float(match.group(5))
                        list_table_fixed_price.append(model.to_dict())
                    elif line_row.count('*') == 2 or line_row.count('*') == 3:
                        fixed_price = False
                        if have_sub:
                            object_lv['fixed_price'] = list_table_fixed_price
                            list_object.append(object_lv)
                        else:
                            object_root['fixed_price'] = list_table_fixed_price
                if name == key.fixed_price_parts_repair:
                    fixed_price_parts_repair = True
                elif fixed_price_parts_repair:
                    line_row = line_row.replace('_', '')
                    match = re.search(regex_fixed_price_parts_repair, line_row)
                    if match:
                        model = Details()
                        model.part_no = match.group(1)
                        model.description = match.group(2)
                        model.work_package = match.group(3)
                        model.quantity = to_int(match.group(4)) 
                        model.unit = match.group(5)
                        model.unit_price = to_float(match.group(6))
                        model.total_price = to_float(match.group(7))
                        list_table_fixed_price_parts_repair.append(model.to_dict())
                    elif line_row.count('*') == 2 or line_row.count('*') == 3:
                        fixed_price_parts_repair = False
                        if have_sub:
                            object_lv['fixed_price_parts_repair'] = list_table_fixed_price_parts_repair
                            list_table_fixed_price_parts_repair.clear()
                            list_object.append(object_lv)
                        else:
                            print('in fixed_price_parts_repair 2')
                            object_root['fixed_price_parts_repair'] = list_table_fixed_price_parts_repair
                            print(list_table_fixed_price_parts_repair)
                            list_table_fixed_price_parts_repair.clear()
                            print(list_table_fixed_price_parts_repair)
                if name == key.material_consumption:
                    material_consumption = True
                elif material_consumption:
                    #print(line_row)
                    match = re.search(regex_material_consumption, line_row)
                    if match:
                        model = Details()
                        model.part_no = match.group(1)
                        model.description = match.group(2)
                        model.quantity = to_int(match.group(3))
                        model.unit = match.group(4)
                        model.unit_price = to_float(match.group(5))
                        model.amount = to_float(match.group(6))
                        model.handling_percent = to_float(match.group(7))
                        model.handling_amount = to_float(match.group(8))
                        model.total_amount = to_float(match.group(9))

                        list_table_material_consumption.append(model.to_dict())
                    elif line_row.count('*') == 2 or line_row.count('*') == 3:
                        material_consumption = False
                        if have_sub:
                            object_lv['material_consumption'] = list_table_material_consumption
                            list_object.append(object_lv)
                        else:
                            object_root['material_consumption'] = list_table_material_consumption
                if name == key.labour:
                    labour = True
                elif labour:
                    #print(line_row)
                    match = re.search(regex_partial_invoice_value, line_row)
                    if match:
                        model = Details()
                        model.description = match.group(1)
                        model.quantity = to_int(match.group(2))
                        model.unit = match.group(3)
                        model.rate = to_float(match.group(4))
                        model.amount = to_float(match.group(5))
                        list_table_labour.append(model.to_dict())
                    elif line_row.count('*') == 2 or line_row.count('*') == 3:
                        labour = False
                        if have_sub:
                            object_lv['labour'] = list_table_labour
                            list_object.append(object_lv)
                        else:
                            object_root['labour'] = list_table_labour
                # object_root['list_object'] = list_object           
                logger.info("%s", line_row)
                # print(object_root)
        page_data['sumary'] = sumary
        page_data['partial_invoice_value'] = list_table_partial_invoice_value
        page_data['miscellaneous'] = list_table_miscellaneous
        
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