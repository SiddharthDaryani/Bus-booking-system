import mysql.connector
from logger import logging

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
        This method is now mostly used for the final booking confirmation,
        as initial date/seat selection is handled by new API calls.
        """
        db_conn = self._get_db_connection() # Get an active connection
        cursor = None # Initialize cursor to None for finally block
        try:
            # Fetch results as dictionaries for easier access
            cursor = db_conn.cursor(dictionary=True) 
            # Updated query to join 'schedule', 'route', 'bus', and 'buscompany' tables
            query = """
            SELECT 
                s.ScheduleID, 
                b.BusNumber, 
                bc.CompanyName, 
                s.DepartureTime, 
                s.ArrivalTime, 
                s.Price, 
                r.Distance, 
                s.DepartureDate AS TravelDate 
            FROM schedule s
            JOIN route r ON s.RouteID = r.RouteID
            JOIN bus b ON s.BusID = b.BusID
            JOIN buscompany bc ON b.CompanyID = bc.CompanyID
            WHERE r.Source = %s AND r.Destination = %s AND s.DepartureDate = %s;
            """
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

    # New method to get available bus schedules (dates and IDs) for a route
    def get_available_bus_schedules(self, source, destination):
        """
        Retrieves unique available travel dates and their corresponding schedule IDs
        for a given source and destination.
        """
        db_conn = self._get_db_connection()
        cursor = None
        try:
            cursor = db_conn.cursor(dictionary=True)
            # Updated query to join 'schedule' and 'route' tables
            query = """
            SELECT DISTINCT s.DepartureDate AS TravelDate, s.ScheduleID 
            FROM schedule s
            JOIN route r ON s.RouteID = r.RouteID
            WHERE r.Source = %s AND r.Destination = %s 
            ORDER BY s.DepartureDate ASC;
            """
            cursor.execute(query, (source, destination))
            schedules = cursor.fetchall()
            logging.info(f"Retrieved {len(schedules)} available schedules/dates for {source} to {destination}.")
            return schedules
        except mysql.connector.Error as err:
            logging.error(f"Error retrieving available bus schedules: {err}", exc_info=True)
            raise
        finally:
            if cursor:
                cursor.close()

    # New method to get seat availability for a specific schedule
    def get_seat_availability(self, schedule_id):
        """
        Retrieves total seats and a list of occupied seats for a given schedule ID.
        Returns a dictionary: {'total_seats': int, 'occupied_seats': list}.
        """
        db_conn = self._get_db_connection()
        cursor = None
        try:
            cursor = db_conn.cursor(dictionary=True)

            # First, get the total number of seats for the bus associated with the schedule
            # Updated query to join 'schedule' and 'bus' tables
            total_seats_query = """
            SELECT b.SeatCapacity AS TotalSeats FROM schedule s
            JOIN bus b ON s.BusID = b.BusID
            WHERE s.ScheduleID = %s;
            """
            cursor.execute(total_seats_query, (schedule_id,))
            total_seats_result = cursor.fetchone()
            # If no total_seats found, default to 50 or handle error appropriately
            total_seats = total_seats_result['TotalSeats'] if total_seats_result else 50 

            # Then, get all occupied seats for that schedule from the 'booking' table
            occupied_seats_query = """
            SELECT SeatNumber FROM booking 
            WHERE ScheduleID = %s;
            """
            cursor.execute(occupied_seats_query, (schedule_id,))
            occupied_seats_results = cursor.fetchall()
            
            occupied_seat_numbers = [seat['SeatNumber'] for seat in occupied_seats_results]
            
            logging.info(f"Retrieved seat availability for ScheduleID {schedule_id}. Total: {total_seats}, Occupied: {len(occupied_seat_numbers)}")
            return {"total_seats": total_seats, "occupied_seats": occupied_seat_numbers}
        except mysql.connector.Error as err:
            logging.error(f"Error retrieving seat availability for ScheduleID {schedule_id}: {err}", exc_info=True)
            raise
        finally:
            if cursor:
                cursor.close()

    def book_seat(self, schedule_id, seat_number, user_id):
        """
        Books a seat for a user.
        Ensures a live database connection before executing the booking procedure.
        """
        db_conn = self._get_db_connection() # Get an active connection
        cursor = None # Initialize cursor to None for finally block
        try:
            cursor = db_conn.cursor()
            # Assuming BookSeat stored procedure handles availability check and actual booking (insertion).
            # If not, you might need to insert into the 'booking' table directly here.
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
            query = "SELECT UserID FROM user WHERE Email = %s" # Changed 'User' to 'user' for consistency
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

    def check_user_exists(self, user_id):
        """
        Checks if a given UserID exists in the 'user' table.
        Returns True if the user exists, False otherwise.
        """
        db_conn = self._get_db_connection()
        cursor = None
        try:
            cursor = db_conn.cursor()
            query = "SELECT COUNT(*) FROM user WHERE UserID = %s;"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            exists = result[0] > 0
            logging.info(f"User ID {user_id} exists: {exists}")
            return exists
        except mysql.connector.Error as err:
            logging.error(f"Error checking if user {user_id} exists: {err}", exc_info=True)
            raise # Re-raise to be handled by app.py
        finally:
            if cursor:
                cursor.close()

    def register_user(self, user_id, first_name, last_name, email, phone_number, password):
        """
        Registers a new user with provided details.
        Note: This is a simplified registration for demonstration/testing.
        In a real application, you'd handle password hashing securely.
        """
        db_conn = self._get_db_connection()
        cursor = None
        try:
            cursor = db_conn.cursor()
            # If UserID is AUTO_INCREMENT, you'd omit UserID from the INSERT and let DB assign.
            # Assuming UserID is provided and not auto-incremented here.
            query = """
            INSERT INTO user (UserID, FirstName, LastName, Email, PhoneNumber, Password)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (user_id, first_name, last_name, email, phone_number, password))
            db_conn.commit()
            logging.info(f"User {user_id} ({email}) registered successfully.")
            return True
        except mysql.connector.Error as err:
            db_conn.rollback()
            logging.error(f"Error registering user {user_id}: {err}", exc_info=True)
            # Catch duplicate entry error if UserID is primary key and user tries to register existing ID
            if err.errno == 1062: # MySQL error code for Duplicate entry for primary key
                logging.warning(f"Attempted to register user {user_id} but UserID already exists.")
                return False # Indicate that registration failed due to duplicate ID
            raise # Re-raise for other errors
        finally:
            if cursor:
                cursor.close()

    def get_schedule_details_by_id(self, schedule_id):
        """
        Retrieves full details of a bus schedule by its ScheduleID.
        """
        db_conn = self._get_db_connection()
        cursor = None
        try:
            cursor = db_conn.cursor(dictionary=True)
            query = """
            SELECT 
                s.ScheduleID, 
                b.BusNumber, 
                bc.CompanyName, 
                s.DepartureTime, 
                s.ArrivalTime, 
                s.Price, 
                r.Distance, 
                s.DepartureDate AS DepartureDate, # Use DepartureDate for clarity
                r.Source,
                r.Destination
            FROM schedule s
            JOIN route r ON s.RouteID = r.RouteID
            JOIN bus b ON s.BusID = b.BusID
            JOIN buscompany bc ON b.CompanyID = bc.CompanyID
            WHERE s.ScheduleID = %s;
            """
            cursor.execute(query, (schedule_id,))
            details = cursor.fetchone() # Fetch single row
            if details:
                logging.info(f"Retrieved details for ScheduleID: {schedule_id}")
            else:
                logging.warning(f"No schedule details found for ScheduleID: {schedule_id}")
            return details
        except mysql.connector.Error as err:
            logging.error(f"Error retrieving schedule details for ID {schedule_id}: {err}", exc_info=True)
            raise
        finally:
            if cursor:
                cursor.close()
