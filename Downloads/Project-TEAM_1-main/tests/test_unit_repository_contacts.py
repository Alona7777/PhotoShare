import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository import contacts as repositories_contacts


class TestAsyncContacts(unittest.IsolatedAsyncioTestCase) :

    async def test_get_contacts(self) :
        limit = 10
        offset = 0
        contacts = [
            Contact(id = 1, first_name = 'test_first_name_1', last_name = 'test_last_name_1', email = 'test_email_1',
                    phone_number = 'test_phone_number_1', birthday = 'test_birthday_1', address = 'test_address_1',
                    notes = 'test_notes_1', user = self.user),
            Contact(id = 2, first_name = 'test_first_name_2', last_name = 'test_last_name_2', email = 'test_email_2',
                    phone_number = 'test_phone_number_2', birthday = 'test_birthday_2', address = 'test_address_2',
                    notes = 'test_notes_2', user = self.user),
            Contact(id = 3, first_name = 'test_first_name_3', last_name = 'test_last_name_3', email = 'test_email_3',
                    phone_number = 'test_phone_number_3', birthday = 'test_birthday_3', address = 'test_address_3',
                    notes = 'test_notes_3', user = self.user),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await repositories_contacts.get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    def setUp(self) -> None :
        self.user = User(id = 1, username = 'test_user', password = "qwerty", verified = True)
        self.session = AsyncMock(spec = AsyncSession)

    async def test_get_all_contacts(self) :
        limit = 10
        offset = 0
        contacts = [
            Contact(id = 1, first_name = 'test_first_name_1', last_name = 'test_last_name_1', email = 'test_email_1',
                    phone_number = 'test_phone_number_1', birthday = 'test_birthday_1', address = 'test_address_1',
                    notes = 'test_notes_1', user = self.user),
            Contact(id = 2, first_name = 'test_first_name_2', last_name = 'test_last_name_2', email = 'test_email_2',
                    phone_number = 'test_phone_number_2', birthday = 'test_birthday_2', address = 'test_address_2',
                    notes = 'test_notes_2', user = self.user),
            Contact(id = 3, first_name = 'test_first_name_3', last_name = 'test_last_name_3', email = 'test_email_3',
                    phone_number = 'test_phone_number_3', birthday = 'test_birthday_3', address = 'test_address_3',
                    notes = 'test_notes_3', user = self.user),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await repositories_contacts.get_all_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self) :
        contact_id = 1
        contacts = [
            Contact(id = 1, first_name = 'test_first_name_1', last_name = 'test_last_name_1', email = 'test_email_1',
                    phone_number = 'test_phone_number_1', birthday = 'test_birthday_1', address = 'test_address_1',
                    notes = 'test_notes_1'),
            Contact(id = 2, first_name = 'test_first_name_2', last_name = 'test_last_name_2', email = 'test_email_2',
                    phone_number = 'test_phone_number_2', birthday = 'test_birthday_2', address = 'test_address_2',
                    notes = 'test_notes_2'),
            Contact(id = 3, first_name = 'test_first_name_3', last_name = 'test_last_name_3', email = 'test_email_3',
                    phone_number = 'test_phone_number_3', birthday = 'test_birthday_3', address = 'test_address_3',
                    notes = 'test_notes_3'),
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await repositories_contacts.get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_create_contact(self) :
        body = ContactSchema(
            first_name = 'test_first_name',
            last_name = 'test_last_name',
            email = 'test@example.com',
            phone_number = 'test_phone_number',
            birthday = '2024-04-21',
            address = 'test_address',
            notes = 'test_notes',
            interests = 'string',
            current_user = self.user
        )
        result = await repositories_contacts.create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.address, body.address)
        self.assertEqual(result.notes, body.notes)
        self.assertEqual(result.interests, body.interests)

    async def test_update_contact(self) :
        body = ContactUpdateSchema(
            first_name = 'test_first_name',
            last_name = 'test_last_name',
            email = 'test@example.com',
            phone_number = 'test_phone_number',
            birthday = '2024-04-21',
            address = 'test_address',
            notes = 'test_notes',
            interests = 'string',
            is_active = True,
            current_user = self.user
        )
        contacts = Contact(id = 1, first_name = 'test_first_name', last_name = 'test_last_name', email = 'test_email',
                           phone_number = 'test_phone_number', birthday = 'test_birthday', address = 'test_address',
                           notes = 'test_notes', user = self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await repositories_contacts.update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.address, body.address)
        self.assertEqual(result.notes, body.notes)
        self.assertEqual(result.interests, body.interests)

    async def test_delete_contacts(self):
        contact_id = 1
        contacts = Contact(id = 1, first_name = 'test_first_name', last_name = 'test_last_name', email = 'test_email',
                           phone_number = 'test_phone_number', birthday = 'test_birthday', address = 'test_address',
                           notes = 'test_notes', user = self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contacts
        self.session.execute.return_value = mocked_contact
        result = await repositories_contacts.delete_contact(contact_id, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)
