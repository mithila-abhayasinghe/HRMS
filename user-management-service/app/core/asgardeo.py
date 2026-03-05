"""
Asgardeo SCIM API Client.
Handles all communication with Asgardeo identity provider for user management.
"""

import httpx
import json
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AsgardeoClient:
    """
    Client for Asgardeo SCIM API operations.
    Handles user creation, updates, and synchronization with Asgardeo.
    """

    def __init__(self):
        """Initialize Asgardeo client with configuration."""
        self.base_url = settings.ASGARDEO_DOMAIN
        self.scim_endpoint = f"{self.base_url}/scim2"
        self.oauth_endpoint = f"{self.base_url}/oauth2"
        self.bearer_token = settings.ASGARDEO_BEARER_TOKEN
        self.client_id = settings.ASGARDEO_CLIENT_ID
        self.client_secret = settings.ASGARDEO_CLIENT_SECRET
        self.timeout = settings.SERVICE_REQUEST_TIMEOUT

    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """
        Get HTTP headers for Asgardeo API calls.

        Args:
            include_auth: Whether to include Bearer token

        Returns:
            Dictionary of headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if include_auth:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        return headers

    async def create_user(
        self, email: str, password: str, first_name: str, last_name: str, phone: str
    ) -> Dict[str, Any]:
        """
        Create a new user in Asgardeo.

        Args:
            email: User email address
            password: User password
            first_name: First name
            last_name: Last name
            phone: Phone number

        Returns:
            User data including asgardeo_id

        Raises:
            Exception: If user creation fails
        """
        user_data = {
            "userName": email,
            "password": password,
            "name": {"givenName": first_name, "familyName": last_name},
            "emails": [{"value": email, "primary": True}],
            "phoneNumbers": [{"value": phone, "type": "mobile"}],
        }

        url = f"{self.scim_endpoint}/Users"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url, json=user_data, headers=self._get_headers()
                )

                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(f"User created in Asgardeo: {email}")
                    return {
                        "asgardeo_id": result.get("id"),
                        "email": email,
                        "status": "created",
                    }
                else:
                    error_msg = response.text
                    logger.error(f"Failed to create user in Asgardeo: {error_msg}")
                    raise Exception(f"Asgardeo user creation failed: {error_msg}")

        except httpx.TimeoutException:
            logger.error(f"Timeout creating user in Asgardeo: {email}")
            raise Exception("Asgardeo service timeout")
        except Exception as e:
            logger.error(f"Error creating user in Asgardeo: {str(e)}")
            raise

    async def get_user(self, asgardeo_id: str) -> Dict[str, Any]:
        """
        Get user information from Asgardeo.

        Args:
            asgardeo_id: Asgardeo user ID

        Returns:
            User data from Asgardeo

        Raises:
            Exception: If user not found or API error
        """
        url = f"{self.scim_endpoint}/Users/{asgardeo_id}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())

                if response.status_code == 200:
                    logger.info(f"Retrieved user from Asgardeo: {asgardeo_id}")
                    return response.json()
                else:
                    logger.error(f"Failed to get user from Asgardeo: {response.text}")
                    raise Exception(f"Failed to retrieve user: {response.text}")

        except Exception as e:
            logger.error(f"Error getting user from Asgardeo: {str(e)}")
            raise

    async def update_user(
        self, asgardeo_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user information in Asgardeo.

        Args:
            asgardeo_id: Asgardeo user ID
            updates: Fields to update

        Returns:
            Updated user data

        Raises:
            Exception: If update fails
        """
        url = f"{self.scim_endpoint}/Users/{asgardeo_id}"

        # SCIM PATCH format
        patch_data = {
            "Operations": [
                {"op": "Replace", "path": key, "value": value}
                for key, value in updates.items()
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    url, json=patch_data, headers=self._get_headers()
                )

                if response.status_code == 200:
                    logger.info(f"Updated user in Asgardeo: {asgardeo_id}")
                    return response.json()
                else:
                    logger.error(f"Failed to update user in Asgardeo: {response.text}")
                    raise Exception(f"Failed to update user: {response.text}")

        except Exception as e:
            logger.error(f"Error updating user in Asgardeo: {str(e)}")
            raise

    async def disable_user(self, asgardeo_id: str) -> bool:
        """
        Disable a user account in Asgardeo.

        Args:
            asgardeo_id: Asgardeo user ID

        Returns:
            True if successful

        Raises:
            Exception: If disable fails
        """
        url = f"{self.scim_endpoint}/Users/{asgardeo_id}"

        patch_data = {
            "Operations": [{"op": "Replace", "path": "active", "value": False}]
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    url, json=patch_data, headers=self._get_headers()
                )

                if response.status_code == 200:
                    logger.info(f"Disabled user in Asgardeo: {asgardeo_id}")
                    return True
                else:
                    logger.error(f"Failed to disable user in Asgardeo: {response.text}")
                    raise Exception(f"Failed to disable user: {response.text}")

        except Exception as e:
            logger.error(f"Error disabling user in Asgardeo: {str(e)}")
            raise

    async def enable_user(self, asgardeo_id: str) -> bool:
        """
        Enable a user account in Asgardeo.

        Args:
            asgardeo_id: Asgardeo user ID

        Returns:
            True if successful

        Raises:
            Exception: If enable fails
        """
        url = f"{self.scim_endpoint}/Users/{asgardeo_id}"

        patch_data = {
            "Operations": [{"op": "Replace", "path": "active", "value": True}]
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.patch(
                    url, json=patch_data, headers=self._get_headers()
                )

                if response.status_code == 200:
                    logger.info(f"Enabled user in Asgardeo: {asgardeo_id}")
                    return True
                else:
                    logger.error(f"Failed to enable user in Asgardeo: {response.text}")
                    raise Exception(f"Failed to enable user: {response.text}")

        except Exception as e:
            logger.error(f"Error enabling user in Asgardeo: {str(e)}")
            raise

    async def list_users(
        self, filter_str: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        List users from Asgardeo with optional filtering.

        Args:
            filter_str: SCIM filter string

        Returns:
            List of users

        Raises:
            Exception: If list operation fails
        """
        url = f"{self.scim_endpoint}/Users"

        if filter_str:
            url += f"?filter={filter_str}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())

                if response.status_code == 200:
                    result = response.json()
                    users = result.get("Resources", [])
                    logger.info(f"Retrieved {len(users)} users from Asgardeo")
                    return users
                else:
                    logger.error(f"Failed to list users from Asgardeo: {response.text}")
                    raise Exception(f"Failed to list users: {response.text}")

        except Exception as e:
            logger.error(f"Error listing users from Asgardeo: {str(e)}")
            raise

    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens (OAuth 2.0).

        Args:
            code: Authorization code from redirect
            state: State parameter for CSRF protection

        Returns:
            Token response with access_token, id_token, etc.

        Raises:
            Exception: If token exchange fails
        """
        url = f"{self.oauth_endpoint}/token"

        data = {
            "code": code,
            "state": state,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": settings.ASGARDEO_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code == 200:
                    tokens = response.json()
                    logger.info("Successfully exchanged code for tokens")
                    return tokens
                else:
                    logger.error(f"Failed to exchange code: {response.text}")
                    raise Exception(f"Token exchange failed: {response.text}")

        except Exception as e:
            logger.error(f"Error exchanging code for token: {str(e)}")
            raise

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate token with Asgardeo (introspection endpoint).

        Args:
            token: JWT or access token

        Returns:
            Token validation response

        Raises:
            Exception: If validation fails
        """
        url = f"{self.oauth_endpoint}/introspect"

        data = {
            "token": token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info("Token validation successful")
                    return result
                else:
                    logger.error(f"Token validation failed: {response.text}")
                    raise Exception(f"Token validation failed: {response.text}")

        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            raise


# Create a singleton instance of the Asgardeo client
asgardeo_client = AsgardeoClient()
