import os.path
from datetime import datetime
import sqlite3
import math


class DatabaseHelper:
    # init the service with the path to the database
    def __init__(self, dbPath):
        # check if db exists
        first_time = os.path.isfile(dbPath) == False

        # connect or connect and create a new sqlite db
        self._connection = sqlite3.connect(dbPath)
        self._cursor = self._connection.cursor()

        # connection ok, create tables if needs
        if (first_time):
            # create the table
            query = '''CREATE TABLE records (
				id INTEGER PRIMARY KEY,
				employeeName STRING NOT NULL,
				start_time LONG NOT NULL,
				end_time LONG
				)'''
            self._cursor.execute(query)

        # init cache
        self._record_id = None
        self.last_activity = None
        self.last_start_time = None
        self.current_activity = None

        if (first_time == False):
            # is not the first time, an activity could exist
            self.CacheMemory()

    # update cache values from db
    def CacheMemory(self):
        result = self._cursor.execute(
            '''SELECT id, employeeName, start_time, end_time 
            FROM records 
            ORDER BY start_time DESC 
            LIMIT 1''')
        row = result.fetchone()
        if row:
            self._record_id = int(row[0])
            self.last_activity = str(row[1])
            self.last_start_time = str(row[2])
            # check if the activity is ended
            if row[3] is None:
                # the activity is "running"
                self.current_activity = self.last_activity

    def start_record(self, activity=None):
        result_string = ''
        # check if activity is given
        if activity == None or len(activity) == 0:
            # no activity, try to check the cache
            if self.current_activity:
                # I have a current activity, that is the last activity also
                # I can't run a new blank activity
                return "INFO: " + self.current_activity + " just started"
            elif self.last_activity:
                # I have a last activity (no current activity), use it as activity to start
                activity = self.last_activity
            else:
                # no current activity and no last activity, it is the "first time".
                return "ERROR: no activity to start. Write an activity (e.g. start working)"

        # if I have an other activity running, I need to stop it first!
        if self.current_activity and activity != self.current_activity:
            result_string += self.stop() + '\n'
        # if the activity to start is the same, do nothing
        elif self.current_activity == activity:
            # activity is currently running
            return "INFO: " + self.current_activity + " just started"

        # save the activity in the db
        date = datetime.utcnow()
        timestamp = int(date.timestamp())
        self._cursor.execute('INSERT INTO records (employeeName, start_time) VALUES (?, ?)', (activity, timestamp))
        # commit changes
        self._connection.commit()

        self.CacheMemory()

        result_string += "INFO: " + activity + " started at " + date.isoformat()
        return result_string

    def stop_record(self):
        if self.current_activity is None:
            return "ERROR: no activity to stop"

        # update the activity in the cache
        ended_activity = self.current_activity
        self.current_activity = None

        # update the record in the db
        # create end time date
        date = datetime.utcnow()
        timestamp = int(date.timestamp())
        # execute db query
        self._cursor.execute('UPDATE records SET end_time=? WHERE id=?', (timestamp, self._record_id))
        self._connection.commit()
        # and in cache
        self._record_id = None

        # calculate the activity time
        seconds = timestamp - int(self.last_start_time)
        return "INFO: " + ended_activity + " takes " + DatabaseHelper.convertDuration(seconds) + " seconds"

    def delete_employee(self, ID):
        self._cursor.execute("""DELETE FROM records WHERE employeeName = ?""", ID)
        self._connection.commit()

    def update_employee(self, ID, newID):
        #print(ID, newID)
        self._cursor.execute("""UPDATE records SET employeeName = ? WHERE employeeName = ?""", (newID, ID))
        self._connection.commit()



    def show_list(self, limit=100):
        interval = 60 * 60 * 24

        # exe query
        result = self._cursor.execute(
            """SELECT id, employeeName, SUM(end_time - start_time) as duration, start_time/? as s_time,
            start_time, end_time
            FROM records 
            WHERE end_time IS NOT NULL
            GROUP BY employeeName, s_time
            ORDER BY start_time DESC 
            LIMIT ?""", (interval, limit))
        result_string = []
        result_string.append("Employee's Working Hours List")
        s_time = None
        # if exist, print the current_activity
        if self.current_activity is not None:
            result_string.append("\t{activity_name}\t\t\t(current)".format(activity_name=self.current_activity))
        # if there are records in the database, print the duration for each activity
        while True:
            row = result.fetchone()
            if row is None:
                break
            if s_time != row[3] and row[3] is not None:
                s_time = row[3]
                date = datetime.fromtimestamp(s_time * interval)
                result_string.append("\t Date: {date}".format(date=date.isoformat()))
            starting_time = datetime.fromtimestamp(float(row[4])).isoformat()
            ending_time = datetime.fromtimestamp(float(row[5])).isoformat()
            result_string.append("\t{id}\t{employee_name}\t\t\t{duration}\t{starting_time}\t{ending_time}".format(id=str(row[0]),
                                                                                                                  employee_name=str(row[1]),
                                                                                                                  duration=DatabaseHelper.convertDuration(row[2]),
                                                                                                                  starting_time=starting_time,
                                                                                                                  ending_time=ending_time))

        return "\n".join(result_string)

    def convertDuration(duration):
        tmp = (60 * 60)
        hours = math.floor(duration / tmp)
        minutes = math.floor((duration / 60) - (hours * 60))
        seconds = math.floor(duration - (hours * tmp) - (minutes * 60))
        return str(hours) + " hours, " + str(minutes) + " minutes and " + str(seconds) + " seconds"

    def dispose(self):
        self._connection.commit()
        self._connection.close()