
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
        check_covered = True
        check_o = True
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

                try:
                    if "NTE CAP" in e:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.nte_cap = to_float(number)
                        else : invoice.nte_cap = 0
                except: pass

                try:
                    if "Covered" in e:
                        check_covered = False
                        check_o = True
                except: pass

                try:
                    if "FPLS" in e and not check_covered and check_o:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.covered_fpls = to_float(number)
                        else : invoice.covered_fpls= 0
                except: pass

                try:
                    if "Labor O&A" in e and not check_covered and check_o:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.covered_labor = to_float(number)
                        else : invoice.covered_labor = 0
                except: pass
                logger.info("data %s ---- %s ---- %s", e, check_covered, check_o)
                try:
                    if "Material" in e and not check_covered and check_o:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            logger.info("data %s ---- %s ", check_covered, check_o)
                            number = number_credit.group(0)
                            invoice.covered_material = number
                        else : invoice.covered_material = 0
                except: pass

                try:
                    if "Repair" in e and not check_covered and check_o:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.covered_repair = to_float(number)
                        else : invoice.covered_repair = 0
                except: pass

                try:
                    if "Test Cell Fee" in e and not check_covered and check_o:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.covered_test_cell_fee = to_float(number)
                        else : invoice.covered_test_cell_fee = 0
                except: pass

                try:
                    if "Total" in e and not check_covered and check_o:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.covered_total = to_float(number)
                        else : invoice.covered_total = 0
                except: pass

                try:
                    if "O&A" in e and not "Labor O&A" in e:
                        check_covered = True
                        check_o = False
                except: pass

                try:
                    if "FPLS" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_fpls = to_float(number)
                        else : invoice.oq_fpls = 0
                except: pass

                try:
                    if "Labor O&A" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_labor = to_float(number)
                        else : invoice.oq_labor = 0
                except: pass

                try:
                    if "Material" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_material = to_float(number)
                        else : invoice.oq_material = 0
                except: pass

                try:
                    if "Repair" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_repair = to_float(number)
                        else : invoice.oq_repair = 0
                except: pass


                try:
                    if "Total SV" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_total = to_float(number)
                        else : invoice.oq_total = 0
                except: pass


                try:
                    if "Transportation ,TAT Penalty & Letter of Credit" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_transportation = to_float(number)
                        else : invoice.oq_transportation = 0
                except: pass


                try:
                    if "LC amount draw down " in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_lc_amount = to_float(number)
                        else : invoice.oq_lc_amount = 0
                except: pass


                try:
                    if "Final invoice" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_final_invoice = to_float(number)
                        else : invoice.oq_final_invoice = 0
                except: pass


                try:
                    if "Invoice#" in e and not check_o and check_covered:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_invoice_total = to_float(number)
                        else : invoice.oq_invoice_total = 0
                except: pass

                try:
                    if "Service Credit" in e and not check_o:
                        number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
                        if number_credit:
                            number = number_credit.group(0)
                            invoice.oq_service_credit = to_float(number)
                        else : invoice.oq_service_credit = 0
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



# Hàm xử lý số liệu
def extract_number(e, key):
    number_credit = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', e)
    return to_float(number_credit.group(0)) if number_credit else 0


