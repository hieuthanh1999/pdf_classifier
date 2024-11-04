import json
class Invoice:
    def __int__(self, inv_no: str):
        self.inv_no = inv_no
 
    def to_string(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)
