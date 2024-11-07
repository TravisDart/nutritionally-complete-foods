import time

import psycopg

import datetime
from itertools import combinations
from solver.logger import Logger


class SQLStore:
    def __init__(self, db_url: str, num_foods: int, logger: Logger):
        self.logger = logger
        self.num_foods = num_foods
        self.conn = psycopg.connect(db_url)
        self.conn.autocommit = True
        self.conn.isolation_level = psycopg.IsolationLevel.SERIALIZABLE

        # If there are no jobs on startup, the workers will wait one time.
        # If there are no jobs again, the workers will exit.
        self.startup_wait = 10

    @classmethod
    def initialize(cls, db_url: str):
        conn = psycopg.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS exclude;")
        cursor.execute("DROP TABLE IF EXISTS solutions;")
        cursor.execute("DROP TABLE IF EXISTS foods;")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exclude (
                id smallint[] PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER
            );
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS solutions (
                id smallint[] PRIMARY KEY
            );
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS foods (
                id smallint PRIMARY KEY
            );
        """
        )

        # Start out by excluding nothing.
        cursor.execute(
            """INSERT INTO exclude (id) VALUES ('{}') ON CONFLICT DO NOTHING;"""
        )

    def __del__(self):
        self.conn.close()

    def exclusions(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM exclude WHERE start_time IS NULL;")
        self.logger.log("items to exclude", cursor.fetchone()[0])

        while True:
            cursor.execute("SELECT pg_advisory_lock(1);")
            try:
                cursor.execute(
                    """
                    UPDATE exclude
                    SET start_time = NOW()
                    WHERE id = (SELECT id FROM exclude WHERE start_time IS NULL LIMIT 1)
                    RETURNING id;
                    """
                )
                row = cursor.fetchall()
            finally:
                cursor.execute("SELECT pg_advisory_unlock(1);")

            if row == []:
                if self.startup_wait > 0:
                    self.startup_wait -= 1
                    self.logger.log("waiting", self.startup_wait)
                    time.sleep(5)
                else:
                    return
            else:
                self.logger.log("Excluding", row[0][0])
                yield row[0][0]

    def add_try(self, exclusion):
        """Update the timestamp of the exclusion so we can see how long the solver took."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT pg_advisory_lock(1);")
        try:
            cursor.execute(
                """
            UPDATE exclude
            SET end_time = NOW(),
                duration = EXTRACT(EPOCH FROM (NOW() - start_time))
            WHERE id = %s
            """,
                (exclusion,),
            )
        finally:
            cursor.execute("SELECT pg_advisory_unlock(1);")

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
        for food_id in solution:
            cursor.execute(
                """INSERT INTO foods (id) VALUES (%s) ON CONFLICT DO NOTHING;""",
                (food_id,),
            )

        cursor.execute("SELECT id FROM foods")
        all_foods = [f[0] for f in cursor.fetchall()]
        self.logger.log("all_foods", all_foods)

        all_combinations = set(
            [
                y
                for x in range(len(all_foods) + 1)
                for y in combinations(all_foods, min(x, self.num_foods))
            ]
        )

        cursor.execute("SELECT id FROM exclude;")
        already_exists = set([tuple(e[0]) for e in cursor.fetchall()])

        new_combinations_to_exclude = all_combinations - already_exists

        cursor.executemany(
            "INSERT INTO exclude (id) VALUES (%s) ON CONFLICT DO NOTHING",
            [(list(c),) for c in new_combinations_to_exclude],
        )

        self.logger.log(
            "all_combinations",
            len(all_combinations),
            "new_combinations_to_exclude",
            len(new_combinations_to_exclude),
            "already_exists",
            len(already_exists),
        )
