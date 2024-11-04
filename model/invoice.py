import json

class Invoice:
    def __init__(self, inv_no: str):
        """
        Khởi tạo một đối tượng Invoice với số hóa đơn.

        Parameters:
            inv_no (str): Số hóa đơn được gán cho thuộc tính inv_no của đối tượng.
        """
        self.inv_no = inv_no

    def to_string(self):
        """
        Chuyển đổi đối tượng thành chuỗi JSON.

        Returns:
            str: Một chuỗi JSON đại diện cho đối tượng, với các thuộc tính được mã hóa thành định dạng JSON.
        """
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)