
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

        # write_json_to_file(page_data)    
        print(json.dumps(page_data, indent=4))
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
        pattern = re.compile(r"^([A-Za-z0-9/-]+)\s+([A-Za-z0-9\s,./()-]+)\s+(\d+)\s+([A-Za-z0-9]+)\s+\$\s*([\d,]+\.\d{2})\s+\$\s*([\d,]+\.\d{2})(?:\s+(.*))?$")
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            power_section = False
            gearbox = False
            nte_exclusions = False
            for i, line in enumerate(text):
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
                elif "Customer reference" in line:
                    try:
                        match = re.search(r"Customer reference:\s*(.*)", line)
                        if match:
                            page_data['customer_reference'] = match.group(1).strip()
                    except: 
                        page_data['customer_reference'] = ''
                elif "Repair price" in line:
                    try:
                        repair_price = to_float(to_string(line.split('$')[1].replace(' ', '')))
                        page_data['repair_price'] = repair_price
                    except:
                        page_data['repair_price'] = 0
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
                                match = pattern.match(line)
                                if match:
                                    list_table_power_section.append(put_data(match))
                    """Extracting data from Gearbox"""
                    try:
                        if 'Gearbox' in line:
                            gearbox = True
                        pass
                    except: pass
                    if gearbox:
                            if 'Total Gearbox' in line:
                                values = line.split('$')
                                total_gearbox = to_float(to_string(values[1].replace(' ', '')))
                                page_data['total_gearbox'] = total_gearbox
                                gearbox = False
                            else:
                                match = pattern.match(line)
                                if match:
                                    list_table_gearbox.append(put_data(match))
                    """Extracting data from NTE Exclusions"""
                    try:
                        if 'NTE exclusions' in line:
                            nte_exclusions = True
                        pass
                    except: pass
                    if nte_exclusions:
                            if 'Total NTE exclusions' in line:
                                values = line.split('$')
                                total_nte_exclusions = to_float(to_string(values[1].replace(' ', '')))
                                page_data['total_nte_exclusions'] = total_nte_exclusions
                                nte_exclusions = False
                            else:
                                match = pattern.match(line)
                                if match:
                                    list_table_nte_exclusions.append(put_data(match))
                if "NTE" in line:
                    if "NTE Correction" in line:

                        try:
                            nte_correction = to_float(to_string(line.split('$')[1].replace(' ', '')))
                            page_data['nte_correction'] = nte_correction
                        except:
                            page_data['nte_correction'] = 0
                    elif re.search(r"NTE\s\$\s[\d,]+\.\d{2}", line):
                        try:
                            nte = to_float(to_string(line.split('$')[1].replace(' ', '')))
                            page_data['nte'] = nte
                        except:
                            page_data['nte'] = 0
            page_data['table_power_section'] = list_table_power_section
            page_data['table_gearbox'] = list_table_gearbox
            page_data['table_nte_exclusions'] = list_table_nte_exclusions
        # write_json_to_file(page_data)   
        print(json.dumps(page_data, indent=4)) 
    except Exception as e:
        print(f"Error: {e}")
        return None
@time_execution
def put_data(match):
    try:
        model = Details()
        model.part_number = match.group(1)
        model.description = remove_duplicate_characters(match.group(2))
        model.quantity = to_int(match.group(3))
        model.category = match.group(4)
        model.costea = to_float(match.group(5))
        model.total_cost_estimate = to_float(match.group(6))
        model.comment = match.group(7)
        return model.to_dict()
    except Exception as e:
        print(f"Error: {e}")
        return None   