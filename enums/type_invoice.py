from enum import Enum

class TypeInvoice(Enum):
    """
    Lớp Enum đại diện cho các loại hóa đơn khác nhau.
    """
    INVOICE = 'invoice'
    REPAIR = 'repair'
    LC = 'lc'
    CREDIT = 'credit'

    