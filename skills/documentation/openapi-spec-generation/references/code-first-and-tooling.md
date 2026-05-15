# OpenAPI Code-First Generation and Tooling
Advanced patterns for generating OpenAPI specs from code (Python/FastAPI, TypeScript/tsoa), validation, linting, and SDK generation.
## Template 2: Code-First Generation (Python/FastAPI)
```python
from fastapi import FastAPI, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum
app = FastAPI(
    title="User Management API",
    description="API for managing users and profiles",
    version="2.0.0",
    openapi_tags=[
        {"name": "Users", "description": "User operations"},
        {"name": "Profiles", "description": "Profile operations"},
    ],
    servers=[
        {"url": "https://api.example.com/v2", "description": "Production"},
        {"url": "http://localhost:8000", "description": "Development"},
    ],
)
class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    pending = "pending"
class UserRole(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"
class UserCreate(UserBase):
    role: UserRole = Field(default=UserRole.user)
    metadata: Optional[dict] = Field(default=None)
    model_config = {"json_schema_extra": {"examples": [{"email": "user@example.com", "name": "John Doe", "role": "user"}]}}
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    metadata: Optional[dict] = None
class User(UserBase):
    id: UUID = Field(..., description="Unique identifier")
    status: UserStatus
    role: UserRole
    avatar: Optional[str] = Field(None)
    metadata: Optional[dict] = None
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    model_config = {"populate_by_name": True}
class Pagination(BaseModel):
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0, alias="totalPages")
    has_next: bool = Field(..., alias="hasNext")
    has_prev: bool = Field(..., alias="hasPrev")
class UserListResponse(BaseModel):
    data: List[User]
    pagination: Pagination
@app.get("/users", response_model=UserListResponse, tags=["Users"], summary="List all users")
async def list_users(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), status: Optional[UserStatus] = Query(None), search: Optional[str] = Query(None, min_length=2, max_length=100)):
    pass
@app.post("/users", response_model=User, status_code=201, tags=["Users"], summary="Create a new user")
async def create_user(user: UserCreate):
    pass
@app.get("/users/{user_id}", response_model=User, tags=["Users"], summary="Get user by ID")
async def get_user(user_id: UUID = Path(..., description="User ID")):
    pass
@app.patch("/users/{user_id}", response_model=User, tags=["Users"], summary="Update user")
async def update_user(user_id: UUID = Path(...), user: UserUpdate = ...):
    pass
@app.delete("/users/{user_id}", status_code=204, tags=["Users", "Admin"], summary="Delete user")
async def delete_user(user_id: UUID = Path(...)):
    pass
if __name__ == "__main__":
    import json
    print(json.dumps(app.openapi(), indent=2))
```
## Template 3: Code-First (TypeScript/Express with tsoa)
```typescript
import { Controller, Get, Post, Patch, Delete, Route, Path, Query, Body, Response, SuccessResponse, Tags, Security, Example } from "tsoa";
interface User {
  id: string;
  email: string;
  name: string;
  status: UserStatus;
  role: UserRole;
  avatar?: string;
  metadata?: Record<string, unknown>;
  createdAt: Date;
  updatedAt?: Date;
}
enum UserStatus { Active = "active", Inactive = "inactive", Suspended = "suspended", Pending = "pending" }
enum UserRole { User = "user", Moderator = "moderator", Admin = "admin" }
interface CreateUserRequest { email: string; name: string; role?: UserRole; metadata?: Record<string, unknown>; }
interface UpdateUserRequest { name?: string; status?: UserStatus; role?: UserRole; metadata?: Record<string, unknown>; }
interface Pagination { page: number; limit: number; total: number; totalPages: number; hasNext: boolean; hasPrev: boolean; }
interface UserListResponse { data: User[]; pagination: Pagination; }
interface ErrorResponse { code: string; message: string; details?: { field: string; message: string }[]; requestId?: string; }
@Route("users")
@Tags("Users")
export class UsersController extends Controller {
  @Get()
  @Security("bearerAuth")
  @Response<ErrorResponse>(400, "Invalid request")
  @Example<UserListResponse>({ data: [{ id: "550e8400-e29b-41d4-a716-446655440000", email: "john@example.com", name: "John Doe", status: UserStatus.Active, role: UserRole.User, createdAt: new Date("2024-01-15T10:30:00Z") }], pagination: { page: 1, limit: 20, total: 1, totalPages: 1, hasNext: false, hasPrev: false } })
  public async listUsers(@Query() page: number = 1, @Query() limit: number = 20, @Query() status?: UserStatus, @Query() search?: string): Promise<UserListResponse> { throw new Error("Not implemented"); }
  @Post()
  @Security("bearerAuth")
  @SuccessResponse(201, "Created")
  public async createUser(@Body() body: CreateUserRequest): Promise<User> { this.setStatus(201); throw new Error("Not implemented"); }
  @Get("{userId}")
  @Security("bearerAuth")
  @Response<ErrorResponse>(404, "User not found")
  public async getUser(@Path() userId: string): Promise<User> { throw new Error("Not implemented"); }
  @Patch("{userId}")
  @Security("bearerAuth")
  @Response<ErrorResponse>(400, "Invalid request")
  @Response<ErrorResponse>(404, "User not found")
  public async updateUser(@Path() userId: string, @Body() body: UpdateUserRequest): Promise<User> { throw new Error("Not implemented"); }
  @Delete("{userId}")
  @Tags("Users", "Admin")
  @Security("bearerAuth")
  @SuccessResponse(204, "Deleted")
  @Response<ErrorResponse>(404, "User not found")
  public async deleteUser(@Path() userId: string): Promise<void> { this.setStatus(204); }
}
```
## Template 4: Validation & Linting
```bash
npm install -g @stoplight/spectral-cli
npm install -g @redocly/cli
# Spectral ruleset (.spectral.yaml)
cat > .spectral.yaml << 'EOF'
extends: ["spectral:oas", "spectral:asyncapi"]
rules:
  operation-operationId: error
  operation-description: warn
  info-description: error
  operation-security-defined: error
  operation-success-response: error
  path-params-snake-case:
    description: Path parameters should be snake_case
    severity: warn
    given: "$.paths[*].parameters[?(@.in == 'path')].name"
    then:
      function: pattern
      functionOptions:
        match: "^[a-z][a-z0-9_]*$"
EOF
spectral lint openapi.yaml
# Redocly config (redocly.yaml)
cat > redocly.yaml << 'EOF'
extends:
  - recommended
rules:
  no-invalid-media-type-examples: error
  no-invalid-schema-examples: error
theme:
  openapi:
    generateCodeSamples:
      languages:
        - lang: curl
        - lang: python
        - lang: javascript
EOF
redocly lint openapi.yaml
redocly preview-docs openapi.yaml
```
## SDK Generation
```bash
npm install -g @openapitools/openapi-generator-cli
# Generate TypeScript client
openapi-generator-cli generate -i openapi.yaml -g typescript-fetch -o ./generated/typescript-client --additionalProperties=supportsES6=true,npmName=@myorg/api-client
# Generate Python client
openapi-generator-cli generate -i openapi.yaml -g python -o ./generated/python-client --additionalProperties=packageName=api_client
# Generate Go client
openapi-generator-cli generate -i openapi.yaml -g go -o ./generated/go-client
```
