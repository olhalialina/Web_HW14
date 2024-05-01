from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.config import messages
from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactUpdate, ContactResponse
from src.repository import contacts as repository_contacts
from src.routes.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], description=messages.NO_MORE_THAN,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(skip: int = 0, limit: int = 100,
                       current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The get_contacts function retrieves a list of contacts.

    :param skip: int: Determine how many records to skip
    :param limit: int: Limit the number of contacts returned
    :param current_user: User: Get the currently authenticated user
    :param db: Session: Pass the database session to the repository layer
    :return: A list of contactresponse objects
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, description=messages.NO_MORE_THAN,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function retrieves a contact from the database by its ID.

    :param contact_id: int: Specify the id of the contact to retrieve
    :param db: Session: Pass the database session to the function
    :param current_user: User: Ensure that the user making the request is authorized to do so
    :return: A contactresponse object
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contact


@router.get("/search/first_name", response_model=List[ContactResponse], description=messages.NO_MORE_THAN,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts_first_name(first_name: str, db: Session = Depends(get_db),
                                  current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_first_name function retrieves contacts from the database based on the provided first name. It uses
    the `get_contacts_first_name` method from the `repository_contacts` module to perform the database query. If no
    contacts are found, it raises an HTTPException with a status code of 404 and a detail message of &quot;Contact not
    found&quot;.

    :param first_name: str: Specify the first name of the contacts to search for
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A list of contacts matching the given first name
    """
    contacts = await repository_contacts.get_contacts_first_name(first_name, current_user, db)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contacts


@router.get("/search/last_name", response_model=List[ContactResponse], description=messages.NO_MORE_THAN,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts_last_name(last_name: str, db: Session = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_last_name function is used to get contacts by last name.

    :param last_name: str: Get contacts by last name
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A list of contacts with the given last name
    """
    contacts = await repository_contacts.get_contacts_last_name(last_name, current_user, db)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contacts


@router.get("/search/email", response_model=List[ContactResponse], description=messages.NO_MORE_THAN,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts_email(email: str, db: Session = Depends(get_db),
                             current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_email function retrieves contacts by email address.

    :param email: str: Specify the email address of the contact
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current authenticated user
    :return: A list of contactresponse objects representing the contacts with the specified email
    """
    contacts = await repository_contacts.get_contacts_email(email, current_user, db)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contacts


@router.get("/search/birthdays", response_model=List[ContactResponse],
            description=messages.NO_MORE_THAN,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_birthdays(db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The get_birthdays function retrieves the birthdays of contacts.

    :param db: Session: Pass the database session to the function
    :param current_user: User: Retrieve the current user
    :return: A list of contact responses
    """
    contacts = await repository_contacts.get_contacts_birthday(current_user, db)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contacts


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             description=messages.NO_MORE_THAN,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact.

    :param body: ContactModel: Pass the contact data to be created
    :param db: Session: Pass the database session dependency
    :param current_user: User: Get the currently authenticated user
    :return: A contactresponse
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse, description=messages.NO_MORE_THAN,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact with the given contact_id using the provided ContactUpdate body.

    :param body: ContactUpdate: Pass the updated contact information to the function
    :param contact_id: int: Identify the contact to be deleted
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current authenticated user
    :return: A contactresponse object
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, description=messages.NO_MORE_THAN,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be updated
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A contactresponse
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.CONTACT_NOT_FOUND)
    return contact