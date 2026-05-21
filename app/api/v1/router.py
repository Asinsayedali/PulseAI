from fastapi import APIRouter
from app.controllers import auth, tickets, comments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(comments.router, prefix="/tickets", tags=["Comments"])
