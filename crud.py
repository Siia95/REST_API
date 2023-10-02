from sqlalchemy.orm import Session
import models
from models import Contact
from schemas import ContactCreate, ContactUpdate
from datetime import date, timedelta, datetime


def create_contact(db: Session, contact: ContactCreate):
    """
        Create a new contact.

        :param db: The database session.
        :param contact: The contact details.
        :return: The created contact.
        """
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, skip: int = 0, limit: int = 10):
    """
        Get a list of contacts.

        :param db: The database session.
        :param skip: The number of contacts to skip.
        :param limit: The maximum number of contacts to return.
        :return: A list of contacts.
        """
    return db.query(Contact).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int):
    """
        Get a specific contact by ID.

        :param db: The database session.
        :param contact_id: The ID of the contact.
        :return: The contact with the specified ID.
        """
    return db.query(Contact).filter(Contact.id == contact_id).first()

def update_contact(db: Session, contact_id: int, contact: ContactUpdate):
    """
        Update the details of a contact.

        :param db: The database session.
        :param contact_id: The ID of the contact to update.
        :param contact: The updated contact details.
        :return: The updated contact.
        """
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
        return db_contact
    return None

def delete_contact(db: Session, contact_id: int):
    """
        Delete a contact by ID.

        :param db: The database session.
        :param contact_id: The ID of the contact to delete.
        :return: The deleted contact.
        """
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
        return db_contact
    return None

def search_contacts(db: Session, query: str):
    """
        Search for contacts by a query string.

        :param db: The database session.
        :param query: The search query.
        :return: A list of contacts matching the search query.
        """
    return db.query(Contact).filter(
        (Contact.first_name.ilike(f"%{query}%")) |
        (Contact.last_name.ilike(f"%{query}%")) |
        (Contact.email.ilike(f"%{query}%"))
    ).all()


def get_upcoming_birthdays(db: Session):
    """
        Get contacts with upcoming birthdays within the next 7 days.

        :param db: The database session.
        :return: A list of contacts with upcoming birthdays.
        """
    today = datetime.now().date()
    seven_days_later = today + timedelta(days=7)

    contacts = db.query(models.Contact).filter(
        models.Contact.birth_date >= today,
        models.Contact.birth_date <= seven_days_later
    ).all()

    return contacts

