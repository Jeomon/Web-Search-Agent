from pydantic import BaseModel
from inspect import getdoc

class Tool:
    def __init__(self, name: str, args_schema: BaseModel|None=None):
        self.name = name
        self.args_schema = args_schema
        self.func = None
        self.description = None
        self.schema = None

    def __call__(self, func):
        if self.args_schema:
            # Store the decorated function and its metadata
            self.description = getdoc(func)
            self.schema = self.args_schema.model_json_schema()
            # Remove unnecessary fields
            self.schema.pop('title')
        self.func = func
        return self  # Return the Tool instance

    def invoke(self, **kwargs):
        # Validate inputs using the schema and invoke the wrapped function
        try:
            if self.args_schema:
                args = self.args_schema(**kwargs)  # Validate arguments
                return self.func(**args.dict())  # Call the function with validated arg
            else:
                return self.func(**kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def async_invoke(self, **kwargs):
        # Validate inputs using the schema and invoke the wrapped function
        try:
            if self.args_schema:
                args = self.args_schema(**kwargs)  # Validate arguments
                return await self.func(**args.dict())  # Call the function with validated arg
            else:
                return await self.func(**kwargs)
        except Exception as e:
            return f"Error: {str(e)}"