#!/usr/bin/env python3
"""Query System

Version: 0.3.5d (package 3.9a, stage 6/6)

Structured query builder for data retrieval.

Package 3.9a Stage 6: Query system for backend data access.

Features:
- Query builder pattern
- SQL-like syntax
- Result caching
- Pagination
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class Query:
    """Structured query"""
    select_fields: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    order_by: Optional[str] = None
    order_desc: bool = False
    limit: Optional[int] = None
    offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'select': self.select_fields,
            'filter': self.filters,
            'order_by': self.order_by,
            'order_desc': self.order_desc,
            'limit': self.limit,
            'offset': self.offset,
        }


class QueryBuilder:
    """Query builder with fluent interface
    
    Usage:
        query = QueryBuilder() \
            .select(['fps', 'cpu', 'gpu']) \
            .filter({'timestamp': '>1h'}) \
            .order_by('timestamp', desc=True) \
            .limit(100)
        
        result = backend.query_data('metrics', query.build())
    """
    
    def __init__(self):
        """Initialize query builder"""
        self._query = Query()
    
    def select(self, fields: List[str]) -> 'QueryBuilder':
        """Select fields
        
        Args:
            fields: List of field names
        
        Returns:
            Self for chaining
        """
        self._query.select_fields = fields
        return self
    
    def filter(self, conditions: Dict[str, Any]) -> 'QueryBuilder':
        """Add filter conditions
        
        Args:
            conditions: Filter conditions
        
        Returns:
            Self for chaining
        """
        self._query.filters.update(conditions)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'QueryBuilder':
        """Set order
        
        Args:
            field: Field to order by
            desc: Descending order
        
        Returns:
            Self for chaining
        """
        self._query.order_by = field
        self._query.order_desc = desc
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """Set result limit
        
        Args:
            count: Maximum results
        
        Returns:
            Self for chaining
        """
        self._query.limit = count
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        """Set result offset (pagination)
        
        Args:
            offset: Offset count
        
        Returns:
            Self for chaining
        """
        self._query.offset = offset
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build query dictionary
        
        Returns:
            Query parameters
        """
        return self._query.to_dict()
    
    def get_query(self) -> Query:
        """Get query object
        
        Returns:
            Query object
        """
        return self._query
