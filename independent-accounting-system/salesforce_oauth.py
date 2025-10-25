#!/usr/bin/env python3
"""
Salesforce OAuth2 Integration Service
Secure authentication using Client Credentials Flow (no password storage)
"""
import os
import requests
import time
from typing import Optional, Dict
from datetime import datetime, timedelta
import json


class SalesforceOAuth2Service:
    """
    Salesforce OAuth2 Client Credentials Flow

    Benefits:
    - No password storage required
    - Automatic token refresh
    - Granular permission control
    - Token expiration management
    - Audit trail
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        instance_url: Optional[str] = None,
        token_url: Optional[str] = None
    ):
        """
        Initialize Salesforce OAuth2 service

        Args:
            client_id: OAuth2 Client ID from Connected App
            client_secret: OAuth2 Client Secret from Connected App
            instance_url: Salesforce instance URL (e.g., https://your-company.salesforce.com)
            token_url: OAuth2 token endpoint (default: https://login.salesforce.com/services/oauth2/token)
        """
        self.client_id = client_id or os.getenv('SALESFORCE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SALESFORCE_CLIENT_SECRET')
        self.instance_url = instance_url or os.getenv('SALESFORCE_INSTANCE_URL')
        self.token_url = token_url or os.getenv(
            'SALESFORCE_TOKEN_URL',
            'https://login.salesforce.com/services/oauth2/token'
        )

        # Token cache
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._token_type: Optional[str] = None

    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get valid access token (from cache or refresh)

        Args:
            force_refresh: Force token refresh even if cached token is valid

        Returns:
            Valid access token

        Raises:
            ValueError: If credentials are not configured
            requests.HTTPError: If OAuth2 request fails
        """
        # Return cached token if valid
        if not force_refresh and self._is_token_valid():
            return self._access_token

        # Request new token
        return self._request_new_token()

    def _is_token_valid(self) -> bool:
        """Check if cached token is still valid"""
        if not self._access_token or not self._token_expiry:
            return False

        # Add 60 second buffer for token expiry
        return datetime.now() < (self._token_expiry - timedelta(seconds=60))

    def _request_new_token(self) -> str:
        """
        Request new access token using Client Credentials Flow

        Returns:
            New access token

        Raises:
            ValueError: If credentials are missing
            requests.HTTPError: If request fails
        """
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Salesforce OAuth2 credentials not configured. "
                "Set SALESFORCE_CLIENT_ID and SALESFORCE_CLIENT_SECRET environment variables."
            )

        # OAuth2 Client Credentials request
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        print(f"[OAuth2] Requesting new access token from {self.token_url}")

        try:
            response = requests.post(
                self.token_url,
                data=payload,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] OAuth2 token request failed: {e}")
            raise

        # Parse token response
        token_data = response.json()

        self._access_token = token_data.get('access_token')
        self._token_type = token_data.get('token_type', 'Bearer')

        # Calculate token expiry (default 2 hours if not provided)
        expires_in = token_data.get('expires_in', 7200)
        self._token_expiry = datetime.now() + timedelta(seconds=expires_in)

        print(f"[OAuth2] Token acquired successfully (expires in {expires_in}s)")

        # Update instance URL if provided in response
        if 'instance_url' in token_data:
            self.instance_url = token_data['instance_url']

        return self._access_token

    def get_authorization_header(self) -> Dict[str, str]:
        """
        Get authorization header for API requests

        Returns:
            Dict with Authorization header
        """
        token = self.get_access_token()
        return {
            'Authorization': f'{self._token_type} {token}',
            'Content-Type': 'application/json'
        }

    def make_api_request(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make authenticated Salesforce API request

        Args:
            endpoint: API endpoint (e.g., '/services/data/v58.0/sobjects/Opportunity')
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request body (for POST/PUT)
            params: Query parameters

        Returns:
            Response object
        """
        if not self.instance_url:
            raise ValueError("Salesforce instance URL not configured")

        url = f"{self.instance_url}{endpoint}"
        headers = self.get_authorization_header()

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params,
            timeout=30
        )

        # Handle token expiration (401 Unauthorized)
        if response.status_code == 401:
            print("[OAuth2] Token expired, refreshing...")
            # Refresh token and retry
            self.get_access_token(force_refresh=True)
            headers = self.get_authorization_header()

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )

        response.raise_for_status()
        return response

    def query(self, soql: str) -> Dict:
        """
        Execute SOQL query

        Args:
            soql: SOQL query string

        Returns:
            Query results
        """
        endpoint = '/services/data/v58.0/query'
        response = self.make_api_request(
            endpoint=endpoint,
            params={'q': soql}
        )
        return response.json()

    def get_opportunities(self, limit: int = 100) -> list:
        """
        Get Opportunity records for revenue tracking

        Args:
            limit: Maximum number of records to fetch

        Returns:
            List of Opportunity records
        """
        soql = f"""
            SELECT Id, Name, Amount, CloseDate, StageName, AccountId, OwnerId
            FROM Opportunity
            WHERE IsWon = true
            ORDER BY CloseDate DESC
            LIMIT {limit}
        """

        result = self.query(soql)
        return result.get('records', [])

    def test_connection(self) -> bool:
        """
        Test Salesforce OAuth2 connection

        Returns:
            True if connection is successful
        """
        try:
            # Test with a simple query
            result = self.query("SELECT Id FROM User LIMIT 1")
            print(f"[SUCCESS] Salesforce OAuth2 connection test passed")
            print(f"  - Instance: {self.instance_url}")
            print(f"  - Token valid until: {self._token_expiry}")
            return True
        except Exception as e:
            print(f"[ERROR] Salesforce OAuth2 connection test failed: {e}")
            return False


class OdooAPIKeyService:
    """
    Odoo API Key Authentication (Odoo 13+)

    Benefits:
    - No password storage
    - User-specific API keys
    - Easy revocation
    - Separate permissions
    """

    def __init__(
        self,
        url: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Odoo API Key service

        Args:
            url: Odoo server URL
            database: Odoo database name
            username: Odoo username
            api_key: Odoo API key (generate in user preferences)
        """
        self.url = url or os.getenv('ODOO_URL')
        self.database = database or os.getenv('ODOO_DB')
        self.username = username or os.getenv('ODOO_USERNAME')
        self.api_key = api_key or os.getenv('ODOO_API_KEY')

        self._uid: Optional[int] = None

    def authenticate(self) -> int:
        """
        Authenticate with Odoo using API Key

        Returns:
            User ID

        Raises:
            ValueError: If credentials are missing
            Exception: If authentication fails
        """
        if not all([self.url, self.database, self.username, self.api_key]):
            raise ValueError(
                "Odoo credentials not configured. "
                "Set ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY environment variables."
            )

        import xmlrpc.client

        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')

        try:
            # Authenticate with API key
            self._uid = common.authenticate(
                self.database,
                self.username,
                self.api_key,
                {}
            )

            if not self._uid:
                raise Exception("Authentication failed - invalid API key")

            print(f"[SUCCESS] Odoo API Key authentication successful (UID: {self._uid})")
            return self._uid
        except Exception as e:
            print(f"[ERROR] Odoo authentication failed: {e}")
            raise

    def get_uid(self) -> int:
        """Get authenticated user ID (authenticate if needed)"""
        if not self._uid:
            self.authenticate()
        return self._uid

    def execute(self, model: str, method: str, *args, **kwargs):
        """
        Execute Odoo method

        Args:
            model: Odoo model name (e.g., 'account.move')
            method: Method name (e.g., 'search_read')
            *args: Method arguments
            **kwargs: Method keyword arguments

        Returns:
            Method result
        """
        import xmlrpc.client

        uid = self.get_uid()
        models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

        return models.execute_kw(
            self.database,
            uid,
            self.api_key,
            model,
            method,
            args,
            kwargs
        )

    def get_expenses(self, limit: int = 100) -> list:
        """
        Get expense records for cost tracking

        Args:
            limit: Maximum number of records

        Returns:
            List of expense records
        """
        return self.execute(
            'account.move',
            'search_read',
            [[('move_type', '=', 'in_invoice'), ('state', '=', 'posted')]],
            {'fields': ['name', 'date', 'amount_total', 'partner_id'], 'limit': limit}
        )

    def test_connection(self) -> bool:
        """
        Test Odoo API Key connection

        Returns:
            True if connection is successful
        """
        try:
            self.authenticate()
            # Test with a simple query
            result = self.execute('res.users', 'search_read', [[('id', '=', self._uid)]], {'limit': 1})
            print(f"[SUCCESS] Odoo API Key connection test passed")
            print(f"  - URL: {self.url}")
            print(f"  - Database: {self.database}")
            print(f"  - User: {result[0].get('name') if result else 'Unknown'}")
            return True
        except Exception as e:
            print(f"[ERROR] Odoo API Key connection test failed: {e}")
            return False


def demo_oauth2_services():
    """Demo OAuth2 services with test credentials"""
    print("=" * 60)
    print("NERDX OAuth2 Services Demo")
    print("=" * 60)

    # Salesforce OAuth2
    print("\n[1] Salesforce OAuth2 Service")
    print("-" * 60)

    salesforce = SalesforceOAuth2Service()

    if salesforce.client_id and salesforce.client_secret:
        print("[INFO] Testing Salesforce OAuth2 connection...")
        if salesforce.test_connection():
            # Fetch opportunities
            opportunities = salesforce.get_opportunities(limit=5)
            print(f"[OK] Fetched {len(opportunities)} opportunities")
            for opp in opportunities[:3]:
                print(f"  - {opp.get('Name')}: ${opp.get('Amount', 0):,.2f}")
    else:
        print("[SKIP] Salesforce OAuth2 credentials not configured")
        print("  Set SALESFORCE_CLIENT_ID and SALESFORCE_CLIENT_SECRET")

    # Odoo API Key
    print("\n[2] Odoo API Key Service")
    print("-" * 60)

    odoo = OdooAPIKeyService()

    if odoo.url and odoo.api_key:
        print("[INFO] Testing Odoo API Key connection...")
        if odoo.test_connection():
            # Fetch expenses
            expenses = odoo.get_expenses(limit=5)
            print(f"[OK] Fetched {len(expenses)} expense records")
            for exp in expenses[:3]:
                print(f"  - {exp.get('name')}: ${exp.get('amount_total', 0):,.2f}")
    else:
        print("[SKIP] Odoo API Key credentials not configured")
        print("  Set ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY")

    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)


if __name__ == "__main__":
    demo_oauth2_services()
