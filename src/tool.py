from pydantic import BaseModel
from inspect import getdoc

def tool(name:str,args_schema:BaseModel):
    def wrapper(func):
        func.name = name
        func.schema = args_schema.model_json_schema()
        func.schema.pop('title')
        func.description = getdoc(func)
        return func
    return wrapper