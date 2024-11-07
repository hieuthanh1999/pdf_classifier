
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
def classifier_invoice_epcor(pages):
    try:
        list_table = []
        page_data = {}
        regex = r"([A-Za-z ]+)\s+([A-Za-z ]+)\s+(\d+\.\d{2})\s+(-?\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\d{1,3}(?:,\d{3})*\.\d{2})"
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                print(line)
                logger.info("%s", line)
                if "Invoice #:" in line:
                    try:
                        match = re.search(r"Invoice #:\s*(.*)", line)
                        if match:
                            page_data['invoice_no'] = match.group(1).strip()
                    except: 
                        page_data['invoice_no'] = ''

                elif "Invoice Date" in line: 
                    try:
                        match = re.search(r"Invoice Date:\s*(.*)", line)
                        if match:
                            page_data['invoice_date'] = match.group(1).strip()
                    except: 
                        page_data['invoice_date'] = ''
                elif "Customer Reference #:" in line:
                    try:
                        match = re.search(r"Customer Reference #:\s*(.*)", line)
                        if match:
                            page_data['customer_reference'] = match.group(1).strip()
                    except: 
                        page_data['customer_reference'] = ''
                elif "Work Order #:" in line:
                    try:
                        match = re.search(r"Work Order #:\s*(.*)", line)
                        if match:
                            page_data['work_order'] = match.group(1).strip()
                    except: 
                        page_data['serial_number'] = ''
                elif "Net amount" in line:
                    try:
                        match = re.search(r"Net amount\s*(\d{1,3}(?:,\d{3})*\.\d{2})", line)
                        if match:
                            page_data['net_amount'] = to_float(match.group(1).strip())
                    except: 
                        page_data['net_amount'] = 0
                elif "Total amount" in line:
                    print(line)
                    try:
                        match = re.search(r'Total amount incl\. VAT (\d{1,3}(?:,\d{3})*(?:\.\d{2})?) USD', line)
                        if match:
                            page_data['total_amount'] = to_float(match.group(1).strip())
                    except: 
                        page_data['total_amount'] = 0
                elif "VAT" in line:
                    try:
                        match = re.search(r'VAT\s(\d+\.\d{2})\s%\s(\d+\.\d{2})\sUSD', line)
                        if match:
                            page_data['vat_percent'] = to_float(match.group(1).strip())
                            page_data['vat'] = to_float(match.group(2).strip())
                    except: 
                        page_data['vat'] = 0
                        page_data['vat_percent'] = 0
                else:
                    match = re.search(regex,line.strip())
                    if match:
                        detail = Details()
                        try:
                            detail.category = match.group(1).strip()
                        except:
                            detail.category = ''
                        try:
                            detail.description = match.group(2).strip()
                        except:
                            detail.description = ''
                        try:
                            detail.quantity =to_int(match.group(3).strip())
                        except:
                            detail.quantity = 0
                        try:
                            detail.unit_price = to_float(match.group(4).strip())
                        except:
                            detail.unit_price = 0
                        try:
                            detail.total_price = to_float(match.group(5).strip())
                        except:
                            detail.total_price = 0
                        list_table.append(detail.to_dict())
            page_data['table'] = list_table

        write_json_to_file(page_data)    
    except Exception as e:
        print(f"Error: {e}")
        return None
@time_execution
def classifier_invoice_epcor_2(pages):
    try:
        list_table_power_section = []
        list_table_gearbox = []
        list_table_nte_exclusions = []
        page_data = {}
        pattern = re.compile(r"([A-Za-z0-9-]+)\s+([A-Za-z0-9\s,]+)\s+(\d+)\s+([A-Za-z0-9]{2})\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\$\s*(?:\$(.*))?$")
        for p_idx, page in enumerate(pages):
            print()
            text = page.extract_text().split('\n')
            power_section = False
            gearbox = False
            nte_exclusions = False
            for i, line in enumerate(text):
                print(line)
                logger.info("%s", line)
                if "EPCOR Order #:" in line:
                    try:
                        match = re.search(r"EPCOR Order #: \s*(.*)", line)
                        if match:
                            page_data['epcor_order'] = match.group(1).strip()
                    except: 
                        page_data['epcor_order'] = ''

                elif "Date Quote" in line: 
                    try:
                        match = re.search(r"Date Quote:\s*(.*)", line)
                        if match:
                            page_data['date_quote'] = match.group(1).strip()
                    except: 
                        page_data['date_quote'] = ''
                elif "Customer Reference" in line:
                    try:
                        match = re.search(r"Customer Reference:\s*(.*)", line)
                        if match:
                            page_data['customer_reference'] = match.group(1).strip()
                    except: 
                        page_data['customer_reference'] = ''
                elif "Work Order #:" in line:
                    try:
                        match = re.search(r"Work Order #:\s*(.*)", line)
                        if match:
                            page_data['work_order'] = match.group(1).strip()
                    except: 
                        page_data['serial_number'] = ''
                elif "Net amount" in line:
                    try:
                        match = re.search(r"Net amount\s*(\d{1,3}(?:,\d{3})*\.\d{2})", line)
                        if match:
                            page_data['net_amount'] = to_float(match.group(1).strip())
                    except: 
                        page_data['net_amount'] = 0
                elif "Total amount" in line:
                    print(line)
                    try:
                        match = re.search(r'Total amount incl\. VAT (\d{1,3}(?:,\d{3})*(?:\.\d{2})?) USD', line)
                        if match:
                            page_data['total_amount'] = to_float(match.group(1).strip())
                    except: 
                        page_data['total_amount'] = 0
                else:
                    """Extracting data from Power section"""
                    try:
                        if 'Power section' in line:
                            power_section = True
                        pass
                    except: pass
                    if power_section:
                            if 'Total Power section' in line:
                                values = line.split('$')
                                total_power_section = to_float(to_string(values[1].replace(' ', '')))
                                page_data['total_power_section'] = total_power_section
                                power_section = False
                            else:
                                match = re.search(pattern, line)
                                if match:
                                    print(match.group(1))
                                    model = Details("")
                                    model.part_number = match.group(1)
                                    model.description = match.group(2)
                                    model.quantity = match.group(3)
                                    model.category = match.group(4)
                                    model.costea = match.group(5)
                                    model.total_cost_estimate = match.group(6)
                                    model.comment = match.group(7)
                                    list_table_power_section.append(model.to_dict())
                    # """
                    # Extracting data from Contract repair Parts List
                    # """
                    # try:
                    #     if 'Contract repair Parts List' in line:
                    #         contract_repair_part_list = True
                    #     pass
                    # except: pass
                    # if contract_repair_part_list:
                    #     if 'B1--小计/SUBTOTAL (USD) :' in line:
                    #         values = line.split('$')
                    #         sub_total_total_price =to_float(to_string(values[1].replace(' ', '')))
                    #         sub_total_subcontract_fee = to_float(to_string(values[2]).replace(' ', ''))
                    #         crpl_total['sub_total_total_price'] = sub_total_total_price
                    #         crpl_total['sub_total_subcontract_fee'] = sub_total_subcontract_fee
                    #     elif 'B3—合计TOTAL (USD)' in line:
                    #         values = line.split('$')
                    #         total = to_float(to_string(values[1].replace(' ', '')))
                    #         crpl_total['total'] = total
                    #         contract_repair_part_list = False
                    #     else:
                    #         pattern = r"(\d+)\s+(\d{7}-\d+)\s+([\w\s,/\-()]+)\s+(\d+)\s+(\w+)\s+(?:([\d,]+(?:\.\d+)?)|\/)\s+\$\s+([\d,]+(?:\.\d+)?)\s+\$\s+([\d,]+(?:\.\d+)?)\s+\$\s+([\d,]+(?:\.\d+)?)?\s*([\w\s]*)?"
                    #         match = re.search(pattern, line)
                    #         if match:
                    #             model = Details("")
                    #             model.item = match.group(1)
                    #             model.part_number = match.group(2)
                    #             model.description = match.group(3)
                    #             model.quantity = match.group(4)
                    #             model.cunit = match.group(5)
                    #             model.usdunit = match.group(6)
                    #             model.total_price = match.group(8)
                    #             model.subcontract_fees = match.group(9)
                    #             model.remarks = match.group(10)
                    #             list_table_crpl.append(model.to_dict())
                    # """Extracting data from LRU List"""
                    # try:
                    #     if 'LRU List' in line:
                    #         lru_list = True  
                    #     pass
                    # except: pass
                    # if lru_list:
                    #     if 'C1--小计/SUBTOTAL (USD) :' in line:
                    #         values = line.split('$')
                    #         sub_total_total_price =to_float(to_string(values[1].replace(' ', '')))
                    #         sub_total_handling = to_float(to_string(values[2]).replace(' ', ''))
                    #         lru_total['sub_total_total_price'] = sub_total_total_price
                    #         lru_total['sub_total_handling_fee'] = sub_total_handling
                    #     elif 'C2--Testing fees测试费用 (USD)' in line:
                    #         values = line.split('$')
                    #         handling_fee = to_float(to_string(values[1].replace(' ', '')))
                    #         lru_total['testing_fee'] = handling_fee
                    #     elif 'C3--Subcontract修理费用 (USD)' in line:
                    #         values = line.split('$')
                    #         sub_total_subcontract_fee = to_float(to_string(values[1].replace(' ', '')))
                    #         lru_total['sub_total_subcontract_fee'] = sub_total_subcontract_fee
                    #     elif 'C5—合计TOTAL (USD)' in line:
                    #         values = line.split('$')
                    #         total = to_float(to_string(values[1].replace(' ', '')))
                    #         lru_total['total'] = total
                    #         lru_list = False
                    #     else:
                    #         pattern = r'(\d+)\s+([A-Za-z0-9-]+)\s+(.+?)\s+(\d+)\s+(EA|SET)\s+\$\s+([\d,]+\.\d{2})\s+\$\s+([\d,]+\.\d{2})(?:\s+\$\s+([\d,]+\.\d{2}))?\s*(.+)?'
                    #         match = re.search(pattern, line)
                    #         if match:
                    #             model = Details("")
                    #             model.item = match.group(1)
                    #             model.part_number = match.group(2)
                    #             model.description = match.group(3)
                    #             model.quantity = match.group(4)
                    #             model.unit = match.group(5)
                    #             model.usdunit = match.group(6)
                    #             model.total_price = match.group(7)
                    #             model.handling = match.group(8)
                    #             model.remarks = match.group(9)
                    #             list_table_lru.append(model.to_dict()) 
            page_data['table_power_section'] = list_table_power_section

        write_json_to_file(page_data)    
    except Exception as e:
        print(f"Error: {e}")
        return None
    