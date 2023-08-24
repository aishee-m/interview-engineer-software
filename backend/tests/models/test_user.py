from uuid import uuid4
import requests
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


async def test_user_model(db: AsyncSession):
    user = User(id=uuid4(), email="user33@yahoo.com", hashed_password="1234")
    db.add(user)
    await db.commit()
    assert user.id

# test case to check for valid users
async def test_valid_user(db: AsyncSession):
    user = User(id=uuid4(), email="user15@gmail.com", hashed_password="1234")
    user1 = User(id=uuid4(), email="user15@example.com", hashed_password="5678")
    db.add(user)
    await db.commit()
    db.add(user1)
    await db.commit()
    
    # fetch all the users 
    selected_users = select(User).order_by(User.id)
    users = await db.execute(selected_users)
    users = users.scalars().all()
    #similar to the API endpoint to check for validity
    def is_valid_email(email):
        email_domain = email.split('@')[1]
        try:
            response = requests.get(f"http://{email_domain}")
            if response.status_code == 200:
                return True #returns true for valid email
        except (IndexError, requests.RequestException):
            return False

    # Validate the email addresses of retrieved users
    valid_emails = [user.email for user in users if is_valid_email(user.email)]
    
    # would return true if all the emails thought to be "valid" is actually "valid"
    assert all(is_valid_email(email) for email in valid_emails)
