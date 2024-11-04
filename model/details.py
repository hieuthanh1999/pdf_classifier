import json
class Details:
    def __int__(self, inv_no: str):
        self.inv_no = inv_no
 
    def to_string(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)
    
    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if value != "" and value is not None}