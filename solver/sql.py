from typing import List, Optional

import psycopg

from itertools import combinations
from solver.logger import Logger, NullLogger


class SQLStore:
    def __init__(self, db_url: str, num_foods: int, logger: Logger = None):
        self.logger = NullLogger if logger is None else logger
        self.num_foods = num_foods
        self.conn = psycopg.connect(db_url)
        self.conn.autocommit = True
        self.conn.isolation_level = psycopg.IsolationLevel.SERIALIZABLE

    @classmethod
    def resume(self):
        """
        Reset the start time of any exclusions we started during the last run but didn't finish.
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE exclude set start_time = null where end_time is null;")

    def initialize(self, timeout: int):
        cursor = self.conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS exclude CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS solutions CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS foods CASCADE;")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exclude (
                id smallint[] PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                timeout BOOLEAN,
                claimed_by INTEGER UNIQUE,
                duration INTEGER
            );
        """
        )

        cursor.execute(
            """
            CREATE OR REPLACE VIEW process_status AS
            select
                id,
                start_time,
                coalesce(duration, EXTRACT(EPOCH FROM (NOW() - start_time))::int) as current_duration
            from exclude
            where start_time is not null and end_time is null
            order by start_time desc
            ;
            """
        )

        cursor.execute(
            f"""
            CREATE OR REPLACE VIEW timed_out_processes AS
            select claimed_by
              from exclude
             where start_time is not null
               and end_time is null
               and EXTRACT(EPOCH FROM (NOW() - start_time))::int > {timeout}
             order by start_time desc
            ;
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

    def get_exclusion(self, worker_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT count(*) FROM exclude WHERE start_time IS NULL;")
        self.logger.log("items to exclude", cursor.fetchone()[0])

        cursor.execute("SELECT pg_advisory_lock(1);")
        try:
            cursor.execute(
                """
                UPDATE exclude
                SET start_time = NOW(),
                claimed_by = %s
                WHERE id = (SELECT id FROM exclude WHERE start_time IS NULL LIMIT 1)
                RETURNING id;
                """,
                (worker_id,),
            )
            row = cursor.fetchall()
        finally:
            cursor.execute("SELECT pg_advisory_unlock(1);")

        if row == []:
            return
        else:
            return row[0][0]

    def get_timed_out_processes(self):
        """Update the timestamp of the exclusion so we can see how long the solver took."""
        cursor = self.conn.cursor()
        results = cursor.execute("SELECT * FROM timed_out_processes;")
        return [r[0] for r in results]

    def add_result(
        self, exclusion: List[int], timeout: bool, solution: Optional[List[int]] = None
    ):
        """Update the timestamp of the exclusion so we can see how long the solver took."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT pg_advisory_lock(1);")
        try:
            cursor.execute(
                """
                UPDATE exclude
                SET end_time = NOW(),
                    timeout = %s,
                    claimed_by = NULL,
                    duration = EXTRACT(EPOCH FROM (NOW() - start_time))
                WHERE id = %s
                """,
                (
                    timeout,
                    exclusion,
                ),
            )
        finally:
            cursor.execute("SELECT pg_advisory_unlock(1);")

        if solution:
            self._add_solution(solution)

    def _add_solution(self, solution):
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
