import unittest

from datetime import date, timedelta

from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_contacts_first_name,
    get_contacts_last_name,
    get_contacts_email,
    get_contacts_birthday,
    create_contact,
    remove_contact,
    update_contact,
)


class TestContactFunctions(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_nonexistent(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_first_name(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_first_name("Brad", user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_last_name(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_last_name("Lee", user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_email(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_email("example.com", user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_birthday(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts_birthday(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        contact_data = ContactModel(
            first_name="Brad",
            last_name="Lee",
            email="john@example.com",
            phone_number="1234567890",
            born_date=date.today(),
            description="A test contact",
        )
        expected_contact = Contact(**contact_data.dict(), user_id=self.user.id)
        self.session.add(expected_contact)
        self.session.commit()
        self.session.refresh(expected_contact)
        result = await create_contact(body=contact_data, user=self.user, db=self.session)

        result_dict = result.__dict__.copy()
        expected_contact_dict = expected_contact.__dict__.copy()
        result_dict.pop('_sa_instance_state', None)
        expected_contact_dict.pop('_sa_instance_state', None)

        self.assertDictEqual(result_dict, expected_contact_dict)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.delete(contact)
        self.session.commit.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        contact_data = ContactUpdate(
            first_name="Updated Brad",
            last_name="Updated Lee",
            email="updated@example.com",
            phone_number="9876543210",
            born_date=date.today() - timedelta(days=365),
            description="Updated contact",
        )
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        contact.first_name = contact_data.first_name
        contact.last_name = contact_data.last_name
        contact.email = contact_data.email
        contact.phone_number = contact_data.phone_number
        contact.born_date = contact_data.born_date
        contact.description = contact_data.description
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=contact_data, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        contact_data = ContactUpdate(
            first_name="Updated Brad",
            last_name="Updated Lee",
            email="updated@example.com",
            phone_number="9876543210",
            born_date=date.today() - timedelta(days=365),
            description="Updated contact",
        )
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=1, body=contact_data, user=self.user, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()