
CREATE DATABASE hospitality_analytics;

USE hospitality_analytics;

-- 1. Hotel master
CREATE TABLE hotels (
    hotel_id CHAR(36) PRIMARY KEY,
    hotel_name VARCHAR(150) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    hotel_category VARCHAR(50)
);

-- 2. Room master
CREATE TABLE rooms (
    room_id CHAR(36) PRIMARY KEY,
    hotel_id CHAR(36) NOT NULL,
    room_number VARCHAR(20),
    room_type VARCHAR(50),
    base_rate DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id),
    UNIQUE (hotel_id, room_number)
);

-- 3. Guest master
CREATE TABLE guests (
    guest_id CHAR(36) PRIMARY KEY,
    guest_name VARCHAR(150) NOT NULL,
    guest_email VARCHAR(150),
    guest_city VARCHAR(100)
);

-- 4. Booking transactions
CREATE TABLE bookings (
    booking_id CHAR(36) PRIMARY KEY,
    guest_id CHAR(36) NOT NULL,
    room_id CHAR(36) NOT NULL,
    booking_date DATE NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    nightly_rate DECIMAL(10,2) NOT NULL,
    booking_status VARCHAR(30) NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id),
    CHECK (check_out_date > check_in_date),
    CHECK (nightly_rate >= 0),
    CHECK (booking_status IN ('Completed', 'Cancelled', 'No Show'))
);

-- 5. Employee master and employment history
CREATE TABLE employees (
    employee_id CHAR(36) PRIMARY KEY,
    hotel_id CHAR(36) NOT NULL,
    employee_name VARCHAR(150) NOT NULL,
    position VARCHAR(100),
    hire_date DATE NOT NULL,
    termination_date DATE,
    employment_status VARCHAR(30),
    FOREIGN KEY (hotel_id) REFERENCES hotels(hotel_id),
    CHECK (termination_date IS NULL OR termination_date >= hire_date)
);

-- 6. Guest feedback
CREATE TABLE guest_feedback (
    feedback_id CHAR(36) PRIMARY KEY,
    booking_id CHAR(36) NOT NULL,
    rating DECIMAL(3,2) NOT NULL,
    feedback_date DATE NOT NULL,
    comments TEXT,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
    UNIQUE (booking_id),
    CHECK (rating >= 1 AND rating <= 5)
);

