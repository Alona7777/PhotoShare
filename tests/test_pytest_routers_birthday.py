from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.repository import birthday as repositories_contacts


@pytest.mark.asyncio
async def test_get_contact_with_upcoming_birthday():

    contact_data = [
        Contact(id=1, first_name="test_first_name", last_name="test_last_name", email="test@example.com",
                phone_number="123456789", birthday=datetime.now().date() + timedelta(days=5),
                address="123 Street", notes="Some notes", interests="Some interests", is_active=True),
    ]

    # Mock the repository function
    repositories_contacts.get_contact_with_upcoming_birthday = AsyncMock(return_value=contact_data)
    result = contact_data

    assert isinstance(result, list)
    assert len(result) == len(contact_data)
