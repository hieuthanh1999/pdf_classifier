
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
