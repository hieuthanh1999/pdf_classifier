
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
        list_table_description = {}
        list_table_rotable_special_process = []
        list_table_new_parts = []
        list_table_new_lcf_parts = []
        list_serviceable_parts = []
        list_serviceable_lcf_parts = []
        list_specially_priced_serviceable_parts = []
        list_table_components_repair = []
        replacement_parts = False
        rotable_special_process = False
        first_replacement_parts = False
        extracted_replace_parts = False
        specially_priced_serviceable_parts = False
        new_lcf_parts = False
        new_parts = False
        serviceable_parts = False
        serviceable_lcf_parts = False
        components_repair = False
        key = keyword(stand_aero)
        regex_new_parts = r'(\S+)\s+([A-Za-z0-9\s,#./()%]+)\s+(\d+)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        regex_rotable_special_process = r'(\S+)\s+([A-Za-z0-9\s,#/().]*)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+([\d-]+)'
        regex_replacements_parts = r'^(?!Less:)([A-Za-z\s]+)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        regex_replacements_parts_discount = r'Less:\s*([A-Za-z\s]+)\s+(\d{1,3}(?:\.\d+)?%)\s+\(\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line_row in enumerate(text):
                line_row = line_row.strip()
                #print(line_row)
                if key.labor in line_row:
                    list_table_description[key.labor] = extract_value(line_row, key.labor)
                if key.component_repair in line_row:
                    list_table_description[key.component_repair] = extract_value(line_row, key.component_repair)
                if key.replacement_parts in line_row and not first_replacement_parts:
                    first_replacement_parts = True
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
                if key.TOTAL in line_row and 'USD' in line_row:
                    list_table_description[key.TOTAL] = extract_value(line_row, key.TOTAL)
                if key.invoice_number in line_row:
                    line_row = line_row.replace(' ', '')
                    match = re.search(r'Invoice#:(\d+)', line_row)
                    if match:
                        page_data[key.invoice_number] = match.group(1)
                if key.date in line_row:
                    print(list_table_description)
                    line_row = line_row.replace(' ', '')
                    match = re.search(r'Date:\s*(\d{4}-[A-Za-z]{3}-\d{2})', line_row)
                    if match:
                        date_value = match.group(1)
                        page_data[key.date] = date_value
                if 'REPLACEMENT PARTS' in line_row and not extracted_replace_parts:
                    replacement_parts = True
                if replacement_parts:
                    #print('in-rp')
                    if 'TOTAL PARTS' in line_row:
                        replacement_parts = False
                        extracted_replace_parts = True
                        page_data['total_parts'] = extract_value(line_row, '')
                    else:
                        match = re.search(regex_replacements_parts, line_row)
                        if match:
                            service_name = match.group(1)
                            list_table_description[service_name] = extract_value(line_row, service_name)
                            #print(i)
                            match = re.search(regex_replacements_parts_discount, text[i+1])
                            if match:
                                list_table_description[service_name + 'Actual'] = to_float(match.group(4))
                                list_table_description[match.group(1)] = to_float(match.group(2))
                                list_table_description[service_name + 'Minus'] = to_float(match.group(3))    
                if 'ROTABLE / SPECIAL PROCESS' in line_row:
                    rotable_special_process = True
                if rotable_special_process:
                    if 'TOTAL ROTABLE / SPECIAL PROCESS' in line_row:
                        rotable_special_process = False
                        page_data['total_rotable_special_process'] = extract_value(line_row, '')
                    else:
                        #print(line_row)
                        match = re.search(regex_rotable_special_process, line_row)
                        if match:
                            print(match.groups())
                            model = Details()
                            model.part_number = match.group(1)
                            model.description = match.group(2)
                            model.total = to_float(match.group(3))
                            model.reference = match.group(4)
                            list_table_rotable_special_process.append(model.to_dict())
                if 'NEW PARTS' in line_row:
                    new_parts = True
                if new_parts:
                    if 'TOTAL NEW PARTS' in line_row:
                        new_parts = False
                        page_data['total_new_parts'] = extract_value(line_row, '')
                    else:
                        match = re.search(regex_new_parts, line_row)
                        if match:
                            model = Details()
                            model.part_number = match.group(1)
                            model.description = match.group(2)
                            model.quantity = to_float(match.group(3))
                            model.list = to_float(match.group(4))
                            model.total = to_float(match.group(5))
                            list_table_new_parts.append(model.to_dict())
                if 'NEW LCF PARTS' in line_row:
                    new_lcf_parts = True
                if new_lcf_parts:
                    if 'TOTAL NEW LCF PARTS' in line_row:
                        new_lcf_parts = False
                        page_data['total_new_lcf_parts'] = extract_value(line_row, '')
                    else:
                        match = re.search(regex_new_parts, line_row)
                        if match:
                            model = Details()
                            model.part_number = match.group(1)
                            model.description = match.group(2)
                            model.quantity = to_float(match.group(3))
                            model.list = to_float(match.group(4))
                            model.total = to_float(match.group(5))
                            list_table_new_lcf_parts.append(model.to_dict())
                if 'SERVICEABLE PARTS' in line_row:
                    serviceable_parts = True
                if serviceable_parts:
                    if 'TOTAL SERVICEABLE PARTS' in line_row:
                        serviceable_parts = False
                        page_data['total_serviceable_parts'] = extract_value(line_row, '')
                    else:
                        match = re.search(regex_new_parts, line_row)
                        if match:
                            model = Details()
                            model.part_number = match.group(1)
                            model.description = match.group(2)
                            model.quantity = to_float(match.group(3))
                            model.list = to_float(match.group(4))
                            model.total = to_float(match.group(5))
                            list_serviceable_parts.append(model.to_dict())
                if 'SERVICEABLE LCF PARTS' in line_row:
                    serviceable_lcf_parts = True
                if serviceable_lcf_parts:
                    if 'TOTAL SERVICEABLE LCF PARTS' in line_row:
                        serviceable_lcf_parts = False
                        page_data['total_serviceable_lcf_parts'] = extract_value(line_row, '')
                    else:
                        match = re.search(regex_new_parts, line_row)
                        if match:
                            model = Details()
                            model.part_number = match.group(1)
                            model.description = match.group(2)
                            model.quantity = to_float(match.group(3))
                            model.list = to_float(match.group(4))
                            model.total = to_float(match.group(5))
                            list_serviceable_lcf_parts.append(model.to_dict())
                if 'SPECIALLY PRICED SERVICEABLE PARTS' in line_row:
                    specially_priced_serviceable_parts = True
                if specially_priced_serviceable_parts:
                    if 'TOTAL SPECIALLY PRICED SERVICEABLE PARTS' in line_row:
                        specially_priced_serviceable_parts = False
                        page_data['total_specially_priced_serviceable_parts'] = extract_value(line_row, '')
                    else:
                        match = re.search(regex_new_parts, line_row)
                        if match:
                            model = Details()
                            model.part_number = match.group(1)
                            model.description = match.group(2)
                            model.quantity = to_float(match.group(3))
                            model.list = to_float(match.group(4))
                            model.total = to_float(match.group(5))
                            list_specially_priced_serviceable_parts.append(model.to_dict())
                #print(line_row)
                logger.info("%s", line_row)
        page_data['description'] = list_table_description   
        page_data['rotable_special_process'] = list_table_rotable_special_process
        page_data['new_parts'] = list_table_new_parts
        page_data['serviceable_parts'] = list_serviceable_parts
        page_data['serviceable_lcf_parts'] = list_serviceable_lcf_parts
        page_data['specially_priced_serviceable_parts'] = list_specially_priced_serviceable_parts
        # write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))
        #print(page_data)       
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
