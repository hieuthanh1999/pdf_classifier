
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
        list_table = []
        pattern = re.compile(
            r'(?P<description>.+?)\s{2,}(?P<condition>.+?)\s{2,}(?P<qty_uom>\d+\.\d{3}\w{2})\s{2,}(?P<unit_price>\$\d{1,3}(?:,\d{3})*\.\d{2})\s{2,}(?P<net_price>\$\d{1,3}(?:,\d{3})*\.\d{2})'
        )

        total_pattern = re.compile(r'Total amount due\s+(?P<total_amount>\$\d{1,3}(?:,\d{3})*\.\d{2})')
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                #logger.info("Line: %s", line)
                if "Invoice Number:" in line:
                    page_data["invoice_number"] = line.split(":", 1)[1].strip()
                elif "Invoice Date:" in line:
                    page_data["invoice_date"] = line.split(":", 1)[1].strip()
                elif "Document No.:" in line:
                    page_data["document_no"] = line.split(":", 1)[1].strip()
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
        print(json.dumps(page_data, indent=4))

        #print(invoice.to_string())
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None

@time_execution
def classifier_invoice_iae_2(pages):
    try:
        page_data = {}
        list_table = []
        list_table_oac = []
        list_last_table = []
        total_oac = []

        last_table = False
        oac = False
        count = 0
        extracting = False
        extract_total_oac = False
        extract_sumary = True
        pattern_oac_total = re.compile(r'(\w+)\s+\$([\d,]+\.\d{2})')
        pattern_oac_sumary = r'^(\d+)\s+(\d+)\s+\$([\d,]+\.\d{2})\s+\$([\d,]+\.\d{2})\s+\(?\$([\d,]+\.\d{2})\)?\s+([\d.]+%)\s+\$([\d,]+\.\d{2})\s+([\d.]+%)\s+\$([\d,]+\.\d{2})\s+\$([\d,]+\.\d{2})$'
        pattern = re.compile(
            r'(?P<description>\S+)\s+(?P<condition>\S+)\s+(?P<qty_uom>\d+\.\d{3}\w{2})\s+\$(?P<unit_price>[\d,]+\.\d{2})\s+\$(?P<net_price>[\d,]+\.\d{2})'
        )
        total_pattern = re.compile(r'Total amount due\s+(?P<total_amount>\$\d{1,3}(?:,\d{3})*\.\d{2})')
        pattern_oac = re.compile(
            r'(?P<part_number>\w+)\s+(?P<category>\w+)\s+(?P<sub_category>\w+)\s+(?P<type>\w+)\s+(?P<item_number>[\w-]+)\s+(?P<part_code>[\w-]+)\s+(?P<description>[\w\s,()-\.]+)\s+(?P<quantity>\d+)\s+(?P<discount>\d+\.\d+)\s+\$(?P<unit_price>[\d,]+\.\d{2})\s+\$(?P<net_price>[\d,]+\.\d{2})\s+\(?\$?(?P<discount_amount>[\d,]+\.\d{2})\)?\s+(?P<tax_rate>\d+\.\d+%)\s+\$(?P<tax_amount>[\d,]+\.\d{2})\s+(?P<additional_tax_rate>\d+\.\d+%)\s+\$(?P<additional_tax_amount>[\d,]+\.\d{2})\s+\$(?P<total_price>[\d,]+\.\d{2})\s+(?P<location>\w+)\s+(?P<condition>\w+)\s+(?P<contract_status>[\w\s]+);'
        )
        pattern_last_table = re.compile(
            r'(\d{6}-\d{2}-\d{3})\s+([A-Z0-9\s\-\(\)]+)\s+([A-Z0-9]+)\s+([A-Za-z0-9\s-]+)\s+(Yes|No|yes)\s+(\d+)\s+([\d\s,]+)\s+(\d{4})\s+\$(\d{1,3}(?:,\d{3})*\.\d{2})\s+\$(\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\$\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\$\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\$\d{1,3}(?:,\d{3})*\.\d{2})\s+(-?\$\d{1,3}(?:,\d{3})*\.\d{2})\s+\$(\d{1,3}(?:,\d{3})*\.\d{2})'
        )
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):

            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                logger.info("Line: %s", line)
                if extract_sumary:
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
                    if 'Total amount due' in line or 'Totalamountdue' in line:
                        extract_sumary = False
                        total_match = total_pattern.search(line)
                        if total_match:
                            total_amount_due = total_match.group('total_amount')
                            page_data['total_amount_due'] = total_amount_due
                        else:
                            total_amount_due = to_float(line.split('$')[1])
                if 'Over & Above Charges' in line:
                    oac = True
                if re.compile(r"Type O&A Total").search(line):
                    extract_total_oac = True
                if 'Invoice Total' in line:
                        extract_total_oac = False
                        page_data['invoice_total'] = to_float(line.split('$')[1])
                        page_data['total_oac'] = total_oac
                if extract_total_oac:
                    match_oac_total = pattern_oac_total.search(line)
                    if match_oac_total:
                        model =  Details()
                        model.type = match_oac_total.group(1)
                        model.total = to_float(match_oac_total.group(2))
                        total_oac.append(model.to_dict())

                if oac:
                    match_oac = pattern_oac.search(line)
                    if match_oac:

                        model =  Details()
                        model.type = match_oac.group(1)
                        model.charge_type = match_oac.group(2)
                        model.category_type = match_oac.group(3)
                        model.build_group = match_oac.group(4)
                        model.ata_number = match_oac.group(5)
                        model.part_number = match_oac.group(6)
                        model.part_name = match_oac.group(7)
                        model.quantity = to_int(match_oac.group(8))
                        model.hour = to_float(match_oac.group(9))
                        model.unit_price = to_float(match_oac.group(10))
                        model.sub_total = to_float(match_oac.group(11))
                        model.adjustment = to_float(match_oac.group(12).replace('%', ''))
                        model.handling_fee = to_float(match_oac.group(13).replace('%', ''))
                        model.iae_handling_fee = to_float(match_oac.group(14))
                        model.discount_percent = to_float(match_oac.group(15).replace('%', ''))
                        model.discount_amount = to_float(match_oac.group(16))
                        model.oaa_total = to_float(match_oac.group(17))
                        model.source = match_oac.group(18)
                        model.material_type = match_oac.group(19)
                        model.exess_work_reason = match_oac.group(20)
                        list_table_oac.append(model.to_dict())
                    else:
                        match_oac = re.compile(pattern_oac_sumary).search(line)
                        if match_oac:
                            model = Details()
                            model.quantity = to_int(match_oac.group(1))
                            model.hours = to_int(match_oac.group(2))
                            model.unit_price = to_float(match_oac.group(3))
                            model.sub_total = to_float(match_oac.group(4))
                            model.adjustment = to_float(match_oac.group(5))
                            model.handling_fee = to_float(match_oac.group(6))
                            model.iae_handling_fee = to_float(match_oac.group(7))
                            model.discount_percent = to_float(match_oac.group(8))
                            model.discount_amount = to_float(match_oac.group(9))
                            model.oaa_total = to_float(match_oac.group(10))
                            page_data['oac_summary'] = model.to_dict()
                    if 'Invoice Total' in line:
                        oac = False
                if 'Part Information' in line and 'Removal Information' in line:
                    last_table = True
                if last_table:

                    match_last_table = pattern_last_table.search(line)
                    if match_last_table:
                        model =  Details()
                        model.lid = match_last_table.group(1)
                        model.description = match_last_table.group(2)
                        model.part_number = match_last_table.group(3)
                        model.removal_reason = match_last_table.group(4)
                        model.met_build_objective = match_last_table.group(5)
                        model.target_life = match_last_table.group(6)
                        group_life = match_last_table.group(7)
                        group_life = remove_whitespace_before_comma(group_life)
                        group_life = remove_whitespace_before_number(group_life)
                        group_life = remove_extra_spaces(group_life)
                        list_group_life = group_life.split(' ')
                        model.tsn = to_int(list_group_life[0])
                        model.csn = to_int(list_group_life[1])
                        model.life_remaining_off_part = to_int(list_group_life[2])
                        model.life_limit_off_part = to_int(list_group_life[3])
                        model.life_remaining_on_part = to_int(list_group_life[4])
                        model.life_limit_on_part = to_int(list_group_life[5])
                        model.year_of_replacement = match_last_table.group(8)
                        model.clp = to_float(match_last_table.group(9))
                        model.cust_price = to_float(match_last_table.group(10))
                        model.life_assurance_credit = to_float(match_last_table.group(11).replace('$', ''))
                        model.fmp_sfc_credit = to_float(match_last_table.group(12).replace('$', ''))
                        model.service_policy_credit = to_float(match_last_table.group(13).replace('$', ''))
                        model.total_adjustment = to_float(match_last_table.group(14).replace('$', ''))
                        model.net_payment = to_float(match_last_table.group(15))
                        list_last_table.append(model.to_dict())
                    pass
        page_data['pw1133g'] = list_last_table
        page_data['over_above_charges'] = list_table_oac
        page_data['table'] = list_table
        # write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))

        #print(invoice.to_string())
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None

def remove_whitespace_before_comma(text):
    return re.sub(r'\s+,', ',', text)

def remove_whitespace_before_number(text):
    return re.sub(r'\s{1,2}(\d)', r'\1', text)

def remove_extra_spaces(text):
    return re.sub(r'\s{2,}', ' ', text)






@time_execution
def classifier_credit_iae(pages):
    try:
        page_data = {}
        list_table = []
        total_oac = []
        extract_total_oac = False
        extract_sumary = True
        pattern_oac_total = re.compile(r'(\w+)\s+\$([\d,]+\.\d{2})')
        pattern = re.compile(
            r'(?P<description>\S+)\s+(?P<condition>\S+)\s+(?P<qty_uom>\d+\.\d{3}\w{2})\s+\$(?P<unit_price>[\d,]+\.\d{2})\s+\$(?P<net_price>[\d,]+\.\d{2})'
        )
        total_pattern = re.compile(r'Total amount due\s+(?P<total_amount>\$\d{1,3}(?:,\d{3})*\.\d{2})')
        key = keyword(rolls_royce)
        for p_idx, page in enumerate(pages):

            text = page.extract_text().split('\n')
            for i, line in enumerate(text):
                logger.info("Line: %s", line)

                if "InvoiceNumber:" in line or "Invoice Number:" in line:
                    page_data["invoice_number"] = line.split(":", 1)[1].strip()
                elif "InvoiceDate:" in line  or "Invoice Date:" in line:
                    page_data["invoice_date"] = line.split(":", 1)[1].strip()
                elif "DocumentNo.:" in line or "Document No:" in line:
                    page_data["document_no"] = line.split(":", 1)[1].strip()
                if extract_sumary:
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
                    if 'Total amount due' in line or 'Totalamountdue' in line:
                        extract_sumary = False
                        total_match = total_pattern.search(line)
                        if total_match:
                            total_amount_due = total_match.group('total_amount')
                            page_data['total_amount_due'] = total_amount_due
                        else:
                            total_amount_due = to_float(line.split('$')[1])
                if 'Over & Above Charges' in line:
                    oac = True
                if re.compile(r"Type O&A Total").search(line):
                    extract_total_oac = True
                if 'Invoice Total' in line:
                        extract_total_oac = False
                        page_data['invoice_total'] = to_float(line.split('$')[1])
                        page_data['total_oac'] = total_oac
                if extract_total_oac:
                    match_oac_total = pattern_oac_total.search(line)
                    if match_oac_total:
                        model =  Details()
                        model.type = match_oac_total.group(1)
                        model.total = to_float(match_oac_total.group(2))
                        total_oac.append(model.to_dict())

        page_data['table'] = list_table
        # write_json_to_file(page_data)
        print(json.dumps(page_data, indent=4))

        #print(invoice.to_string())
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
