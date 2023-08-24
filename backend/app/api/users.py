from typing import Any, List
import requests

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import Response

from app.core.logger import logger
from app.deps.db import get_async_session
from app.deps.users import current_superuser
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter()


@router.get("/users", response_model=List[UserRead])
async def get_users(
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    logger.info("Fetching users")
    try:
        total = await session.scalar(select(func.count(User.id)))
        users = (
        (await session.execute(select(User).offset(skip).limit(limit))).scalars().all()
        )
        response.headers["Content-Range"] = f"{skip}-{skip + len(users)}/{total}"
    except requests.RequestException:
        pass
    return users

@router.get("/users/valid", response_model=List[UserRead])
async def get_valid_users(
    response: Response,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
   logger.info("Fetching valid users")
   total = await session.scalar(select(func.count(User.id)))
   # fetch all the users
   users = ((await session.execute(select(User).offset(skip).limit(limit))).scalars().all() )
   valid_users = []
   # similar to try catch approach
   for each_user in users:
        email_domain =  each_user.email.split('@')[1]    # domain of the user email to access via GET
        try:
            response_valid = requests.get(f"http://{email_domain}")  
            if response_valid.status_code == 200:            #check if valid domain
               valid_users.append(each_user)                # add to the list of valid users
        except requests.RequestException:
            pass
   response.headers["Content-Range"] = f"{skip}-{skip + len(valid_users)}/{total}"
   return valid_users  
