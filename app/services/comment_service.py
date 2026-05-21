# Business logic for comment operations
# add_comment(ticket_id: int, data: CommentCreate, user_id: str, session) -> Comment
# list_comments(ticket_id: int, session) -> list[CommentResponse]
#
# Responsibilities:
#   - verify ticket exists via ticket_repo
#   - create comment via comment_repo
