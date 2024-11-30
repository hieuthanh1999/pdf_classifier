
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
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

@time_execution
def classifier_invoice_credit(pages):
    try:
        invoice = Invoice()
        key = keyword(credit)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, e in enumerate(text):
                #invoice
                try:
                    if key.invoice_no in e:
                        if i + 1 < len(text):
                            next_line = text[i + 1].strip()
                            if next_line:
                                data_array = next_line.split()
                                invoice.inv_no = data_array[1]
                except: invoice.inv_no = ''
                #credit note
                try:
                    if key.credit_note in e:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.credit_note = to_float(number)
                        else : invoice.credit_note = 0
                except: pass
                #total credit and currency
                try:
                    if key.total_credit in e:
                        total_credit = re.search(r'([A-Z]{3})\s*-\s*([-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?)', e)
                        if total_credit:
                            currency = total_credit.group(1)
                            price = total_credit.group(2)
                            invoice.total_credit = to_float(price)
                            invoice.currency_credit = currency
                        else : 
                            invoice.total_credit = 0
                            invoice.currency_credit = 'USD'
                            #logger.info("Data PDF NEXT LINE: %s", invoice.to_string()) 
                except: pass
        #0.2s
        print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None


@time_execution
def classifier_invoice_lc_ge(path, poppler_path, pytesseract):
    try:
        key = keyword(credit)
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
        pattern_invoice = r'(\d+)\s+([a-z]{2}|\d*)\s+([a-z]{2}|\d{2}-[A-Z]{3}-\d{4})?'
        for p_idx, page in enumerate(pages):
            text = pytesseract.image_to_string(page, config=custom_config)
            # for i, text in enumerate(data):
            #     logger.info("data: %s", str(text))
            text = text.split('\n')
            for i, line_row in enumerate(text):
                line_row = line_row.strip()
                logger.info("line_row: %s", line_row)
                #invoice
                try:
                    if key.invoice_no in line_row:
                        if i + 1 < len(text):
                            next_line = text[i + 1].strip()
                            if next_line:
                                match = re.search(pattern_invoice, next_line)
                                if match:   
                                    page_data['engine_serial_no'] = match.group(1) if match.group(1) else ""
                                    page_data['invoice_no'] = match.group(2) if match.group(2) and not re.match(r'[a-z]{2}', match.group(2)) else ""
                                    page_data['invoice_date'] = match.group(3) if match.group(3) and not re.match(r'[a-z]{2}', match.group(3)) else ""
                except:
                    page_data['engine_serial_no'] = ""
                    page_data['invoice_no'] = ""
                    page_data['invoice_date'] = ""
 
                if 'REPAIR OF' in line_row:
                    extracting = True
                    continue
                if 'INVOICE TOTAL' in line_row:
                    logger.info("%s", line_row)
                    extracting = False
                    total_pattern = r'INVOICE TOTAL[:\uFF1A]?\s(USD|EUR|GBP|JPY|CNY)\s([\d,]+\.\d{2})'

                    total_match = re.search(total_pattern, line_row)
                    if total_match:
                        total_amount = to_float(total_match.group(2))
                        currency = total_match.group(1) 
                        dict_total['amount'] = total_amount
                        dict_total['currency'] = currency
                        page_data['total_amount'] = dict_total
                    break
                if extracting:
                    charge_pattern = r'(.+?)\s([\d,]+\.\d{2})'
                    charge_match = re.search(charge_pattern, line_row)
                    if charge_match:
                        
                        model =  Details()
                        description = charge_match.group(1).strip() if charge_match.group(1) else ""
                        total = to_float(charge_match.group(2)) if charge_match.group(2) else ""

                        model.description = description
                        model.total = total
                        
                        list_table.append(model.to_dict())
        page_data['description'] = list_table

        print(json.dumps(page_data, indent=4))  
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None