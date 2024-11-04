
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
def classifier_invoice_invoice_epcor(pages):
    try:
        list_table = []
        page_data = {}
        for p_idx, page in enumerate(pages):
            # tables = page.extract_tables()
            # for table in tables:
            #     header = None
            #     for row in table:
            #         if "PN" in row:
            #             header = row
            #         elif header and any(row):
            #             print(f"Error: {e}")
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                logger.info("%s", line)
    except Exception as e:
        print(f"Error: {e}")
        return None