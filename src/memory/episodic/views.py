from pydantic import BaseModel,Field
from uuid import uuid4

class Memory(BaseModel):
    id: str = Field(description='The id of the memory to be filled by the user',examples=['32cd40b6-5db1-48b3-9434-ebd9502f06f0'],default_factory=lambda: str(uuid4()))
    tags: list[str] = Field(...,description='Tags to help identify similar future conversations.',examples=[['google','weather']])
    summary: str = Field(...,description='Describes what the conversation accomplished.')
    what_worked: str = Field(...,description='Highlights the most effective strategy used.')
    what_to_avoid: str = Field(...,description='Describes the important pitfalls to avoid.')

    def to_dict(self):
        return self.model_dump()

    class Config:
        extra = 'allow'

class Memories(BaseModel):
    memories: list[Memory]=Field(description='The list of memories',default_factory=list)

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs)["memories"]

    def all(self):
        return [memory.to_dict() for memory in self.memories]

    def to_string(self):
        return '\n\n'.join([f'**Tags:** {memory.tags}\n***Summary:** {memory.summary}\n**What Worked:** {memory.what_worked}\n**What to Avoid:** {memory.what_to_avoid}' for memory in self.memories])

