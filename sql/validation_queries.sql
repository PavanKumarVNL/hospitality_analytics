USE hospitality_analytics;

SELECT 'hotels' AS table_name, COUNT(*) AS records FROM hotels
UNION ALL
SELECT 'rooms', COUNT(*) FROM rooms
UNION ALL
SELECT 'guests', COUNT(*) FROM guests
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'guest_feedback', COUNT(*) FROM guest_feedback;

SELECT
    booking_status,
    COUNT(*) AS total_bookings,
    MIN(check_in_date) AS first_checkin,
    MAX(check_in_date) AS last_checkin
FROM bookings
GROUP BY booking_status;


SELECT
    (SELECT COUNT(*)
     FROM rooms r
     LEFT JOIN hotels h ON r.hotel_id = h.hotel_id
     WHERE h.hotel_id IS NULL) AS invalid_rooms,

    (SELECT COUNT(*)
     FROM bookings b
     LEFT JOIN guests g ON b.guest_id = g.guest_id
     WHERE g.guest_id IS NULL) AS invalid_guests,

    (SELECT COUNT(*)
     FROM bookings b
     LEFT JOIN rooms r ON b.room_id = r.room_id
     WHERE r.room_id IS NULL) AS invalid_bookings,

    (SELECT COUNT(*)
     FROM guest_feedback f
     LEFT JOIN bookings b ON f.booking_id = b.booking_id
     WHERE b.booking_id IS NULL) AS invalid_feedback;
     
     
SELECT
    MIN(rating) AS minimum_rating,
    MAX(rating) AS maximum_rating,
    ROUND(AVG(rating), 2) AS average_rating,
    COUNT(*) AS total_feedback
FROM guest_feedback;

-- validate aggregated tables

SELECT 'hotel_performance' AS table_name, COUNT(*) AS records
FROM agg_hotel_monthly_performance

UNION ALL

SELECT 'guest_satisfaction', COUNT(*)
FROM agg_guest_satisfaction

UNION ALL

SELECT 'employee_turnover', COUNT(*)
FROM agg_employee_turnover;	
