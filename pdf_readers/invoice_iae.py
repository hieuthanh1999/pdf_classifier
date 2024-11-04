
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
def classifier_invoice_iae(pages):
    try:
        page_data = {}
        dict_total = {}
        list_table = []
        extracting = False
        charges = []
        total_amount = None
        pattern = re.compile(
            r'(?P<description>.+?)\s{2,}(?P<condition>.+?)\s{2,}(?P<qty_uom>\d+\.\d{3}\w{2})\s{2,}(?P<unit_price>\$\d{1,3}(?:,\d{3})*\.\d{2})\s{2,}(?P<net_price>\$\d{1,3}(?:,\d{3})*\.\d{2})'
        )
        total_pattern = re.compile(r'Total amount due\s+(?P<total_amount>\$\d{1,3}(?:,\d{3})*\.\d{2})')
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                match = pattern.search(line)
        
                if match:
                    description = match.group('description')
                    condition = match.group('condition')
                    qty_uom = match.group('qty_uom')
                    unit_price = match.group('unit_price')
                    net_price = match.group('net_price')

                    model =  Details()
                    model.description = description
                    model.condition = condition
                    model.qty_uom = qty_uom
                    model.unit_price = unit_price
                    model.net_price = net_price
                    list_table.append(model.to_dict())
                total_match = total_pattern.search(line)
                if total_match:
                    total_amount_due = total_match.group('total_amount')
                    page_data['total_amount_due'] = total_amount_due

        page_data['table'] = list_table
        #write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))          

        #print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
