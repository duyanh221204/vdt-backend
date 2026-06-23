from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from dto.response.auth_response import AuthResponse
from service.auth_service import AuthService, get_auth_service

router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication']
)


@router.post('/login', response_model=AuthResponse)
async def authenticate(
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    return await auth_service.authenticate(data)
