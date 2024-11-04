
import configparser
import json
import re
import os
import sys
import pdfplumber
from model import *
from type import  *
import logging
import time
from common import *
from pdf_readers import *

@time_execution
def classifier_repair_invoice(pages):
    page_data = {}
    try:
        data_page_labour_summary = []
        data_page_new_material = []
        data_page_campaign_material = []
        data_page_component_repair_flat_rate_summary = []
        data_page_other_summary = []

        details_page = {}
        key = keyword(repair)
        for p_idx, page in enumerate(pages):
            text = page.extract_text().split('\n')
            page_name = ''
            table_data = [] 
            details = {}
            for i, e in enumerate(text):
                """
                Summary of charges
                """
                summary_of_charges = False
                try:
                    if key.summary_of_charges in e:
                        summary_of_charges = True 
                        page_name = 'summary_of_charges'
                        #logger.info("Repair: %s", e)
                    pass
                except: pass

                if summary_of_charges:
                    #logger.info("Full content of page %d:", p_idx)
                    for i, line in enumerate(text):
                       
                        if key.summary_of_charges_total in line:
                            match = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                            if match:
                                details[key.summary_of_charges_total] = to_float(match.group(0))
                            else : details[key.summary_of_charges_total] = 0
                        if key.summary_of_charges_total in line:
                            match = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                            if match:
                                details[key.summary_of_charges_total] = to_float(match.group(0))
                            else : details[key.summary_of_charges_total] = 0
                        if key.summary_of_charges_materials in line:
                            match = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                            if match:
                                details[key.summary_of_charges_materials] = to_float(match.group(0))
                            else : details[key.summary_of_charges_materials] = 0
                        if key.summary_of_charges_campaign in line:
                            match = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                            if match:
                                details[key.summary_of_charges_campaign] = to_float(match.group(0))
                            else : details[key.summary_of_charges_campaign] = 0
                        if key.summary_of_charges_component in line:
                            match = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                            if match:
                                details[key.summary_of_charges_component] = to_float(match.group(0))
                            else : details[key.summary_of_charges_component] = 0
                        if key.summary_of_charges_total_other in line:
                            match = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                            if match:
                                details[key.summary_of_charges_total_other] = to_float(match.group(0))
                            else : details[key.summary_of_charges_total_other] = 0
                            # for i, e in enumerate(text):
                            if i + 1 < len(text):
                                next_line = text[i + 1].strip()
                            if next_line:
                                details[key.summary_of_charges_total_all] = to_float(next_line)
                            else : details[key.summary_of_charges_total_all] = 0
                        
                   
                            #details['summary_of_charges_total'] = 

                """
                Summary of charges
                """
                warranty_summary = False
                try:
                    if key.warranty_summary in e:
                        warranty_summary = True 
                        page_name = 'warranty_summary'
                    pass
                except: pass
                if warranty_summary:
                    for line in text:
                        if key.warranty_summary_total_credit in line:
                            #logger.info("data %s:", line)
                            match = re.search(r'[-+]?\d{1,3}(?:,\d{3})*(?:\.\d+)?', line)
                            if match:
                                details[key.warranty_summary_total_credit] = to_float(match.group(0))
                            else : details[key.warranty_summary_total_credit] = 0
                            break
                """
                labour summary
                """
                labour_summary = False
                try:
                    if key.labour_summary in e:
                        labour_summary = True 
                        page_name = 'labour_summary'
                    pass
                except: pass
                labour_summary_material = False
                if labour_summary:
                    for line in text:
                        #logger.info("%s", line)
                        if "Next Page" in line:
                            break
                        if key.labour_summary_material in line:
                            labour_summary_material = True
                            continue
                        if labour_summary_material:

                            model =  Details()
                            match = re.match(r'^\s*(\S+)\s+(.+?)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+(\w+)\s*$', line.strip())
                            if match:
                                # Lấy các thông tin từ nhóm trong regex
                                material = match.group(1)
                                description = match.group(2)
                                unit_price = to_float(match.group(3))
                                qty = to_float(match.group(4))
                                extended_list = to_float(match.group(5))
                                sub_total = to_float(match.group(6))
                                total = to_float(match.group(7))
                                currency = match.group(8)

                                model.material = material
                                model.description = description
                                model.unit_price = unit_price
                                model.qty = qty
                                model.extended_list = extended_list
                                model.sub_total = sub_total
                                model.total = total
                                model.currency = currency
                                data_page_labour_summary.append(model.to_dict())
                                #logger.info("%s", details.to_string())
                    details['table'] = data_page_labour_summary
                
                """
                new material summary
                """
                new_material_summary = False
                try:
                    if key.new_material_summary in e:
                        new_material_summary = True 
                        page_name = 'new_material_summary'
                    pass
                except: pass
                new_summary_material = False
                if new_material_summary:
                    for line in text:
                        #logger.info("%s", line)
                        if "Next Page" in line:
                            break
                        if key.labour_summary_material in line:
                            new_summary_material = True
                            continue
                        if new_summary_material:
                            model =  Details()
                            pattern = r'^\s*(\S+)\s{2,}(.+?)\s{2,}(.+?)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.%-]+)\s+([\d,.]+)\s+([\d,.]+)\s+(\w+)\s*$'
                            match = re.match(pattern, line)
                            if match:
                                material = match.group(1)
                                description = match.group(2) 
                                reason_for_memoval = match.group(3)
                                unit_price = to_float(match.group(4))
                                qty = to_float(match.group(5))
                                extended_list = to_float(match.group(6))
                                discount = to_float(match.group(7))
                                sub_total = to_float(match.group(8))
                                total = to_float(match.group(9))
                                currency = match.group(10)
                                #logger.info("%s", description)
                                model.material = material
                                model.description = description
                                model.reason_for_memoval = reason_for_memoval
                                model.unit_price = unit_price
                                model.qty = qty
                                model.extended_list = extended_list
                                model.discount = discount
                                model.sub_total = sub_total
                                model.total = total
                                model.currency = currency
                                data_page_new_material.append(model.to_dict())
                      
                    details['table'] = data_page_new_material

                """
                campaign material summary
                """
                campaign_material_summary = False
                try:
                    if key.campaign_material_summary in e:
                        campaign_material_summary = True 
                        page_name = 'campaign_material_summary'
                    pass
                except: pass
                campaign_summary_material = False
                if campaign_material_summary:
                    for line in text:
                        
                        if "Next Page" in line:
                            break
                        if key.labour_summary_material in line:
                            campaign_summary_material = True
                            continue
                        if campaign_summary_material:
                            model =  Details()
                            pattern = r'(\d+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+-?)\s+([\d,.]+)\s+([\d,.]+)\s+(\w+)'
                            match = re.match(pattern, line.strip())
                            if match:
                                
                                material = match.group(1)
                                
                                unit_price = to_float(match.group(2))
                                qty = to_float(match.group(3))
                                extended_list = to_float(match.group(4))
                                discount = to_float(match.group(5))
                                sub_total = to_float(match.group(6))
                                total = to_float(match.group(7))
                                currency = match.group(8)
                                
                                model.material = material
                                model.unit_price = unit_price
                                model.qty = qty
                                model.extended_list = extended_list
                                model.discount = discount
                                model.sub_total = sub_total
                                model.total = total
                                model.currency = currency
                                data_page_campaign_material.append(model.to_dict())
                                #logger.info("%s", model.to_dict())
                    details['table'] = data_page_campaign_material

                """
                component_repair_flat_rate_summary
                """
                component_repair_flat_rate_summary = False
                try:
                    if key.component_repair_flat_rate_summary in e:
                        component_repair_flat_rate_summary = True 
                        page_name = 'component_repair_flat_rate_summary'
                    pass
                except: pass
                campaign_summary_material = False
                if component_repair_flat_rate_summary:
                    for line in text:
                        
                        if "Next Page" in line:
                            break
                        if key.labour_summary_material in line:
                            campaign_summary_material = True
                            continue
                        if campaign_summary_material:
                            model =  Details()
                            #logger.info("%s", line)
                            pattern = r'(\S+)\s+(.+?)\s+(\d{2})\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+(\w+)'
                            match = re.match(pattern, line.strip())

                            if match:
                              
                                material = match.group(1)
                               
                                # logger.info("%s", repair_level)
                                description = match.group(2)
                                repair_level = match.group(3)
                                unit_price = to_float(match.group(4))
                                qty = to_float(match.group(5))
                                extended_list = to_float(match.group(6))
                                sub_total = to_float(match.group(7))
                                total = to_float(match.group(8))
                                currency = match.group(9)
                                #logger.info("%s", description)
                                model.material = material
                                model.description = description
                                model.repair_level = repair_level
                                model.unit_price = unit_price
                                model.qty = qty
                                model.extended_list = extended_list
                    
                                model.sub_total = sub_total
                                model.total = total
                                model.currency = currency
                                data_page_component_repair_flat_rate_summary.append(model.to_dict())
                                #logger.info("%s", model.to_dict())
                    details['table'] = data_page_component_repair_flat_rate_summary

                """
                other_summary
                """
                other_summary = False
                try:
                    if key.other_summary in e:
                        other_summary = True 
                        page_name = 'other_summary'
                    pass
                except: pass
                campaign_summary_material = False
                if other_summary:
                    for line in text:
                        if "Next Page" in line:
                            break
                        if key.labour_summary_material in line:
                            campaign_summary_material = True
                            continue
                        if campaign_summary_material:
                            model =  Details()
                            #logger.info("%s", line)
                            pattern = r'(.+?)\s{2,}(.+?)\s+([\d,.]+-?)\s+([\d,.]+)\s+([\d,.]+-?)\s+([\d,.]+-?)\s+([\d,.]+-?)\s+(\w+)'
                            match = re.match(pattern, line.strip())

                            if match:
                                material = match.group(1)
                                description = match.group(2)
                                unit_price = to_float(match.group(3))
                                qty = to_float(match.group(4))
                                extended_list = to_float(match.group(5))
                                sub_total = to_float(match.group(6))
                                total = to_float(match.group(7))
                                currency = match.group(8)
                                #logger.info("%s", material)
                                model.material = material
                                model.description = description
                                model.unit_price = unit_price
                                model.qty = qty
                                model.extended_list = extended_list
                                model.sub_total = sub_total
                                model.total = total
                                model.currency = currency
                                data_page_other_summary.append(model.to_dict())
                                #logger.info("%s", model.to_dict())
                    details['table'] = data_page_other_summary
            if page_name:
                page_data[page_name] = details 
        #write_json_to_file(page_data)
        # with open('output.json', 'w', encoding='utf-8') as file:
        #     json.dump(page_data, file, ensure_ascii=False, indent=4)
        print(json.dumps(page_data, indent=4))
        #print(page_data)           
    except Exception as e:
        logger.error("Error invoice credit: %s", str(e))
        return None
