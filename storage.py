import datetime
import pickle
import sqlite3

SCHEMA = '''
CREATE TABLE IF NOT EXISTS results (
    origin_airport VARCHAR(3) NOT NULL,
    destination_airport VARCHAR(3) NOT NULL,
    date VARCHAR(10) NOT NULL,
    request_timestamp VARCHAR(10) NOT NULL,
    query_result TEXT NUL NULL
)'''


class Storage(object):
    def __init__(self, database_file):
        self.con_ = sqlite3.connect(database_file)
        self.con_.execute(SCHEMA)

    def add(self, result):
        self.con_.execute('INSERT INTO results VALUES (?, ?, ?, ?, ?)',
                          (result.route[0], result.route[1], result.route[2], result.timestamp, pickle.dumps(result), ))
        self.con_.commit()

    def has_valid(self, route):
        max_age = (datetime.datetime.now() -
                   datetime.timedelta(days=1)).isoformat()

        cursor = self.con_.execute('''SELECT COUNT(*) > 0
        FROM results
        WHERE
        origin_airport = ?
        AND destination_airport = ?
        AND date = ?
        AND request_timestamp >= ?''',
                                   (route[0], route[1], route[2], max_age))

        count = next(cursor)[0]
        return count > 0

    def load_freshest(self):
        cur = self.con_.cursor()
        flights = {}
        for row in cur.execute('SELECT query_result FROM results'):
            res = pickle.loads(row[0])
            age = datetime.datetime.now() - res.timestamp
            if age >= datetime.timedelta(hours=24):
                continue

            if res.route not in flights:
                flights[res.route] = res
            else:
                flights[res.route] = max(
                    res, flights[res.route], key=lambda x: x.timestamp)

        return flights
