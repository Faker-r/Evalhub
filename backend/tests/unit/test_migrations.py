"""Unit tests for utils/migrations.py."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from api.utils.migrations import run_migrations


class TestRunMigrations:
    @patch("api.utils.migrations.subprocess.run")
    def test_success_with_stdout(self, mock_run, capsys):
        mock_run.return_value = MagicMock(stdout="Applied migration 001", returncode=0)

        run_migrations()

        mock_run.assert_called_once()
        captured = capsys.readouterr()
        assert "Migration output:" in captured.out
        assert "Migrations completed successfully!" in captured.out

    @patch("api.utils.migrations.subprocess.run")
    def test_success_no_stdout(self, mock_run, capsys):
        mock_run.return_value = MagicMock(stdout="", returncode=0)

        run_migrations()

        captured = capsys.readouterr()
        assert "Migrations completed successfully!" in captured.out
        assert "Migration output:" not in captured.out

    @patch("api.utils.migrations.subprocess.run")
    def test_called_process_error(self, mock_run, capsys):
        err = subprocess.CalledProcessError(1, "alembic")
        err.stdout = "partial"
        err.stderr = "error detail"
        mock_run.side_effect = err

        with pytest.raises(subprocess.CalledProcessError):
            run_migrations()

        captured = capsys.readouterr()
        assert "Migration failed" in captured.out

    @patch("api.utils.migrations.subprocess.run")
    def test_general_exception(self, mock_run, capsys):
        mock_run.side_effect = OSError("Permission denied")

        with pytest.raises(OSError):
            run_migrations()

        captured = capsys.readouterr()
        assert "An error occurred" in captured.out
