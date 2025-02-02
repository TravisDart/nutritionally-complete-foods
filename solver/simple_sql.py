from itertools import combinations
from typing import List, Optional

import psycopg

from solver.logger import Logger, NullLogger


class SimpleSQLStore:
    def __init__(
        self, db_url: str, num_foods: int, timeout: int = 3600, logger: Logger = None
    ):
        self.logger = NullLogger if logger is None else logger
        self.conn = psycopg.connect(db_url)
        self.conn.autocommit = True
        self.conn.isolation_level = psycopg.IsolationLevel.SERIALIZABLE

    def initialize(self):
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS solutions (
                    id smallint[] PRIMARY KEY
                );
            """
            )
        except psycopg.errors.UniqueViolation:
            pass

        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS work (
                    worker_id INT PRIMARY KEY,
                    work_value INT
                );
                """
            )
        except psycopg.errors.UniqueViolation:
            pass

    def add_solution(self, solution):
        """Insert the new solution"""
        self.logger.log("Adding solution", solution, end=" ")
        cursor = self.conn.cursor()
        solution = list(solution)

        cursor.execute(
            """SELECT id FROM solutions WHERE id = %s;""",
            (solution,),
        )
        if cursor.fetchone() is not None:
            self.logger.log("Solution already exists")
            return

        cursor.execute(
            """INSERT INTO solutions (id) VALUES (%s) ON CONFLICT DO NOTHING;""",
            (solution,),
        )

    def add_work(self, worker_id, work):
        """Insert the new solution"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO work (worker_id, work_value)
            VALUES (%s, %s)
            ON CONFLICT (worker_id) DO UPDATE
            SET work_value = EXCLUDED.work_value;
            """,
            (worker_id, work),
        )

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()
