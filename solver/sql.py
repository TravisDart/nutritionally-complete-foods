import sqlite3
import datetime

from itertools import combinations


class SQLStore:
    def __init__(self, db_file, num_foods, start_over=False, verbose=False):
        """
        SQL IDs are lists delimited by spaces so we can call .split() on them later.
        """
        self.num_foods = num_foods
        self.verbose = verbose

        self.conn = sqlite3.connect(db_file)
        cursor = self.conn.cursor()

        if start_over:
            if self.verbose:
                print("Starting over")
            cursor.execute(f"DROP TABLE IF EXISTS exclude")
            cursor.execute(f"DROP TABLE IF EXISTS solutions")
            cursor.execute(f"DROP TABLE IF EXISTS foods")
            self.conn.commit()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS exclude (
                id TEXT PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER
            )
        """
        )
        self.conn.commit()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS solutions (
                id TEXT PRIMARY KEY
            )
        """
        )
        self.conn.commit()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS foods (
                id TEXT PRIMARY KEY
            )
        """
        )
        self.conn.commit()

        # Start out by excluding nothing.
        cursor.execute("""INSERT OR IGNORE INTO exclude (id) VALUES ("");""")
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def exclusions(self):
        cursor = self.conn.cursor()
        while True:
            cursor.execute(
                """
                UPDATE exclude
                SET start_time = DATETIME('now')
                WHERE id = (SELECT MIN(id) FROM exclude WHERE start_time IS NULL)
                RETURNING id;
                """
            )

            row = cursor.fetchone()
            if row is None:
                break
            else:
                if self.verbose:
                    print()
                    print("Excluding", row[0])
                yield row[0].split()

    def add_try(self, exclusion):
        """Update the timestamp of the exclusion so we can see how long the solver took."""
        cursor = self.conn.cursor()
        sql_id = " ".join([str(e) for e in exclusion])
        cursor.execute(
            """
            UPDATE exclude
            SET end_time = DATETIME('now'),
                duration = (SELECT JULIANDAY(DATETIME('now')) - JULIANDAY(start_time)) * 86400 -- Seconds
            WHERE id = ?
            """,
            (sql_id,),
        )
        self.conn.commit()

    def add_solution(self, solution):
        """Insert the new solution"""
        # Convert tuple to string to store in SQL so we can call .split() on it later.
        if self.verbose:
            print("Adding solution", solution)

        cursor = self.conn.cursor()
        sql_id = " ".join([str(e) for e in solution])

        # Check if the solution already exists
        cursor.execute(
            """SELECT id FROM solutions WHERE id = ?;""",
            (sql_id,),
        )
        if cursor.fetchone() is not None:
            if self.verbose:
                print("Solution already exists")
            return

        # Continue if the solution does not exist...

        cursor.execute(
            """INSERT OR IGNORE INTO solutions (id) VALUES (?);""",
            (sql_id,),
        )
        for food_id in solution:
            cursor.execute(
                """INSERT OR IGNORE INTO foods (id) VALUES (?);""", (food_id,)
            )
        self.conn.commit()

        # Recalculate all combinations
        cursor.execute(f"SELECT id FROM foods")
        all_foods = [f[0] for f in cursor.fetchall()]
        if self.verbose:
            print("foods_in_solutions", all_foods)

        all_combinations = set(
            [
                " ".join(y)
                for x in range(len(all_foods) + 1)
                for y in combinations(all_foods, min(x, self.num_foods))
            ]
        )

        # Don't reinsert the ones that already exist.
        cursor.execute(f"SELECT id FROM exclude")
        already_exists = set([e[0] for e in cursor.fetchall()])

        new_combinations_to_exclude = all_combinations - already_exists
        # Use "OR IGNORE" to be on the safe side.
        sql = "INSERT OR IGNORE INTO exclude (id) VALUES (?)"

        cursor.executemany(sql, [(c,) for c in new_combinations_to_exclude])

        if self.verbose:
            print("all_combinations", len(all_combinations))
            print(
                "new_combinations_to_exclude",
                len(new_combinations_to_exclude),
            )
            print("already_exists", len(already_exists))
