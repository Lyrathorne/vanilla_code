from fastapi import FastAPI
from pydantic import BaseModel, Field
app = FastAPI()
notes = []
class Note(BaseModel):
    id : int = Field(gt = 1, lt = 100000000)
    title : str = Field(min_length = 3, max_length = 50)
    text : str = Field(min_length = 5)

@app.get("/notes")
def get_notes():
    return notes
@app.get("/notes/{note_id}")
def get_note(note_id: int):
    if note_id < 0 or note_id >= len(notes):
        return {"error": "Note not found"}
    return notes[note_id]
@app.post("/notes") 
def create_note(note: Note):
    notes.append(note.model.dump())
    return {"message": "Note added", "notes": notes}
@app.put("/notes/{note_id}")
def update_note(note_id: int, new_note: Note):
    if note_id < 0 or note_id >= len(notes):
        return {"error": "Note not found"}
    notes[note_id] = new_note.model.dump()
    return {"message": "Note updated", "notes": notes}
@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    if note_id < 0 or note_id >= len(notes):
        return {"error": "Note not found"}
    notes.pop(note_id)
    return {"message": "Note deleted", "notes": notes}
