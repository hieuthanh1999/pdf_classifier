# common/utils.py
from types import SimpleNamespace
import json
import time
from common import *

from types import SimpleNamespace

def keyword(type):
    """
    Chuyển đổi một từ điển (dictionary) thành một đối tượng SimpleNamespace.

    Parameters:
        type (dict): Một từ điển chứa các cặp khóa-giá trị.

    Returns:
        SimpleNamespace: Đối tượng chứa các thuộc tính tương ứng với các khóa trong từ điển.
    """
    return SimpleNamespace(**type)

def to_string(value):
    """
    Chuyển đổi giá trị thành chuỗi, loại bỏ khoảng trắng ở đầu và cuối.
    
    Args:
        value: Giá trị cần chuyển đổi (có thể là bất kỳ kiểu dữ liệu nào).
    
    Returns:
        str: Chuỗi đã được chuyển đổi và loại bỏ khoảng trắng.
              Trả về chuỗi rỗng nếu có lỗi xảy ra.
    """
    try:
        return str(value).strip()
    except (ValueError, TypeError):
        return ''


def to_float_regex(value):
    """
    Chuyển đổi một chuỗi đầu vào thành kiểu số thực (float) sau khi loại bỏ các ký tự không hợp lệ.

    Parameters:
        value (str): Chuỗi đầu vào cần chuyển đổi.

    Returns:
        float: Giá trị số thực sau khi chuyển đổi. Nếu chuyển đổi thất bại, trả về 0.0.
    """
    value = re.sub(r'[^-\d.]', '', value)
    
    try:
        return float(value)
    except ValueError:
        return 0.0


def to_int(value):
    """
    Chuyển đổi giá trị thành số nguyên (int), loại bỏ dấu '-' ở cuối nếu có.
    
    Args:
        value: Chuỗi đại diện cho số (có thể chứa dấu phẩy và dấu '-').
    
    Returns:
        int: Giá trị số nguyên đã được chuyển đổi.
             Trả về 0 nếu có lỗi xảy ra.
    """
    try:
        if isinstance(value, str) and value.endswith('-'):
            value = value[:-1]
        return int(value.replace(',', ''))
    except (ValueError, TypeError):
        return 0
    
def to_percentage(value):
    """
    Chuyển đổi giá trị phần trăm thành số thực (float), loại bỏ ký hiệu '%' nếu có.

    Args:
        value: Chuỗi đại diện cho phần trăm (có thể chứa dấu phẩy và ký hiệu '%').

    Returns:
        float: Giá trị số thực đã được chuyển đổi.
               Trả về 0.0 nếu có lỗi xảy ra.
    """
    try:
        value = value.replace('%', '').strip()
        return float(value.replace(',', '')) / 100
    except (ValueError, TypeError):
        return 0.0
 
def to_float(value):
    """
    Chuyển đổi giá trị thành số thực (float), loại bỏ dấu '-' ở cuối nếu có.
    
    Args:
        value: Chuỗi đại diện cho số (có thể chứa dấu phẩy và dấu '-').
    
    Returns:
        float: Giá trị số thực đã được chuyển đổi.
               Trả về 0.0 nếu có lỗi xảy ra.
    """
    try:
        if value.endswith('-'):
            value = value[:-1] 
        return float(value.replace(',', ''))
    except (ValueError, TypeError):
        return 0.0 
    

def write_json_to_file(data, file_path = 'output/output.json'):
    """
    Ghi dữ liệu vào file JSON.

    :param data: Dữ liệu cần ghi (có thể là dict, list, ...)
    :param file_path: Đường dẫn đến file JSON
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Đã xảy ra lỗi khi ghi file: {e}")

def time_execution(func):
    """
    Decorator để tính thời gian thực thi của một hàm.

    :param func: Hàm cần tính thời gian thực thi
    :return: Kết quả của hàm và thời gian thực thi
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Thời gian thực thi của hàm '{func.__name__}': {execution_time:.4f} s")
        return result
    return wrapper
def remove_duplicate_characters(description):
    return re.sub(r'(.)\1', r'\1', description)