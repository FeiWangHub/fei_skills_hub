---
name: api-design-principles
description: Master REST and GraphQL API design principles to build intuitive, scalable, and maintainable APIs that delight developers. Use when designing new APIs, reviewing API specifications, or establishing API design standards.
---
# API Design Principles
Master REST and GraphQL API design principles to build intuitive, scalable, and maintainable APIs that delight developers and stand the test of time.
## When to Use This Skill
- Designing new REST or GraphQL APIs
- Refactoring existing APIs for better usability
- Establishing API design standards for your team
- Reviewing API specifications before implementation
- Migrating between API paradigms (REST to GraphQL, etc.)
- Creating developer-friendly API documentation
- Optimizing APIs for specific use cases (mobile, third-party integrations)
## Core Concepts
### 1. RESTful Design Principles
**Resource-Oriented Architecture**
- Resources are nouns (users, orders, products), not verbs
- Use HTTP methods for actions (GET, POST, PUT, PATCH, DELETE)
- URLs represent resource hierarchies
- Consistent naming conventions
**HTTP Methods Semantics:**
- `GET`: Retrieve resources (idempotent, safe)
- `POST`: Create new resources
- `PUT`: Replace entire resource (idempotent)
- `PATCH`: Partial resource updates
- `DELETE`: Remove resources (idempotent)
### 2. GraphQL Design Principles
**Schema-First Development**
- Types define your domain model
- Queries for reading data
- Mutations for modifying data
- Subscriptions for real-time updates
**Query Structure:**
- Clients request exactly what they need
- Single endpoint, multiple operations
- Strongly typed schema
- Introspection built-in
### 3. API Versioning Strategies
**URL Versioning:**
```
/api/v1/users
/api/v2/users
```
**Header Versioning:**
```
Accept: application/vnd.api+json; version=1
```
**Query Parameter Versioning:**
```
/api/users?version=1
```
## REST API Design Patterns
### Pattern 1: Resource Collection Design
```
# Good: Resource-oriented endpoints
GET    /api/users              # List users (with pagination)
POST   /api/users              # Create user
GET    /api/users/{id} # Get specific user
PUT    /api/users/{id} # Replace user
PATCH  /api/users/{id} # Update user fields
DELETE /api/users/{id} # Delete user

# Nested resources
GET    /api/users/{id}/orders  # Get user's orders
POST   /api/users/{id}/orders  # Create order for user
```
### Pattern 2: Pagination and Filtering
```python
from typing import List, Optional
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

class FilterParams(BaseModel):
    status: Optional[str] = None
    created_after: Optional[str] = None
    search: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    page_size: int
    pages: int
```
## API Design Checklist
### Resource Design
- [ ] Resources are nouns, not verbs
- [ ] Plural names for collections
- [ ] Consistent naming across all endpoints
- [ ] Clear resource hierarchy (avoid deep nesting >2 levels)
- [ ] All CRUD operations properly mapped to HTTP methods
### HTTP Methods
- [ ] GET for retrieval (safe, idempotent)
- [ ] POST for creation
- [ ] PUT for full replacement (idempotent)
- [ ] PATCH for partial updates
- [ ] DELETE for removal (idempotent)
### Status Codes
- [ ] 200 OK for successful GET/PATCH/PUT
- [ ] 201 Created for POST
- [ ] 204 No Content for DELETE
- [ ] 400 Bad Request for malformed requests
- [ ] 401 Unauthorized for missing auth
- [ ] 403 Forbidden for insufficient permissions
- [ ] 404 Not Found for missing resources
- [ ] 422 Unprocessable Entity for validation errors
- [ ] 429 Too Many Requests for rate limiting
- [ ] 500 Internal Server Error for server issues
### Error Handling
- [ ] Consistent error response format
- [ ] Detailed error messages
- [ ] Field-level validation errors
- [ ] Error codes for client handling
- [ ] Timestamps in error responses
### Security
- [ ] Input validation on all fields
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CORS configured correctly
- [ ] HTTPS enforced
- [ ] Sensitive data not in URLs
- [ ] No secrets in responses
