from fastapi import FastAPI
from schemas import Note
import service

app = FastAPI()

@app.get("/notes")
def get_notes():
    return service.get_all_notes()

@app.get("/notes/{note_id}")
def get_note(note_id: int):
    note = service.get_note_by_id(note_id)
    if note is None:
        return {"error": "Note not found"}
    return note

@app.post("/notes")
def create_note(note: Note):
    return service.create_note(note.dict())

@app.put("/notes/{note_id}")
def update_note(note_id: int, new_note: Note):
    result = service.update_note(note_id, new_note.dict())
    if result is None:
        return {"error": "Note not found"}
    return result

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    result = service.delete_note(note_id)
    if result is None:
        return {"error": "Note not found"}
    return result