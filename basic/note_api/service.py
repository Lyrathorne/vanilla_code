from db_fake import notes

def get_all_notes():
    return notes

def get_note_by_id(note_id: int):
    if note_id < 0 or note_id >= len(notes):
        return None
    return notes[note_id]

def create_note(note: dict):
    notes.append(note)
    return {"message": "Note added", "notes": notes}

def update_note(note_id: int, new_note: dict):
    if note_id < 0 or note_id >= len(notes):
        return None
    notes[note_id] = new_note
    return {"message": "Note updated", "notes": notes}

def delete_note(note_id: int):
    if note_id < 0 or note_id >= len(notes):
        return None
    notes.pop(note_id)
    return {"message": "Note deleted", "notes": notes}