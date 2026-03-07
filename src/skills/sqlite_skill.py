"""SQLite skill – run simple SQL queries against local SQLite databases.

Covers the "Data & Analytics" and "Database" categories.
Uses Python stdlib ``sqlite3`` module only.

Supported actions
-----------------
execute         Run a SQL statement and return results.
create_table    Create a table with specified columns.
insert          Insert a row into a table.
select          Query rows from a table (with optional WHERE).
list_tables     List all tables in the database.
describe_table  Show the schema of a table.
drop_table      Drop (delete) a table.
count           Count rows in a table.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path


class SqliteSkill:
    """Run SQL queries against local SQLite databases."""

    name = "sqlite"
    description = (
        "SQLite database operations. "
        "Supported actions: 'execute' (sql, db_path); "
        "'create_table' (table, columns, db_path); "
        "'insert' (table, values, db_path); "
        "'select' (table, columns=*, where, db_path); "
        "'list_tables' (db_path); 'describe_table' (table, db_path); "
        "'drop_table' (table, db_path); 'count' (table, db_path)."
        "\ndb_path defaults to ':memory:' (temporary in-memory DB)."
    )

    def run(
        self,
        action: str,
        sql: str = "",
        db_path: str = ":memory:",
        table: str = "",
        columns: str = "",
        values: str = "",
        where: str = "",
    ) -> str:
        """
        Perform a SQLite operation.

        Parameters
        ----------
        action:
            The database operation (see description).
        sql:
            Raw SQL for ``"execute"``.
        db_path:
            Path to the SQLite database file (default ``":memory:"``).
        table:
            Table name for create/insert/select/describe/drop/count.
        columns:
            Column definitions for ``"create_table"``
            (e.g. ``"id INTEGER PRIMARY KEY, name TEXT, age INTEGER"``).
            For ``"select"``, columns to return (default ``"*"``).
        values:
            Comma-separated values for ``"insert"``
            (e.g. ``"1, 'Alice', 30"``).
        where:
            WHERE clause for ``"select"``
            (e.g. ``"age > 25"``; without the ``WHERE`` keyword).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "execute":
                return self._execute(db_path, sql)
            if action == "create_table":
                return self._create_table(db_path, table, columns)
            if action == "insert":
                return self._insert(db_path, table, values)
            if action == "select":
                return self._select(db_path, table, columns or "*", where)
            if action == "list_tables":
                return self._list_tables(db_path)
            if action == "describe_table":
                return self._describe_table(db_path, table)
            if action == "drop_table":
                return self._drop_table(db_path, table)
            if action == "count":
                return self._count(db_path, table)
        except sqlite3.Error as exc:
            return f"Error: {exc}"
        except Exception as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use execute, create_table, insert, select, list_tables, "
            "describe_table, drop_table, or count."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _connect(db_path: str) -> sqlite3.Connection:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _execute(self, db_path: str, sql: str) -> str:
        if not sql:
            return "Error: sql is required for execute"
        with self._connect(db_path) as conn:
            cur = conn.execute(sql)
            conn.commit()
            if cur.description:
                rows = cur.fetchall()
                headers = [d[0] for d in cur.description]
                return _format_table(headers, [list(r) for r in rows])
            return f"OK – {cur.rowcount} row(s) affected"

    def _create_table(self, db_path: str, table: str, columns: str) -> str:
        if not table:
            return "Error: table is required for create_table"
        if not columns:
            return "Error: columns is required for create_table"
        sql = f"CREATE TABLE IF NOT EXISTS {table} ({columns})"
        with self._connect(db_path) as conn:
            conn.execute(sql)
            conn.commit()
        return f"Table '{table}' created"

    def _insert(self, db_path: str, table: str, values: str) -> str:
        if not table:
            return "Error: table is required for insert"
        if not values:
            return "Error: values is required for insert"
        sql = f"INSERT INTO {table} VALUES ({values})"
        with self._connect(db_path) as conn:
            conn.execute(sql)
            conn.commit()
        return f"Inserted 1 row into '{table}'"

    def _select(self, db_path: str, table: str, cols: str, where: str) -> str:
        if not table:
            return "Error: table is required for select"
        sql = f"SELECT {cols} FROM {table}"
        if where:
            sql += f" WHERE {where}"
        with self._connect(db_path) as conn:
            cur = conn.execute(sql)
            rows = cur.fetchall()
            headers = [d[0] for d in cur.description] if cur.description else []
        return _format_table(headers, [list(r) for r in rows])

    def _list_tables(self, db_path: str) -> str:
        with self._connect(db_path) as conn:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cur.fetchall()]
        if not tables:
            return "(no tables)"
        return "Tables: " + ", ".join(tables)

    def _describe_table(self, db_path: str, table: str) -> str:
        if not table:
            return "Error: table is required for describe_table"
        with self._connect(db_path) as conn:
            cur = conn.execute(f"PRAGMA table_info({table})")
            rows = cur.fetchall()
        if not rows:
            return f"Error: table '{table}' not found or has no columns"
        lines = [f"Schema for '{table}':"]
        for row in rows:
            not_null = " NOT NULL" if row[3] else ""
            pk = " PRIMARY KEY" if row[5] else ""
            lines.append(f"  {row[1]} {row[2]}{not_null}{pk}")
        return "\n".join(lines)

    def _drop_table(self, db_path: str, table: str) -> str:
        if not table:
            return "Error: table is required for drop_table"
        with self._connect(db_path) as conn:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            conn.commit()
        return f"Table '{table}' dropped"

    def _count(self, db_path: str, table: str) -> str:
        if not table:
            return "Error: table is required for count"
        with self._connect(db_path) as conn:
            cur = conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
        return f"Row count in '{table}': {count}"


def _format_table(headers: list[str], rows: list[list]) -> str:
    if not rows:
        return "(no rows)"
    widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
              for i, h in enumerate(headers)]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    hrow = "|" + "|".join(f" {h:<{widths[i]}} " for i, h in enumerate(headers)) + "|"
    lines = [sep, hrow, sep]
    for row in rows:
        lines.append("|" + "|".join(f" {str(row[i]):<{widths[i]}} " for i in range(len(headers))) + "|")
    lines.append(sep)
    return "\n".join(lines)
