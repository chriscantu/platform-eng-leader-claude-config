"""
Unit tests for database management
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest
from claudedirector.core.database import DatabaseManager
from claudedirector.core.exceptions import DatabaseError


class TestDatabaseManager:
    """Test database management functionality"""

    def test_singleton_pattern(self, temp_db):
        """Test that DatabaseManager follows singleton pattern"""
        # Reset singleton for clean test
        DatabaseManager._instance = None

        db1 = DatabaseManager(temp_db)
        db2 = DatabaseManager(temp_db)

        assert db1 is db2
        assert DatabaseManager._instance is db1

    def test_connection_creation(self, temp_db):
        """Test that database connections are created correctly"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        with db_manager.get_connection() as conn:
            assert isinstance(conn, sqlite3.Connection)
            # Test basic query
            cursor = conn.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1

    def test_connection_context_manager(self, temp_db):
        """Test database connection context manager"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        with db_manager.get_connection() as conn:
            conn.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
            conn.commit()

        # Verify data was inserted
        with db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM test_table WHERE name = ?", ("test",))
            result = cursor.fetchone()
            assert result[0] == "test"

    def test_execute_query(self, temp_db):
        """Test query execution helper method"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        # Insert test data
        db_manager.execute_query("INSERT INTO test_table (name) VALUES (?)", ("query_test",))

        # Query test data
        result = db_manager.execute_query(
            "SELECT name FROM test_table WHERE name = ?", ("query_test",), fetch_one=True
        )

        assert result[0] == "query_test"

    def test_execute_query_fetchall(self, temp_db):
        """Test query execution with fetchall"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        # Insert multiple records
        test_names = ["test1", "test2", "test3"]
        for name in test_names:
            db_manager.execute_query("INSERT INTO test_table (name) VALUES (?)", (name,))

        # Query all records
        results = db_manager.execute_query(
            "SELECT name FROM test_table ORDER BY name", fetch_all=True
        )

        assert len(results) == 3
        assert [row[0] for row in results] == test_names

    def test_get_tables(self, temp_db):
        """Test getting list of database tables"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        tables = db_manager.get_tables()
        assert "test_table" in tables

    def test_table_exists(self, temp_db):
        """Test checking if table exists"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        assert db_manager.table_exists("test_table") is True
        assert db_manager.table_exists("nonexistent_table") is False

    def test_invalid_database_path(self):
        """Test handling of invalid database path"""
        DatabaseManager._instance = None

        with pytest.raises(DatabaseError):
            # Try to create database in non-existent directory
            DatabaseManager("/nonexistent/path/db.sqlite")

    def test_database_error_handling(self, temp_db):
        """Test database error handling"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        with pytest.raises(DatabaseError):
            # Try to execute invalid SQL
            db_manager.execute_query("INVALID SQL STATEMENT")

    def test_connection_cleanup(self, temp_db):
        """Test that connections are properly cleaned up"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        # Create and use connection
        with db_manager.get_connection() as conn:
            conn.execute("SELECT 1")

        # Connection should be closed after context exit
        # Note: sqlite3 connections don't have a reliable "is_closed" check,
        # but we can test that we can create new connections
        with db_manager.get_connection() as conn2:
            result = conn2.execute("SELECT 1").fetchone()
            assert result[0] == 1

    def test_concurrent_access(self, temp_db):
        """Test concurrent database access (thread safety simulation)"""
        DatabaseManager._instance = None
        db_manager = DatabaseManager(temp_db)

        # Simulate concurrent writes
        for i in range(10):
            db_manager.execute_query(
                "INSERT INTO test_table (name) VALUES (?)", (f"concurrent_test_{i}",)
            )

        # Verify all writes succeeded
        results = db_manager.execute_query(
            "SELECT COUNT(*) FROM test_table WHERE name LIKE 'concurrent_test_%'", fetch_one=True
        )
        assert results[0] == 10
