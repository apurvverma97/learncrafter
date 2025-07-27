"""
Data Access Object for Supabase.

This module encapsulates all the database interaction logic for Supabase.
"""

import logging
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseDAO:
    """Handles all database operations with Supabase."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)

    def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record."""
        try:
            response = self.client.table(table_name).insert(data).execute()
            if not response.data:
                raise Exception(f"Failed to insert record into {table_name}")
            return response.data[0]
        except Exception as e:
            logger.error(f"Failed to insert record into {table_name}: {e}")
            raise

    def get(self, table_name: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a specific record by a given filter."""
        try:
            query = self.client.table(table_name).select("*")
            for key, value in filters.items():
                query = query.eq(key, value)
            response = query.execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get record from {table_name} with filters {filters}: {e}")
            raise

    def update(self, table_name: str, filters: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Update an existing record."""
        try:
            query = self.client.table(table_name).update(data)
            for key, value in filters.items():
                query = query.eq(key, value)
            query.execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update record in {table_name} with filters {filters}: {e}")
            return False

    def delete(self, table_name: str, filters: Dict[str, Any]) -> bool:
        """Delete a record."""
        try:
            query = self.client.table(table_name).delete()
            for key, value in filters.items():
                query = query.eq(key, value)
            query.execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete record from {table_name} with filters {filters}: {e}")
            return False

    def list_query(
        self,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List records with optional filtering and ordering."""
        try:
            query = self.client.table(table_name).select("*")
            if filters:
                for key, value in filters.items():
                    if isinstance(value, str) and "%" in value:
                        query = query.ilike(key, value)
                    else:
                        query = query.eq(key, value)
            if order_by:
                query = query.order(order_by)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to list records from {table_name}: {e}")
            return []

    def count_query(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering."""
        try:
            query = self.client.table(table_name).select("*", count="exact")
            if filters:
                for key, value in filters.items():
                    if isinstance(value, str) and "%" in value:
                        query = query.ilike(key, value)
                    else:
                        query = query.eq(key, value)
            response = query.execute()
            return response.count
        except Exception as e:
            logger.error(f"Failed to count records from {table_name}: {e}")
            return 0
