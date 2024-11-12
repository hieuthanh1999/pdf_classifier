
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
def classifier_invoice_smbc(pages):
    try:
        page_data = {}
        key_data = {}
        list_table = []
        inv = Invoice()
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                try:
                    to_match = re.search(r"To\s*:\s*([\w\s,]+(?:\n.*?)*?)\s*Date\s*:", line, re.DOTALL)
                    if to_match:
                        inv.to = to_match.group(1).replace("\n", " ").strip()
                except:
                    inv.to = '' 
                try:
                    date_match = re.search(r"Date\s*:\s*([\w\s]+)", line)
                    if date_match:
                        inv.date = date_match.group(1).strip()
                except:
                    inv.date = '' 
               
                try:
                    invoice_number_match = re.search(r"Invoice\s#\s*:\s*([\w\-]+)", line)
                    if invoice_number_match:
                        inv.invoice_number = invoice_number_match.group(1).strip()
                except:
                    inv.invoice_number = ''
                try:    
                    from_match = re.search(r"From\s*:\s*([\w\s,.]+)", line)
                    if from_match:
                        inv.from_company = from_match.group(1).strip()
                except:
                    inv.from_company = ''
                try:
                    attn_match = re.search(r"Attn\s*:\s*([\w\s]+)", line)
                    if attn_match:
                        inv.attn = attn_match.group(1).strip()
                except:
                    inv.from_company = ''
                try:
                    email_match = re.search(r"E-mail\s*:\s*([\w@.]+)", line)
                    if email_match:
                        inv.email = email_match.group(1).strip()
                except:
                    inv.from_company = ''
                try:
                    fax_match = re.search(r"Fax\s#\s*:\s*([\+\d\s]+)", line)
                    if fax_match:
                        inv.fax = fax_match.group(1).strip()
                except:
                    inv.from_company = ''
                try:
                    due_amount_match = re.search(r"DUE AMOUNT\s*:\s*US\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", line)
                    if due_amount_match:
                        inv.due_amount = due_amount_match.group(1).strip()
                except:
                    inv.from_company = ''
                try:
                    due_date_match = re.search(r"DUE DATE\s*:\s*([\w\s]+)", line)
                    if due_date_match:
                        inv.due_date = due_date_match.group(1).strip()
                except:
                    inv.from_company = ''
                try:
                    vat_match = re.search(r"(\d+)% Dutch VAT", line)
                    if vat_match:
                        inv.vat_percentage = vat_match.group(1).strip()
                except:
                    inv.from_company = ''
                try:
                    period_covered_match = re.search(r"ERIOD COVERED\s*:\s*([\w\s~]+)", line)
                    if period_covered_match:
                        inv.period_covered = period_covered_match.group(1).strip()
                except:
                    inv.from_company = ''
        print(inv.to_string())                 
    except Exception as e:
        logger.error("Error invoice smbc: %s", str(e))
        return None
