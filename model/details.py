import json
import json

class Details:
    def __init__(self, inv_no: str):
        """
        Khởi tạo một đối tượng Details với số hóa đơn.

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
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng thành từ điển (dictionary) loại bỏ các thuộc tính rỗng hoặc None.

        Returns:
            dict: Một từ điển chứa các thuộc tính của đối tượng, ngoại trừ những thuộc tính có giá trị rỗng hoặc None.
        """
        return {key: value for key, value in self.__dict__.items() if value != "" and value is not None}
