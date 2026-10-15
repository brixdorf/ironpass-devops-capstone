import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://ironpass:ironpass@localhost:5432/ironpass",
)
