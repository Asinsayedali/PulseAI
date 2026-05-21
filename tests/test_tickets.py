# Tests to implement:
#   - POST /api/v1/tickets       → 201, ticket created, ai fields null
#   - GET  /api/v1/tickets       → 200, paginated list
#   - GET  /api/v1/tickets/{id}  → 200, ticket detail
#   - GET  /api/v1/tickets/{id}  → 404, not found
#   - PATCH /api/v1/tickets/{id} → 200, status updated
#   - PATCH /api/v1/tickets/{id} → 403, not owner or admin
