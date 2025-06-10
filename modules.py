import mysql.connector
from logger import logging # Import the configured logger for logging within this module

class ConnectDB:
    def __init__(self, host='localhost', user='root', password='0000', database='bus_booking_system'):
        # Initialize connection parameters
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        # Initialize the database connection attribute as None.
        # The connection will be established/re-established when needed.
        self._mydb = None 

    def _get_db_connection(self):
        """
        Internal method to get an active database connection.
        If the current connection is None or not connected, it establishes a new one.
        This ensures that every database operation uses a live connection.
        """
        if self._mydb is None or not self._mydb.is_connected():
            logging.info("Attempting to establish a new database connection.")
            try:
                self._mydb = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                logging.info("Successfully established a new database connection.")
            except mysql.connector.Error as err:
                # Log the specific MySQL connection error
                logging.error(f"Error connecting to database: {err}", exc_info=True)
                # Re-raise a custom exception to be caught in app.py
                raise ConnectionError("Could not connect to the database.") from err
        return self._mydb

    # The public method for app.py to establish connection (now just calls the internal getter)
    def connect_to_db(self):
        """
        Public method called by app.py to ensure the database connection is established.
        It internally uses _get_db_connection to get or create a valid connection.
        """
        return self._get_db_connection()

    def find_available_buses(self, source, destination, travel_date):
        """
        Finds available buses based on source, destination, and date.
        Ensures a live database connection before executing the query.
        """
        db_conn = self._get_db_connection() # Get an active connection
        cursor = None # Initialize cursor to None for finally block
        try:
            # Fetch results as dictionaries for easier access
            cursor = db_conn.cursor(dictionary=True) 
            query = "CALL FindAvailableBuses(%s, %s, %s);"
            cursor.execute(query, (source, destination, travel_date))
            results = cursor.fetchall() # Fetch all results

            if results:
                logging.info(f"Found {len(results)} available buses for {source} to {destination} on {travel_date}.")
                return results
            else:
                logging.info(f"No available buses found for {source} to {destination} on {travel_date}.")
                return None
        except mysql.connector.Error as err:
            logging.error(f"Error finding available buses: {err}", exc_info=True)
            raise # Re-raise the exception to be caught by app.py's error handling
        finally:
            if cursor:
                cursor.close()
            # The connection (db_conn / self._mydb) is managed by _get_db_connection and close_connection()
            # So, we don't close the connection here for every cursor operation.

    def book_seat(self, schedule_id, seat_number, user_id):
        """
        Books a seat for a user.
        Ensures a live database connection before executing the booking procedure.
        """
        db_conn = self._get_db_connection() # Get an active connection
        cursor = None # Initialize cursor to None for finally block
        try:
            cursor = db_conn.cursor()
            query = "CALL BookSeat(%s, %s, %s);"
            cursor.execute(query, (schedule_id, seat_number, user_id))
            db_conn.commit() # Important: Commit changes to the database.
            logging.info(f"Seat {seat_number} booked successfully for ScheduleID {schedule_id}, UserID {user_id}.")
            return True # Booking successful.
        except mysql.connector.Error as err:
            db_conn.rollback() # Rollback transaction if an error occurs during booking.
            logging.error(f"Error during booking seat {seat_number} for ScheduleID {schedule_id}, UserID {user_id}: {err}", exc_info=True)
            return False # Booking failed.
        finally:
            if cursor:
                cursor.close()

    def close_connection(self):
        """
        Closes the database connection if it is open.
        This should be called at the end of the request lifecycle in app.py.
        """
        if self._mydb and self._mydb.is_connected():
            self._mydb.close()
            logging.info("Database connection explicitly closed.")
            self._mydb = None # Reset the connection to None
        else:
            logging.info("No active database connection to close (or already closed).")
            
    def get_user_id(self, email):
        """
        Retrieves the user ID based on the email.
        Ensures a live database connection before executing the query.
        """
        db_conn = self._get_db_connection() # Get an active connection
        cursor = None # Initialize cursor to None for finally block
        try:
            cursor = db_conn.cursor()
            query = "SELECT UserID FROM User WHERE Email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            if result:
                logging.info(f"User ID found for email {email}.")
                return result[0]
            else:
                logging.info(f"No user ID found for email {email}.")
                return None
        except mysql.connector.Error as err:
            logging.error(f"Error getting user ID for email {email}: {err}", exc_info=True)
            raise # Re-raise the exception to be caught by app.py's error handling
        finally:
            if cursor:
                cursor.close()