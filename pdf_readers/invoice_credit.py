
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
def classifier_invoice_lc_ge(path):
    try:
        pages = convert_from_path(path, dpi=300, poppler_path=r'/Users/hieuthanh/Desktop/OCR/pdf_classifier/Release-24/Library/bin')
        invoice_texts = []
        for p_idx, page in enumerate(pages):
            text = pytesseract.image_to_string(page, lang='eng') 
            invoice_texts.append(text)
            logger.info("Text from page %d: %s", p_idx + 1, text)
        
        # for p_idx, page in enumerate(pages):
        #     text = page.extract_text().split('\n')
        #     logger.info("%s", text)     
        #     for i, e in enumerate(text):
        #         logger.info("%s", e)          
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None