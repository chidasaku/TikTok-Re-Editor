"""Lark Base API client for user management"""
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any
import streamlit as st


class LarkBaseClient:
    """Lark Base API client"""

    BASE_URL = "https://open.larksuite.com/open-apis"

    def __init__(self):
        """Initialize with credentials from Streamlit secrets"""
        self.app_id = st.secrets["lark"]["app_id"]
        self.app_secret = st.secrets["lark"]["app_secret"]
        self.base_app_token = st.secrets["lark"]["base_app_token"]
        self.table_id = st.secrets["lark"]["table_id"]
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def _get_tenant_access_token(self) -> str:
        """Get or refresh tenant access token"""
        now = datetime.now()
        if self._tenant_access_token and self._token_expires_at and now < self._token_expires_at:
            return self._tenant_access_token

        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        response = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Failed to get tenant access token: {data.get('msg')}")

        self._tenant_access_token = data["tenant_access_token"]
        # Token expires in 2 hours, refresh 5 minutes before
        from datetime import timedelta
        self._token_expires_at = now + timedelta(seconds=data["expire"] - 300)

        return self._tenant_access_token

    def _headers(self) -> Dict[str, str]:
        """Get headers with authorization"""
        return {
            "Authorization": f"Bearer {self._get_tenant_access_token()}",
            "Content-Type": "application/json"
        }

    def search_records(self, filter_condition: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search records in the table"""
        url = f"{self.BASE_URL}/bitable/v1/apps/{self.base_app_token}/tables/{self.table_id}/records/search"

        payload = {
            "page_size": 500
        }
        if filter_condition:
            payload["filter"] = filter_condition

        response = requests.post(url, headers=self._headers(), json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            error_code = data.get("code")
            error_msg = data.get("msg", "Unknown error")
            # 権限エラーや空テーブルの場合は空リストを返す
            if error_code in [1254040, 1254041, 1254043]:  # Common permission/not found errors
                return []
            raise Exception(f"Failed to search records (code={error_code}): {error_msg}")

        return data.get("data", {}).get("items", [])

    def get_record_by_field(self, field_name: str, field_value: str) -> Optional[Dict[str, Any]]:
        """Get a single record by field value using list API with filter"""
        # Use list API instead of search API (lower permission requirements)
        url = f"{self.BASE_URL}/bitable/v1/apps/{self.base_app_token}/tables/{self.table_id}/records"

        params = {
            "page_size": 500,
            "filter": f'CurrentValue.[{field_name}]="{field_value}"'
        }

        try:
            response = requests.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                # If filter not supported, fall back to get all and filter manually
                all_records = self.get_all_records()
                for record in all_records:
                    if record.get("fields", {}).get(field_name) == field_value:
                        return record
                return None

            items = data.get("data", {}).get("items", [])
            return items[0] if items else None
        except Exception:
            # Fall back to manual filtering
            try:
                all_records = self.get_all_records()
                for record in all_records:
                    if record.get("fields", {}).get(field_name) == field_value:
                        return record
            except Exception:
                pass
            return None

    def create_record(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        url = f"{self.BASE_URL}/bitable/v1/apps/{self.base_app_token}/tables/{self.table_id}/records"

        response = requests.post(url, headers=self._headers(), json={"fields": fields})
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Failed to create record: {data.get('msg')}")

        return data.get("data", {}).get("record", {})

    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing record"""
        url = f"{self.BASE_URL}/bitable/v1/apps/{self.base_app_token}/tables/{self.table_id}/records/{record_id}"

        response = requests.put(url, headers=self._headers(), json={"fields": fields})
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            raise Exception(f"Failed to update record: {data.get('msg')}")

        return data.get("data", {}).get("record", {})

    def delete_record(self, record_id: str) -> bool:
        """Delete a record"""
        url = f"{self.BASE_URL}/bitable/v1/apps/{self.base_app_token}/tables/{self.table_id}/records/{record_id}"

        response = requests.delete(url, headers=self._headers())
        response.raise_for_status()
        data = response.json()

        return data.get("code") == 0

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Get all records from the table"""
        url = f"{self.BASE_URL}/bitable/v1/apps/{self.base_app_token}/tables/{self.table_id}/records"

        all_records = []
        page_token = None

        try:
            while True:
                params = {"page_size": 500}
                if page_token:
                    params["page_token"] = page_token

                response = requests.get(url, headers=self._headers(), params=params)
                response.raise_for_status()
                data = response.json()

                if data.get("code") != 0:
                    error_code = data.get("code")
                    error_msg = data.get("msg", "Unknown error")
                    # Return empty list for permission or not found errors
                    if error_code in [1254040, 1254041, 1254043, 1254044]:
                        return []
                    raise Exception(f"Failed to get records (code={error_code}): {error_msg}")

                items = data.get("data", {}).get("items", [])
                all_records.extend(items)

                page_token = data.get("data", {}).get("page_token")
                if not page_token or not data.get("data", {}).get("has_more"):
                    break
        except requests.exceptions.RequestException as e:
            # Network error - return empty list
            return []

        return all_records
