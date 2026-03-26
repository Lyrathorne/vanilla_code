from pydantic import BaseModel, Field
class Note(BaseModel):
    id : int = Field(gt = 1, lt = 100000000)
    title : str = Field(min_length = 3, max_length = 50)
    text : str = Field(min_length = 5)
