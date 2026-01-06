"""User models.

Note: User authentication is handled by Supabase Auth.
This file is kept for potential future use (e.g., user profiles table).
"""

# If you need to store additional user data beyond what Supabase Auth provides,
# you can create a profiles table that references the Supabase user UUID:
#
# from sqlalchemy import Column, String
# from api.core.database import Base
#
# class Profile(Base):
#     """User profile model - extends Supabase Auth user."""
#     __tablename__ = "profiles"
#
#     id = Column(String, primary_key=True)  # Supabase user UUID
#     display_name = Column(String, nullable=True)
#     avatar_url = Column(String, nullable=True)
