import json
import logging

from api.core.logging import JSONFormatter, get_logger, setup_logging
from api.core.trace_context import trace_id_var


class TestJSONFormatter:
    def test_output_is_valid_json(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="hello", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["message"] == "hello"
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test"

    def test_includes_trace_id_from_context(self):
        formatter = JSONFormatter()
        token = trace_id_var.set("test-trace-123")
        try:
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="with trace", args=(), exc_info=None,
            )
            output = formatter.format(record)
            parsed = json.loads(output)
            assert parsed["trace_id"] == "test-trace-123"
        finally:
            trace_id_var.reset(token)

    def test_trace_id_empty_when_no_context(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="no trace", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["trace_id"] == ""

    def test_has_all_required_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="api.core.test", level=logging.WARNING, pathname="test.py",
            lineno=42, msg="check fields", args=(), exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_func"
        output = formatter.format(record)
        parsed = json.loads(output)
        assert set(parsed.keys()) == {
            "timestamp", "level", "logger", "message",
            "trace_id", "module", "func",
        }


class TestGetLogger:
    def test_returns_named_logger(self):
        log = get_logger("my.module")
        assert log.name == "my.module"


class TestSetupLogging:
    def teardown_method(self):
        root = logging.getLogger()
        root.handlers = [
            h for h in root.handlers
            if not isinstance(h.formatter, JSONFormatter)
        ]

    def test_root_logger_has_json_formatter(self):
        setup_logging()
        root = logging.getLogger()
        has_json = any(
            isinstance(h.formatter, JSONFormatter)
            for h in root.handlers
        )
        assert has_json

    def test_setup_logging_is_idempotent(self):
        setup_logging()
        root = logging.getLogger()
        count_before = sum(
            1 for h in root.handlers if isinstance(h.formatter, JSONFormatter)
        )
        setup_logging()
        count_after = sum(
            1 for h in root.handlers if isinstance(h.formatter, JSONFormatter)
        )
        assert count_before == count_after
