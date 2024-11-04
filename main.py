
import configparser
import json
import re
import os
import sys
from enum import Enum
import pdfplumber
from model import *
from type import  *
import logging
import time
from common import *
from pdf_readers import *

class TypeInvoice(Enum):
    INVOICE = 'invoice'
    REPAIR = 'repair'
    LC = 'lc'
    CREDIT = 'credit'

class Code(Enum):
    IAE = 'iae'
    GE = 'ge'
    PRATT_WHITNEY_CANADA = 'pratt_whitney_canada'
    AMECO = 'ameco'
    ROLLS_ROYCE = 'rolls_royce'
    HONEY_WELL = 'honey_well'
    CELESTIAL = 'celestial'
    
#----------------------------------------------------------------
# MAIN
#----------------------------------------------------------------
def extract_data(type_invoice, code, file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            if type_invoice == TypeInvoice.CREDIT.value and code == Code.GE.value:
                classifier_invoice_credit(pdf.pages)
            if type_invoice == TypeInvoice.REPAIR.value and code == Code.PRATT_WHITNEY_CANADA.value:
                classifier_repair_invoice(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.HONEY_WELL.value:
                classifier_honey_well_invoice(pdf.pages)   
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.ROLLS_ROYCE.value:
                classifier_invoice_rolls_royce(pdf.pages)
            if type_invoice == TypeInvoice.REPAIR.value and code == Code.ROLLS_ROYCE.value:
                classifier_invoice_credit_rolls_royce(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE and code == Code.AMECO.value:
                classifier_invoice_ameco(pdf.pages)
            if type_invoice == TypeInvoice.LC.value and code == Code.AMECO.value:
                classifier_invoice_lc_ameco(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.CELESTIAL.value:
                classifier_invoice_celestial(pdf.pages)
            if type_invoice == 'invoice_epcor':
                classifier_invoice_invoice_epcor(pdf.pages)
            if type_invoice == TypeInvoice.INVOICE.value and code == Code.IAE.value:
                classifier_invoice_iae(pdf.pages)
            if type_invoice == 'stand_aero':
                classifier_invoice_stand_aero(pdf.pages)

                
                
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