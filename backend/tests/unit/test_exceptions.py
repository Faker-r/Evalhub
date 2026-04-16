"""Unit tests for custom exception classes."""

import pytest
from fastapi import status

from api.core.exceptions import (
    AlreadyExistsException,
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)


class TestNotFoundException:
    def test_default_message(self):
        exc = NotFoundException()
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Resource not found"

    def test_custom_message(self):
        exc = NotFoundException("Dataset not found")
        assert exc.detail == "Dataset not found"


class TestAlreadyExistsException:
    def test_default_message(self):
        exc = AlreadyExistsException()
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.detail == "Resource already exists"

    def test_custom_message(self):
        exc = AlreadyExistsException("Guideline already exists")
        assert exc.detail == "Guideline already exists"


class TestUnauthorizedException:
    def test_default_message(self):
        exc = UnauthorizedException()
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail == "Unauthorized access"

    def test_custom_message(self):
        exc = UnauthorizedException("Invalid token")
        assert exc.detail == "Invalid token"


class TestForbiddenException:
    def test_default_message(self):
        exc = ForbiddenException()
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.detail == "Access forbidden"

    def test_custom_message(self):
        exc = ForbiddenException("Not allowed")
        assert exc.detail == "Not allowed"


class TestBadRequestException:
    def test_default_message(self):
        exc = BadRequestException()
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == "Bad request"

    def test_custom_message(self):
        exc = BadRequestException("Invalid input")
        assert exc.detail == "Invalid input"
