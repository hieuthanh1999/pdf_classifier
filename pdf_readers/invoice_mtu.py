
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

def process_table_row(row):
    return [cell if cell is not None and cell.strip() != '' else 'N/A' for cell in row]
    
@time_execution
def classifier_lc_mtu_invoice(pages):
    try:
        page_data = {}
        key = keyword(honey_well)
        for p_idx, page in enumerate(pages):
            logger.info("%s", page)
            text = page.extract_text().split('\n')
            for i, line_row in enumerate(text):
                logger.info("%s", line_row)
        # write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))
        #print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
