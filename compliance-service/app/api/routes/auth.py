"""
Authentication and debug routes.
Provides endpoints for token validation and inspection.
"""

from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import (
    get_current_user,
    get_current_active_user,
    TokenData,
    require_role,
    require_permission,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create router for auth-related endpoints
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


class TokenDebugResponse(BaseModel):
    """Response model for token debug endpoint."""

    message: str
    user_id: str
    username: str | None
    email: str | None
    roles: list[str]
    permissions: list[str]
    groups: list[str]
    issuer: str | None
    audience: str | list[str] | None
    expires_at: int | None
    issued_at: int | None
    all_claims: dict


class WhoAmIResponse(BaseModel):
    """Response model for whoami endpoint."""

    user_id: str
    username: str | None
    email: str | None
    roles: list[str]
    permissions: list[str]


@router.get("/debug", response_model=TokenDebugResponse)
async def debug_token(
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> TokenDebugResponse:
    """
    Debug endpoint to inspect JWT token contents.
    Returns all decoded information from the token.

    **Authentication Required**: Bearer token in Authorization header

    Example:
    ```
    curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
         http://localhost:8000/api/v1/auth/debug
    ```

    Returns:
    - User identification (sub, username, email)
    - Roles assigned to the user
    - Permissions/scopes
    - Groups membership
    - Token metadata (issuer, audience, expiration)
    - All raw claims from the token
    """
    logger.info(f"Debug token request for user: {current_user.sub}")

    return TokenDebugResponse(
        message="Token decoded successfully",
        user_id=current_user.sub,
        username=current_user.username,
        email=current_user.email,
        roles=current_user.roles,
        permissions=current_user.permissions,
        groups=current_user.groups,
        issuer=current_user.iss,
        audience=current_user.aud,
        expires_at=current_user.exp,
        issued_at=current_user.iat,
        all_claims=current_user.raw_claims,
    )


@router.get("/whoami", response_model=WhoAmIResponse)
async def whoami(
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> WhoAmIResponse:
    """
    Get current authenticated user information.
    Returns basic user details without exposing all token claims.

    **Authentication Required**: Bearer token in Authorization header

    Example:
    ```
    curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
         http://localhost:8000/api/v1/auth/whoami
    ```

    Returns:
    - User ID
    - Username
    - Email
    - Assigned roles
    - Granted permissions
    """
    logger.info(f"WhoAmI request for user: {current_user.username or current_user.sub}")

    return WhoAmIResponse(
        user_id=current_user.sub,
        username=current_user.username,
        email=current_user.email,
        roles=current_user.roles,
        permissions=current_user.permissions,
    )


@router.get("/verify")
async def verify_token(
    current_user: Annotated[TokenData, Depends(get_current_user)],
) -> dict:
    """
    Simple token verification endpoint.
    Returns success if token is valid.

    **Authentication Required**: Bearer token in Authorization header

    Example:
    ```
    curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
         http://localhost:8000/api/v1/auth/verify
    ```

    Returns:
    - Success message with user ID
    """
    logger.info(f"Token verified for user: {current_user.sub}")

    return {
        "valid": True,
        "user_id": current_user.sub,
        "message": "Token is valid",
    }


@router.get("/roles")
async def list_my_roles(
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> dict:
    """
    List all roles assigned to the current user.

    **Authentication Required**: Bearer token in Authorization header

    Returns:
    - List of role names
    - Count of roles
    """
    logger.info(f"Roles requested for user: {current_user.sub}")

    return {
        "user_id": current_user.sub,
        "roles": current_user.roles,
        "role_count": len(current_user.roles),
    }


@router.get("/permissions")
async def list_my_permissions(
    current_user: Annotated[TokenData, Depends(get_current_active_user)],
) -> dict:
    """
    List all permissions/scopes assigned to the current user.

    **Authentication Required**: Bearer token in Authorization header

    Returns:
    - List of permissions
    - Count of permissions
    """
    logger.info(f"Permissions requested for user: {current_user.sub}")

    return {
        "user_id": current_user.sub,
        "permissions": current_user.permissions,
        "permission_count": len(current_user.permissions),
    }


# Example protected endpoints demonstrating role-based access


@router.get("/admin-only")
async def admin_only_endpoint(
    current_user: Annotated[TokenData, Depends(require_role("admin"))],
) -> dict:
    """
    Example endpoint that requires 'admin' role.
    Only users with 'admin' role can access this.

    **Authentication Required**: Bearer token with 'admin' role

    Returns:
    - Success message
    - User information
    """
    logger.info(f"Admin endpoint accessed by: {current_user.sub}")

    return {
        "message": "Welcome, admin!",
        "user_id": current_user.sub,
        "roles": current_user.roles,
    }


@router.get("/manager-or-admin")
async def manager_or_admin_endpoint(
    current_user: Annotated[TokenData, Depends(require_role("manager", "admin"))],
) -> dict:
    """
    Example endpoint that requires 'manager' OR 'admin' role.
    Users with either role can access this.

    **Authentication Required**: Bearer token with 'manager' or 'admin' role

    Returns:
    - Success message
    - User information
    """
    logger.info(f"Manager/Admin endpoint accessed by: {current_user.sub}")

    return {
        "message": "Welcome, manager or admin!",
        "user_id": current_user.sub,
        "roles": current_user.roles,
    }


@router.get("/with-permission")
async def permission_based_endpoint(
    current_user: Annotated[
        TokenData, Depends(require_permission("employees:read", "employees:write"))
    ],
) -> dict:
    """
    Example endpoint that requires specific permissions.
    Users must have 'employees:read' OR 'employees:write' permission.

    **Authentication Required**: Bearer token with required permissions

    Returns:
    - Success message
    - User information
    """
    logger.info(f"Permission-based endpoint accessed by: {current_user.sub}")

    return {
        "message": "You have the required permission!",
        "user_id": current_user.sub,
        "permissions": current_user.permissions,
    }
