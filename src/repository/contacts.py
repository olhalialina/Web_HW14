from datetime import date, timedelta
from typing import List, Type
from sqlalchemy import String, and_, extract, func, or_

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    The get_contacts function retrieves contacts based on the provided skip, limit, user, and database session parameters.

    :param skip: int: Indicate the number of records to skip
    :param limit: int: Limit the number of records that are returned
    :param user: User: Specify the user whose contacts are being retrieved
    :param db: Session: Create a database session object
    :return: A list of contact objects that match the criteria specified
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Type[Contact] | None:
    """
    The get_contact function retrieves a contact from the database based on the provided contact ID, user, and database session.

    :param contact_id: int: Specify the id of the contact to retrieve
    :param user: User: Ensure that the contact is associated with the user
    :param db: Session: Execute the query
    :return: A contact object or none
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id), Contact.user_id == user.id).first()


async def get_contacts_first_name(first_name: str, user: User, db: Session) -> list[Type[Contact]]:
    """
    The get_contacts_first_name function retrieves contacts by first name for a specific user from the database.

    :param first_name: str: Specify the first name to search for in contacts
    :param user: User: Retrieve contacts for a specific user
    :param db: Session: Pass the database session object to the function
    :return: A list of contact objects
    """
    return db.query(Contact).filter(and_(Contact.first_name.like(f'%{first_name}%'), Contact.user_id == user.id)).all()


async def get_contacts_last_name(last_name: str, user: User, db: Session) -> list[Type[Contact]]:
    """
    The get_contacts_last_name function asynchronously retrieves a list of contacts with a specific last name for the given user.

    :param last_name: str: Specify the last name to search for
    :param user: User: Pass in the user object
    :param db: Session: Pass the database session to the function
    :return: A list of contact objects which have the specified last name
    """
    return db.query(Contact).filter(and_(Contact.last_name.like(f'%{last_name}%'), Contact.user_id == user.id)).all()


async def get_contacts_email(email_part: str, user: User, db: Session) -> list[Type[Contact]]:
    """
    The get_contacts_email function retrieves contacts with emails containing a specific part, belonging to a user.

    :param email_part: str: Specify the part of the email to search for
    :param user: User: Filter the contacts by user
    :param db: Session: Create a database session
    :return: A list of contact objects that match the search criteria
    """
    return db.query(Contact).filter(and_(Contact.email.like(f'%{email_part}%'), Contact.user_id == user.id)).all()


async def get_contacts_birthday(user: User, db: Session) -> list[Type[Contact]]:
    """
    The get_contacts_birthday function retrieves a list of contacts whose birthday is within the next 7 days for a given user.

    :param user: User: Specify the user for whom to retrieve contacts
    :param db: Session: Pass the database session to the function
    :return: A list of contact objects whose birthday is within the next 7 days
    """
    days = []
    for i in range(7):
        day = date.today() + timedelta(days=i)
        days.append(str(day.day) + str(day.month))

    contacts = db.query(Contact).filter(and_(
        or_(func.concat(
            extract('day', Contact.born_date).cast(String),
            extract('month', Contact.born_date).cast(String)
        ).in_(days))), Contact.user_id == user.id).all()
    return contacts


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactModel: Get the data from the request body
    :param user: User: Get the user id of the contact
    :param db: Session: Pass the database session to the function
    :return: A contact object
    """
    contact = Contact(first_name=body.first_name, last_name=body.last_name, email=body.email,
                      phone_number=body.phone_number, born_date=body.born_date,
                      description=body.description, user_id=user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be updated
    :param user: User: Get the user object from the database
    :param db: Session: Pass the database session object to the function
    :return: The removed contact object if it exists, otherwise none
    """
    contact = db.query(Contact).filter(
        and_(Contact.id == contact_id), Contact.user_id == user.id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Specify the id of the contact to update
    :param body: ContactUpdate: Pass in the new information for the contact
    :param user: User: Ensure that the user performing the update is authorized to do so
    :param db: Session: Pass the database connection to the function
    :return: The updated contact object or none if the contact was not found
    """
    contact = db.query(Contact).filter(
        and_(Contact.id == contact_id), Contact.user_id == user.id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.born_date = body.born_date
        contact.description = body.description
        db.commit()
    return contact