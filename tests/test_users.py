"""Tests for user endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import user as user_crud
from app.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    """Test user creation endpoint.

    Args:
        client: Test HTTP client
    """
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
    }

    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test user creation with duplicate email fails.

    Args:
        client: Test HTTP client
        db_session: Database session
    """
    # Create first user
    user_in = UserCreate(
        email="duplicate@example.com",
        username="user1",
        password="password123",
    )
    await user_crud.create(db_session, obj_in=user_in)

    # Try to create second user with same email
    user_data = {
        "email": "duplicate@example.com",
        "username": "user2",
        "password": "password123",
    }

    response = await client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test get user endpoint.

    Args:
        client: Test HTTP client
        db_session: Database session
    """
    # Create user
    user_in = UserCreate(
        email="getuser@example.com",
        username="getuser",
        password="password123",
    )
    user = await user_crud.create(db_session, obj_in=user_in)

    # Get user
    response = await client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user.id
    assert data["email"] == user.email
    assert data["username"] == user.username


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient) -> None:
    """Test get user with non-existent ID.

    Args:
        client: Test HTTP client
    """
    response = await client.get("/api/v1/users/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test list users endpoint.

    Args:
        client: Test HTTP client
        db_session: Database session
    """
    # Create multiple users
    for i in range(3):
        user_in = UserCreate(
            email=f"user{i}@example.com",
            username=f"user{i}",
            password="password123",
        )
        await user_crud.create(db_session, obj_in=user_in)

    # List users
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test update user endpoint.

    Args:
        client: Test HTTP client
        db_session: Database session
    """
    # Create user
    user_in = UserCreate(
        email="update@example.com",
        username="updateuser",
        password="password123",
    )
    user = await user_crud.create(db_session, obj_in=user_in)

    # Update user
    update_data = {
        "full_name": "Updated Name",
    }
    response = await client.patch(f"/api/v1/users/{user.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == user.email


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test delete user endpoint.

    Args:
        client: Test HTTP client
        db_session: Database session
    """
    # Create user
    user_in = UserCreate(
        email="delete@example.com",
        username="deleteuser",
        password="password123",
    )
    user = await user_crud.create(db_session, obj_in=user_in)

    # Delete user
    response = await client.delete(f"/api/v1/users/{user.id}")
    assert response.status_code == 204

    # Verify user is deleted
    get_response = await client.get(f"/api/v1/users/{user.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Test health check endpoint.

    Args:
        client: Test HTTP client
    """
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "version" in data
