from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import get_db, SessionLocal
from datetime import datetime, timedelta
from typing import List


router = APIRouter()

@router.post("/contacts/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

@router.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    contacts = crud.get_contacts(db, skip=skip, limit=limit)
    return contacts

@router.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    updated_contact = crud.update_contact(db, contact_id, contact)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact

@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    deleted_contact = crud.delete_contact(db, contact_id)
    if deleted_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted_contact

@router.get("/contacts/search/", response_model=List[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db)):
    contacts = crud.search_contacts(db, query)
    return contacts


@router.get("/contacts/birthdays/", response_model=List[schemas.Contact])
def upcoming_birthdays(db: Session = Depends(get_db)):
    contacts = crud.get_upcoming_birthdays(db)
    return contacts

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Додайте інші маршрути для CRUD операцій та додаткових функціональних вимог.
