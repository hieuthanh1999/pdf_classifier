
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
def classifier_invoice_stand_aero(pages):
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
                logger.info("%s", line_row)
               
        #print(invoice.to_string())           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
