"""
Performance regression tests for ClaudeDirector
"""

import tempfile
import time
from pathlib import Path

import pytest
from claudedirector.core.config import ClaudeDirectorConfig
from claudedirector.core.database import DatabaseManager


class TestPerformanceRegression:
    """Test performance benchmarks and regression detection"""

    def test_database_connection_performance(self):
        """Test database connection creation performance"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            # Reset singleton
            DatabaseManager._instance = None

            # Measure connection creation time
            start_time = time.time()
            db_manager = DatabaseManager(db_path)
            connection_time = time.time() - start_time

            # Should be very fast (under 50ms)
            assert (
                connection_time < 0.05
            ), f"Database connection took {connection_time:.4f}s, expected < 0.05s"

            # Measure multiple connection requests (should use singleton)
            start_time = time.time()
            for _ in range(10):
                same_manager = DatabaseManager(db_path)
                assert same_manager is db_manager  # Should be same instance
            multiple_connection_time = time.time() - start_time

            # Multiple requests should be even faster due to singleton pattern
            assert (
                multiple_connection_time < 0.01
            ), f"Multiple connections took {multiple_connection_time:.4f}s, expected < 0.01s"

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_config_creation_performance(self):
        """Test configuration creation performance"""
        # Measure config creation time
        start_time = time.time()
        config = ClaudeDirectorConfig()
        config_time = time.time() - start_time

        # Should be very fast (under 10ms)
        assert config_time < 0.01, f"Config creation took {config_time:.4f}s, expected < 0.01s"

        # Measure multiple config creations
        start_time = time.time()
        configs = []
        for _ in range(100):
            configs.append(ClaudeDirectorConfig(enable_caching=False))
        multiple_config_time = time.time() - start_time

        # Should scale linearly and be reasonable (under 100ms for 100 configs)
        assert (
            multiple_config_time < 0.1
        ), f"100 config creations took {multiple_config_time:.4f}s, expected < 0.1s"

        # Verify all configs are valid
        assert all(not c.enable_caching for c in configs)

    def test_database_query_performance(self):
        """Test database query performance"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            DatabaseManager._instance = None
            db_manager = DatabaseManager(db_path)

            # Create test table
            db_manager.execute_query(
                """
                CREATE TABLE performance_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Measure insert performance
            start_time = time.time()
            for i in range(1000):
                db_manager.execute_query(
                    "INSERT INTO performance_test (data) VALUES (?)", (f"test_data_{i}",)
                )
            insert_time = time.time() - start_time

            # Should complete 1000 inserts in reasonable time (under 1 second)
            assert insert_time < 1.0, f"1000 inserts took {insert_time:.4f}s, expected < 1.0s"

            # Measure query performance
            start_time = time.time()
            for i in range(100):
                result = db_manager.execute_query(
                    "SELECT data FROM performance_test WHERE data = ?",
                    (f"test_data_{i}",),
                    fetch_one=True,
                )
                assert result[0] == f"test_data_{i}"
            query_time = time.time() - start_time

            # Should complete 100 queries quickly (under 100ms)
            assert query_time < 0.1, f"100 queries took {query_time:.4f}s, expected < 0.1s"

            # Measure bulk query performance
            start_time = time.time()
            all_results = db_manager.execute_query(
                "SELECT COUNT(*) FROM performance_test", fetch_one=True
            )
            bulk_query_time = time.time() - start_time

            assert all_results[0] == 1000
            assert (
                bulk_query_time < 0.01
            ), f"Bulk query took {bulk_query_time:.4f}s, expected < 0.01s"

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_workspace_scanning_performance(self):
        """Test workspace scanning performance with various file counts"""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_path = Path(temp_dir)

            # Create test workspace structure
            meeting_prep = workspace_path / "meeting-prep"
            meeting_prep.mkdir()

            # Create varying numbers of files to test scaling
            file_counts = [10, 50, 100]

            for file_count in file_counts:
                # Clear directory
                for f in meeting_prep.glob("*.md"):
                    f.unlink()

                # Create test files
                for i in range(file_count):
                    test_file = meeting_prep / f"meeting_{i:03d}.md"
                    test_file.write_text(
                        f"""
# Meeting {i}
Date: 2024-01-{i:02d}
Attendees: Person A, Person B

## Agenda
- Topic 1
- Topic 2

## Action Items
- [ ] Task 1
- [ ] Task 2
"""
                    )

                # Measure scanning time
                start_time = time.time()

                # Simulate workspace scanning (just file discovery for now)
                found_files = list(meeting_prep.glob("*.md"))

                scan_time = time.time() - start_time

                assert len(found_files) == file_count

                # Performance should scale reasonably (under 10ms per 100 files)
                expected_max_time = file_count * 0.0001  # 0.1ms per file
                assert (
                    scan_time < expected_max_time
                ), f"Scanning {file_count} files took {scan_time:.4f}s, expected < {expected_max_time:.4f}s"

    def test_memory_usage_stability(self):
        """Test memory usage remains stable during operations"""
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available for memory testing")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            DatabaseManager._instance = None

            # Perform memory-intensive operations
            for iteration in range(10):
                # Create database manager
                db_manager = DatabaseManager(db_path)

                # Create and populate table
                table_name = f"memory_test_{iteration}"
                db_manager.execute_query(
                    f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id INTEGER PRIMARY KEY,
                        data TEXT
                    )
                """
                )

                # Insert data
                for i in range(100):
                    db_manager.execute_query(
                        f"INSERT INTO {table_name} (data) VALUES (?)", (f"data_{iteration}_{i}",)
                    )

                # Query data
                results = db_manager.execute_query(
                    f"SELECT COUNT(*) FROM {table_name}", fetch_one=True
                )
                assert results[0] == 100

                # Check memory usage
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory

                # Memory should not grow excessively (under 50MB increase)
                assert (
                    memory_increase < 50
                ), f"Memory increased by {memory_increase:.2f}MB after {iteration + 1} iterations"

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()

    def test_import_performance(self):
        """Test module import performance"""
        import importlib
        import sys

        # Test core module imports
        modules_to_test = [
            "claudedirector.core.config",
            "claudedirector.core.database",
            "claudedirector.core.exceptions",
        ]

        for module_name in modules_to_test:
            # Remove from cache if already imported
            if module_name in sys.modules:
                del sys.modules[module_name]

            # Measure import time
            start_time = time.time()
            importlib.import_module(module_name)
            import_time = time.time() - start_time

            # Imports should be fast (under 100ms each)
            assert (
                import_time < 0.1
            ), f"Import of {module_name} took {import_time:.4f}s, expected < 0.1s"

    @pytest.mark.slow
    def test_sustained_operation_performance(self):
        """Test performance during sustained operations"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            DatabaseManager._instance = None
            db_manager = DatabaseManager(db_path)

            # Create test table
            db_manager.execute_query(
                """
                CREATE TABLE sustained_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_num INTEGER,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Perform sustained operations and measure performance degradation
            operation_times = []

            for batch in range(10):  # 10 batches
                start_time = time.time()

                # Perform batch operations
                for i in range(100):  # 100 operations per batch
                    operation_num = batch * 100 + i
                    db_manager.execute_query(
                        "INSERT INTO sustained_test (operation_num) VALUES (?)", (operation_num,)
                    )

                batch_time = time.time() - start_time
                operation_times.append(batch_time)

            # Check that performance doesn't degrade significantly over time
            first_batch_time = operation_times[0]
            last_batch_time = operation_times[-1]

            # Last batch should not be more than 50% slower than first batch
            performance_degradation = (last_batch_time - first_batch_time) / first_batch_time
            assert (
                performance_degradation < 0.5
            ), f"Performance degraded by {performance_degradation:.2%}, expected < 50%"

            # Verify all operations completed
            total_count = db_manager.execute_query(
                "SELECT COUNT(*) FROM sustained_test", fetch_one=True
            )
            assert total_count[0] == 1000

        finally:
            if Path(db_path).exists():
                Path(db_path).unlink()
