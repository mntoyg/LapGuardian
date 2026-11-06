"""Persistence layer: a single local SQLite database.

The database lives in the platform application-data directory and never leaves
the machine. ``schema.sql`` holds the DDL; :mod:`lapguardian.storage.db` applies
it and handles migration.
"""
