from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import get_db, SessionLocal
from datetime import datetime, timedelta
from typing import List
from fastapi_limiter import FastAPILimiter



router = APIRouter()

@router.post("/contacts/", response_model=schemas.Contact, description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def create_contact(contact: dict, limit: int = 100, db: Session = Depends(get_db)):
    """
        Create a new contact.

        :param contact: Contact details.
        :param limit: Rate limit for creating contacts.
        :param db: Database session.
        :return: Created contact.
        """
    return crud.create_contact(db, contact, limit)

@router.get("/contacts/", response_model=List[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
        Get a list of contacts.

        :param skip: Number of contacts to skip.
        :param limit: Number of contacts to retrieve.
        :param db: Database session.
        :return: List of contacts.
        """
    contacts = crud.get_contacts(db, skip=skip, limit=limit)
    return contacts

@router.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """
        Get details of a specific contact.

        :param contact_id: ID of the contact.
        :param db: Database session.
        :return: Contact details.
        """
    contact = crud.get_contact(db, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    """
        Update details of a specific contact.

        :param contact_id: ID of the contact.
        :param contact: Updated contact details.
        :param db: Database session.
        :return: Updated contact details.
        """
    updated_contact = crud.update_contact(db, contact_id, contact)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact

@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    """
        Delete a specific contact.

        :param contact_id: ID of the contact to delete.
        :param db: Database session.
        :return: Deleted contact details.
        """
    deleted_contact = crud.delete_contact(db, contact_id)
    if deleted_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted_contact

@router.get("/contacts/search/", response_model=List[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db)):
    """
        Search for contacts based on a query.

        :param query: Search query.
        :param db: Database session.
        :return: List of matching contacts.
        """
    contacts = crud.search_contacts(db, query)
    return contacts


@router.get("/contacts/birthdays/", response_model=List[schemas.Contact])
def upcoming_birthdays(db: Session = Depends(get_db)):
    """
        Get upcoming birthdays.

        :param db: Database session.
        :return: List of contacts with upcoming birthdays.
        """
    contacts = crud.get_upcoming_birthdays(db)
    return contacts

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Додайте інші маршрути для CRUD операцій та додаткових функціональних вимог.
