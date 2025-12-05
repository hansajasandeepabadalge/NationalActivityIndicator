#!/bin/sh
pip install -q alembic psycopg2-binary sqlalchemy pydantic pydantic-settings
alembic upgrade head
