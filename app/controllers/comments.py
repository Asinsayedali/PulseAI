from fastapi import APIRouter

router = APIRouter()

# POST  /tickets/{ticket_id}/comments  →  comment_service.add_comment()
# GET   /tickets/{ticket_id}/comments  →  comment_service.list_comments()
