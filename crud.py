from sqlalchemy.orm import Session
import models
from models import Contact
from schemas import ContactCreate, ContactUpdate
from datetime import date, timedelta, datetime


def create_contact(db: Session, contact: ContactCreate):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Contact).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int):
    return db.query(Contact).filter(Contact.id == contact_id).first()

def update_contact(db: Session, contact_id: int, contact: ContactUpdate):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    return None

def delete_contact(db: Session, contact_id: int):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return db_contact
    return None

def search_contacts(db: Session, query: str):
    return db.query(Contact).filter(
        (Contact.first_name.ilike(f"%{query}%")) |
        (Contact.last_name.ilike(f"%{query}%")) |
        (Contact.email.ilike(f"%{query}%"))
    ).all()


def get_upcoming_birthdays(db: Session):
    today = datetime.now().date()
    seven_days_later = today + timedelta(days=7)

    contacts = db.query(models.Contact).filter(
        models.Contact.birth_date >= today,
        models.Contact.birth_date <= seven_days_later
    ).all()

    return contacts

