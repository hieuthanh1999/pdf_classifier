
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

def clean_value(value):
    return value.replace('_', '')

@time_execution
def classifier_invoice_klm(pages):
    try:
        page_data = {}
        key_data = {}
        list_table = []
        inv = Invoice()
        table_started = False
        for p_idx, page in enumerate(pages):
            text = page.extract_text()
            if text is None:
                continue

            text_lines = text.split('\n')

            for line in text_lines:
                try:
                    try:
                        # Trích xuất "INVOICE :"
                        invoice_number_match = re.search(r"INVOICE\s*[:\-]?\s*(\S+)", line)
                        if invoice_number_match:
                            page_data['invoice_number'] = invoice_number_match.group(1).strip()
                    except:
                        page_data['invoice_number'] = '' 
                    # Trích xuất "Invoice date :"
                    try:
                        invoice_date_match = re.search(r"Invoice\s*date\s*[:\-]?\s*(\d{2}\s*[A-Za-z]{3}\s*\d{2})", line)
                        if invoice_date_match:
                            page_data['invoice_date'] = invoice_date_match.group(1).strip()
                    except:
                        page_data['invoice_date'] = '' 
                    # Trích xuất "Int. Ref. :"
                    try:
                        int_ref_match = re.search(r"Int\.\s*Ref\.\s*[:\-]?\s*(\S+)", line)
                        if int_ref_match:
                            page_data['int_ref'] = int_ref_match.group(1).strip()
                    except:
                        page_data['int_ref'] = '' 
                    # Trích xuất "Customer :"
                    try:
                        customer_match = re.search(r"Customer\s*[:\-]?\s*(\S+)", line)
                        if customer_match:
                            page_data['customer'] = customer_match.group(1).strip()
                    except:
                        page_data['customer'] = ''
                    # Trích xuất "Customer support mngr:"
                    try:
                        customer_support_mngr_match = re.search(r"Customer\s*support\s*mngr\s*[:\-]?\s*(.+)", line)
                        if customer_support_mngr_match:
                            page_data['customer_support_mngr'] = customer_support_mngr_match.group(1).strip()
                    except:
                        page_data['customer_support_mngr'] = ''
                    # Trích xuất "MU :"
                    try:
                        mu_match = re.search(r"MU\s*[:\-]?\s*(\S+)", line)
                        if mu_match:
                            page_data['mu'] = mu_match.group(1).strip()
                    except:
                        page_data['mu'] = ''
                    # Loại bỏ "MU" khỏi customer_support_mngr nếu đã có giá trị trong mu
                    try:
                        if page_data['mu'] and page_data['customer_support_mngr'] and 'MU' in page_data['customer_support_mngr']:
                            page_data['customer_support_mngr'] = page_data['customer_support_mngr'].replace(f"MU : {page_data['mu']}", "").strip()
                    except:
                        page_data['customer_support_mngr'] = ''
                    # Trích xuất "VAT reg. :"
                    try:
                        vat_reg_match = re.search(r"VAT\s*reg\.\s*[:\-]?\s*(.*?)\s*Contract\s*number\s*[:\-]?", line)
                        if vat_reg_match:
                            page_data['vat_reg'] = vat_reg_match.group(1).strip()
                        else:
                            page_data['vat_reg'] = ''
                    except:
                        page_data['vat_reg'] = ''
                    # Trích xuất "Contract number :"
                    try:
                        contract_number_match = re.search(r"Contract\s*number\s*[:\-]?\s*(\S+)", line)
                        if contract_number_match:
                            page_data['contract_number'] = contract_number_match.group(1).strip()
                    except:
                        page_data['contract_number'] = ''
                    # Trích xuất "Order :"
                    try:
                        order_match = re.search(r"Order\s*[:\-]?\s*(\S+)", line)
                        if order_match:
                            page_data['order']= order_match.group(1).strip()
                    except:
                        page_data['order'] = ''

                    try:
                        order_match = re.search(r"Your\s*order:\s*(.*)", line)
                        if order_match:
                            page_data['your_order'] = order_match.group(1).strip()
                    except:
                        page_data['your_order'] = ''

                    # Trích xuất thông tin "Billing month:"
                    try:
                        billing_month_match = re.search(r"Billing\s*month:\s*(.*)", line)
                        if billing_month_match:
                            page_data['billing_month'] = billing_month_match.group(1).strip()
                    except:
                        page_data['your_order'] = ''
                    try:
                        pattern = r"^([\w\s]+)\s+([\d,]+(?:\.\d+)?)\s+([A-Za-z]+)\s+([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)$"
                        matches = re.findall(pattern, line, re.MULTILINE)
                        for match in matches:
                            description, quantity, uom, amount, total_usd = match
                            model = Details()
                            model.description = description.strip()
                            model.Quantity = quantity
                            model.UOM = uom
                            model.Amount = amount
                            model.total_usd = total_usd
                            list_table.append(model.to_dict())
                    except:
                        list_table.append(model.to_dict())

                    pattern_total_excl_vat  = r"Total\s+amount\s+excl\s+V\.A\.T\.\s+USD\s+([\d,]+\.\d{2})"
                    pattern_total_incl_vat  =  r"Total amount incl V\.A\.T\.\s+USD\s+([0-9_\,\.]+)"
                    # Apply the regex pattern to extract values
                    match_total_excl_vat = re.search(pattern_total_excl_vat, line)

                    pattern_vat = r"V\.A\.T\.\s+([\d,]+(?:\.\d{1,2})?)\s+%\s+USD\s+([0-9_\.]+)"
                    match_vat = re.search(pattern_vat, line)
                    match_total_incl_vat  = re.search(pattern_total_incl_vat, line)

                    if match_total_excl_vat:
                        try:
                            page_data['total_excl_vat'] = match_total_excl_vat.group(1)
                        except:
                            page_data['total_excl_vat'] = ''
                        # logger.info("%s", total_excl_vat)
                    if match_vat:
                        try:
                            page_data['vat_percent'] = clean_value(match_vat.group(1))
                        except:
                            page_data['vat_percent'] = ''
                        try:
                            page_data['vat_value'] = clean_value(match_vat.group(2))
                        except:
                            page_data['vat_value'] = ''
                        #logger.info("%s --- %s ", vat_percent,  vat_value)
                    
                    if match_total_incl_vat:
                        try:
                            page_data['total_incl_vat'] = clean_value(match_total_incl_vat.group(1))
                        except:
                            page_data['total_incl_vat'] = ''
                        #logger.info("%s", total_excl_vat)

                except Exception as e:
                    logger.error("Error processing line: %s, error: %s", line, str(e))
        page_data['table'] = list_table
        print(json.dumps(page_data, indent=4))
    except Exception as e:
        logger.error("Error invoice smbc: %s", str(e))
        return None