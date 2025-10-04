from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas import auth_schemas
from app.controllers.auth_controller import AuthController
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/login", response_model=auth_schemas.TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await AuthController.login(form_data, db)

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return await AuthController.logout(token, db)

@router.get("/session", response_model=auth_schemas.SessionInfo)
async def get_session_info(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return await AuthController.get_session_info(token, db)