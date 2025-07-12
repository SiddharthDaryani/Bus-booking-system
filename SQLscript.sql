-- Create the database
CREATE DATABASE IF NOT EXISTS bus_booking_system;
USE bus_booking_system;

-- -----------------------------------------------------
-- Table `user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `user` (
  `UserID` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(255) NOT NULL,
  `LastName` VARCHAR(255) NOT NULL,
  `Email` VARCHAR(255) NOT NULL UNIQUE,
  `PhoneNumber` VARCHAR(20) NULL,
  `Password` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `buscompany`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `buscompany` (
  `CompanyID` INT NOT NULL AUTO_INCREMENT,
  `CompanyName` VARCHAR(255) NOT NULL UNIQUE,
  `ContactNumber` VARCHAR(20) NULL,
  `Email` VARCHAR(255) NULL,
  PRIMARY KEY (`CompanyID`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `bus`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bus` (
  `BusID` INT NOT NULL AUTO_INCREMENT,
  `CompanyID` INT NOT NULL,
  `BusNumber` VARCHAR(20) NOT NULL UNIQUE,
  `SeatCapacity` INT NOT NULL,
  PRIMARY KEY (`BusID`),
  INDEX `fk_bus_buscompany_idx` (`CompanyID` ASC) VISIBLE,
  CONSTRAINT `fk_bus_buscompany`
    FOREIGN KEY (`CompanyID`)
    REFERENCES `buscompany` (`CompanyID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `route`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `route` (
  `RouteID` INT NOT NULL AUTO_INCREMENT,
  `Source` VARCHAR(255) NOT NULL,
  `Destination` VARCHAR(255) NOT NULL,
  `Distance` DECIMAL(10,2) NULL,
  PRIMARY KEY (`RouteID`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `schedule`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `schedule` (
  `ScheduleID` INT NOT NULL AUTO_INCREMENT,
  `BusID` INT NOT NULL,
  `RouteID` INT NOT NULL,
  `DepartureDate` DATE NOT NULL,
  `DepartureTime` TIME NOT NULL,
  `ArrivalTime` TIME NOT NULL,
  `Price` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`ScheduleID`),
  INDEX `fk_schedule_bus1_idx` (`BusID` ASC) VISIBLE,
  INDEX `fk_schedule_route1_idx` (`RouteID` ASC) VISIBLE,
  CONSTRAINT `fk_schedule_bus1`
    FOREIGN KEY (`BusID`)
    REFERENCES `bus` (`BusID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_schedule_route1`
    FOREIGN KEY (`RouteID`)
    REFERENCES `route` (`RouteID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `availableseats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `availableseats` (
  `ScheduleID` INT NOT NULL,
  `SeatNumber` INT NOT NULL,
  PRIMARY KEY (`ScheduleID`, `SeatNumber`),
  INDEX `fk_availableseats_schedule1_idx` (`ScheduleID` ASC) VISIBLE,
  CONSTRAINT `fk_availableseats_schedule1`
    FOREIGN KEY (`ScheduleID`)
    REFERENCES `schedule` (`ScheduleID`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `booking`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `booking` (
  `BookingID` INT NOT NULL AUTO_INCREMENT,
  `ScheduleID` INT NOT NULL,
  `UserID` INT NOT NULL,
  `SeatNumber` INT NOT NULL,
  `BookingDate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`BookingID`),
  INDEX `fk_booking_schedule1_idx` (`ScheduleID` ASC) VISIBLE,
  INDEX `fk_booking_user1_idx` (`UserID` ASC) VISIBLE,
  CONSTRAINT `fk_booking_schedule1`
    FOREIGN KEY (`ScheduleID`)
    REFERENCES `schedule` (`ScheduleID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_booking_user1`
    FOREIGN KEY (`UserID`)
    REFERENCES `user` (`UserID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;


--
-- Data for table `user`
--
INSERT INTO `user` (`FirstName`, `LastName`, `Email`, `PhoneNumber`, `Password`) VALUES
('Alice', 'Smith', 'alice.smith@example.com', '1234567890', 'pass123'),
('Bob', 'Johnson', 'bob.johnson@example.com', '0987654321', 'securepass'),
('Charlie', 'Brown', 'charlie.brown@example.com', '1122334455', 'mysecret');

--
-- Data for table `buscompany`
--
INSERT INTO `buscompany` (`CompanyName`, `ContactNumber`, `Email`) VALUES
('SwiftBus', '9988776655', 'info@swiftbus.com'),
('StarTravels', '1231231234', 'contact@startravels.com');

--
-- Data for table `bus`
--
INSERT INTO `bus` (`CompanyID`, `BusNumber`, `SeatCapacity`) VALUES
(1, 'SB001', 40),
(1, 'SB002', 30),
(2, 'ST001', 50);

--
-- Data for table `route`
--
INSERT INTO `route` (`Source`, `Destination`, `Distance`) VALUES
('New York', 'Boston', 350.00),
('Los Angeles', 'San Francisco', 600.50),
('Chicago', 'Miami', 2000.00);

--
-- Data for table `schedule`
--
INSERT INTO `schedule` (`BusID`, `RouteID`, `DepartureDate`, `DepartureTime`, `ArrivalTime`, `Price`) VALUES
(1, 1, '2025-07-15', '08:00:00', '13:00:00', 45.00),
(2, 1, '2025-07-15', '10:00:00', '15:30:00', 40.00),
(3, 2, '2025-07-16', '09:00:00', '17:00:00', 75.50),
(1, 3, '2025-07-17', '22:00:00', '10:00:00', 120.00);

--
-- Data for table `availableseats`
--
-- For ScheduleID 1 (BusID 1, Route 1, New York to Boston, 40 seats)
INSERT INTO `availableseats` (`ScheduleID`, `SeatNumber`) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
(1, 6), (1, 7), (1, 8), (1, 9), (1, 10),
(1, 11), (1, 12), (1, 13), (1, 14), (1, 15),
(1, 16), (1, 17), (1, 18), (1, 19), (1, 20),
(1, 21), (1, 22), (1, 23), (1, 24), (1, 25),
(1, 26), (1, 27), (1, 28), (1, 29), (1, 30),
(1, 31), (1, 32), (1, 33), (1, 34), (1, 35),
(1, 36), (1, 37), (1, 38), (1, 39), (1, 40);

-- For ScheduleID 2 (BusID 2, Route 1, New York to Boston, 30 seats)
INSERT INTO `availableseats` (`ScheduleID`, `SeatNumber`) VALUES
(2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
(2, 6), (2, 7), (2, 8), (2, 9), (2, 10),
(2, 11), (2, 12), (2, 13), (2, 14), (2, 15),
(2, 16), (2, 17), (2, 18), (2, 19), (2, 20),
(2, 21), (2, 22), (2, 23), (2, 24), (2, 25),
(2, 26), (2, 27), (2, 28), (2, 29), (2, 30);

-- For ScheduleID 3 (BusID 3, Route 2, Los Angeles to San Francisco, 50 seats)
INSERT INTO `availableseats` (`ScheduleID`, `SeatNumber`) VALUES
(3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
(3, 6), (3, 7), (3, 8), (3, 9), (3, 10),
(3, 11), (3, 12), (3, 13), (3, 14), (3, 15),
(3, 16), (3, 17), (3, 18), (3, 19), (3, 20),
(3, 21), (3, 22), (3, 23), (3, 24), (3, 25),
(3, 26), (3, 27), (3, 28), (3, 29), (3, 30),
(3, 31), (3, 32), (3, 33), (3, 34), (3, 35),
(3, 36), (3, 37), (3, 38), (3, 39), (3, 40),
(3, 41), (3, 42), (3, 43), (3, 44), (3, 45),
(3, 46), (3, 47), (3, 48), (3, 49), (3, 50);

--
-- Stored Procedure: FindAvailableBuses
--
DELIMITER //

CREATE PROCEDURE FindAvailableBuses(
    IN p_source VARCHAR(255),
    IN p_destination VARCHAR(255),
    IN p_travel_date DATE
)
BEGIN
    SELECT
        s.ScheduleID,
        b.BusNumber,
        bc.CompanyName,
        r.Source,
        r.Destination,
        s.DepartureDate,
        s.DepartureTime,
        s.ArrivalTime,
        s.Price,
        b.SeatCapacity,
        (SELECT COUNT(*) FROM availableseats WHERE ScheduleID = s.ScheduleID) AS AvailableSeatsCount
    FROM
        schedule s
    JOIN
        bus b ON s.BusID = b.BusID
    JOIN
        buscompany bc ON b.CompanyID = bc.CompanyID
    JOIN
        route r ON s.RouteID = r.RouteID
    WHERE
        r.Source = p_source AND r.Destination = p_destination AND s.DepartureDate = p_travel_date
    HAVING
        AvailableSeatsCount > 0; -- Only show schedules with available seats
END //

DELIMITER ;

--
-- Stored Procedure: BookSeat
--
DELIMITER //

CREATE PROCEDURE BookSeat(
    IN p_schedule_id INT,
    IN p_seat_number INT,
    IN p_user_id INT
)
BEGIN
    -- Start a transaction
    START TRANSACTION;

    -- Check if the seat is available
    IF EXISTS (SELECT 1 FROM availableseats WHERE ScheduleID = p_schedule_id AND SeatNumber = p_seat_number) THEN
        -- Insert into booking table
        INSERT INTO booking (ScheduleID, UserID, SeatNumber, BookingDate)
        VALUES (p_schedule_id, p_user_id, p_seat_number, NOW());

        -- Remove from available seats
        DELETE FROM availableseats
        WHERE ScheduleID = p_schedule_id AND SeatNumber = p_seat_number;

        -- Commit the transaction
        COMMIT;
    ELSE
        -- Rollback if seat is not available
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat not available or already booked.';
    END IF;
END //

DELIMITER ;


-- After a booking, you would typically remove the seat from `availableseats`
-- These are here for initial data setup, but the BookSeat procedure handles this for new bookings.
DELETE FROM `availableseats` WHERE `ScheduleID` = 1 AND `SeatNumber` = 10;
DELETE FROM `availableseats` WHERE `ScheduleID` = 1 AND `SeatNumber` = 11;
DELETE FROM `availableseats` WHERE `ScheduleID` = 3 AND `SeatNumber` = 5;

-- Trying the call function with sample data entered
CALL FindAvailableBuses('New York', 'Boston', '2025-07-15');
CALL FindAvailableBuses('Los Angeles', 'San Francisco', '2025-07-16');

-- Before running BookSeat, let's verify current available seats for a schedule
SELECT * FROM availableseats WHERE ScheduleID = 1;

-- Trying to book seat number 12 on Schedule 1 for User 1
CALL BookSeat(1, 12, 1);
SELECT * FROM booking WHERE ScheduleID = 1 AND UserID = 1 AND SeatNumber = 12;

-- Verify the seat is removed from available_seats
SELECT * FROM availableseats WHERE ScheduleID = 1 AND SeatNumber = 12;