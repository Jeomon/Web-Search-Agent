from pydantic import BaseModel
from inspect import getdoc
from json import dumps

class Tool:
    def __init__(self, name: str='', params: BaseModel|None=None):
        self.name = name
        self.params = params
        self.func = None
        self.description = None
        self.schema = None

    def __call__(self, func):
        if self.params:
            # Store the decorated function and its metadata
            self.description = getdoc(func)
            skip_keys=['title']
            self.schema = {k:{term:content for term,content in v.items() if term not in skip_keys} for k,v in self.params.model_json_schema().get('properties').items()}
        self.func = func
        return self  # Return the Tool Instance

    def invoke(self, **kwargs):
        # Validate inputs using the schema and invoke the wrapped function
        try:
            if self.params:
                args = self.params(**kwargs)  # Validate arguments
                return self.func(**args.dict())  # Call the function with validated arg
            else:
                return self.func(**kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def async_invoke(self, **kwargs):
        # Validate inputs using the schema and invoke the wrapped function
        try:
            if self.params:
                args = self.params(**kwargs)  # Validate arguments
                return await self.func(**args.dict())  # Call the function with validated arg
            else:
                return await self.func(**kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
        
    def __repr__(self):
        return f"Tool(name={self.name}, description={self.description}, params={list(self.params.model_fields.keys())})"
    
    def prompt(self):
        return f'''Tool Name: {self.name}\nTool Description: {self.description}\nTool Input: {dumps(self.schema,indent=2)}'''