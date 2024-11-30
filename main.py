# -*- coding: utf-8 -*-
import configparser
import json
import re
import os
import sys
import pdfplumber
from model import *
from type import  *
from enums import  *
import logging
import time
from common import *
from pdf_readers import *
from dotenv import load_dotenv
import pytesseract


load_dotenv()

poppler_path = os.getenv("POPPLER_PATH")
poppler_path = r'/usr/local/bin'
#pytesseract.pytesseract.tesseract_cmd = r"/usr/local/bin/tesseract"
tesseract_path = os.getenv("TESSERACT_PATH")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

#----------------------------------------------------------------
# MAIN
#----------------------------------------------------------------
def extract_data(type_invoice, code, file_path):
    """
    Hàm này trích xuất dữ liệu từ file PDF dựa trên loại hóa đơn và mã hóa.
    
    Parameters:
        type_invoice (str): Loại hóa đơn cần xử lý.
        code (str): Mã hóa đại diện cho nhà cung cấp.
        file_path (str): Đường dẫn tới file PDF cần xử lý.
    """
    try:
        logger.info("Info: type_invoice : %s ====== code: %s ====== path: %s ", type_invoice, code, file_path)
        if type_invoice == TypeInvoice.LC.value and code == Code.GE.value:
            classifier_invoice_lc_ge(file_path)
        with pdfplumber.open(file_path) as pdf:
            
            if type_invoice == TypeInvoice.CREDIT.value and code == Code.GE.value:
                classifier_invoice_credit(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.WILLS.value:
                classifier_invoice_wills(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.WLFC.value:
                classifier_invoice_wlfc(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.PW.value:
                classifier_invoice_pw(pdf.pages)
            if type_invoice == TypeInvoice.LC.value and code == Code.MTU.value:
                classifier_lc_mtu_invoice(file_path, poppler_path, pytesseract)
            if type_invoice == TypeInvoice.REPAIR.value and code == Code.PRATT_WHITNEY_CANADA.value:
                classifier_repair_invoice(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.HONEY_WELL.value:
                classifier_honey_well_invoice(pdf.pages)   
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.ROLLS_ROYCE.value:
                classifier_invoice_rolls_royce(pdf.pages)
            if type_invoice == TypeInvoice.REPAIR.value and code == Code.ROLLS_ROYCE.value:
                classifier_invoice_credit_rolls_royce(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.AMECO.value:
                classifier_invoice_ameco(pdf.pages)
            if type_invoice == TypeInvoice.LC.value and code == Code.AMECO.value:
                classifier_invoice_lc_ameco(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.CELESTIAL.value:
                classifier_invoice_celestial(pdf.pages)
            if type_invoice == 'invoice_epcor':
                classifier_invoice_epcor(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.IAE.value:
                classifier_invoice_iae(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.STAND_AERO.value:
                classifier_invoice_stand_aero(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.AMECO_3.value:
                classifier_invoice_ameco_3(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.EPCOR.value:
                classifier_invoice_epcor(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.SMBC.value:
                classifier_invoice_smbc(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.KLM.value:
                classifier_invoice_klm(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.EPCOR_2.value:
                classifier_invoice_epcor_2(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.LUFTHANSA.value:
                classifier_invoice_lufthansa(pdf.pages)
            if type_invoice == TypeInvoice.CREDIT.value and code == Code.STAND_AERO.value:
                    classifier_credit_stand_aero(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.IAE_2.value:
                classifier_invoice_iae_2(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.STENGINEERING.value:
                classifier_invoice_stengineering(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.AERCAP.value:
                classifier_invoice_aercap(pdf.pages)
            if type_invoice == TypeInvoice.DEPOSIT.value and code == Code.ROLLS_ROYCE.value:
                classifier_invoice_deposit_rolls_royce(pdf.pages)
            if type_invoice == TypeInvoice.LC.value and code == Code.AMECO.value:
                classifier_lc_ameco(file_path, poppler_path, pytesseract)
            if type_invoice == TypeInvoice.LC.value and code == Code.GE.value:
                classifier_invoice_lc_ge(file_path, poppler_path, pytesseract)
        pdf.close()
    except IOError as e:
        print({"error": "Không thể mở tập tin " + str(e)})
    except TypeError:
        print({"error": "Type Error"})
    except IndexError:
        print({"error": "Index Error"})


if __name__ == '__main__':
    args = sys.argv[1:]
    extract_data(args[0], args[1], args[2])