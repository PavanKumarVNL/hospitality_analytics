-- Create a monthly calendar

USE hospitality_analytics;

CREATE TABLE dim_months (
    month_start DATE PRIMARY KEY,
    month_end DATE NOT NULL
);

INSERT INTO dim_months (month_start, month_end)
WITH RECURSIVE months AS (
    SELECT DATE('2021-01-01') AS month_start

    UNION ALL

    SELECT DATE_ADD(month_start, INTERVAL 1 MONTH)
    FROM months
    WHERE month_start < '2025-12-01'
)
SELECT
    month_start,
    LAST_DAY(month_start)
FROM months;

-- Hotel monthly performance


CREATE TABLE agg_hotel_monthly_performance AS

SELECT
    h.hotel_id,
    h.hotel_name,
    m.month_start,

    COUNT(DISTINCT r.room_id)
        * (DATEDIFF(m.month_end, m.month_start) + 1)
        AS available_room_nights,

    COALESCE(
        SUM(
            CASE
                WHEN b.booking_id IS NOT NULL
                THEN DATEDIFF(
                    LEAST(b.check_out_date, DATE_ADD(m.month_end, INTERVAL 1 DAY)),
                    GREATEST(b.check_in_date, m.month_start)
                )
                ELSE 0
            END
        ), 0
    ) AS occupied_room_nights,

    COALESCE(
        SUM(
            CASE
                WHEN b.booking_id IS NOT NULL
                THEN
                    b.nightly_rate *
                    DATEDIFF(
                        LEAST(b.check_out_date, DATE_ADD(m.month_end, INTERVAL 1 DAY)),
                        GREATEST(b.check_in_date, m.month_start)
                    )
                ELSE 0
            END
        ), 0
    ) AS room_revenue,

    ROUND(
        COALESCE(
            SUM(
                CASE
                    WHEN b.booking_id IS NOT NULL
                    THEN DATEDIFF(
                        LEAST(b.check_out_date, DATE_ADD(m.month_end, INTERVAL 1 DAY)),
                        GREATEST(b.check_in_date, m.month_start)
                    )
                    ELSE 0
                END
            ), 0
        ) * 100.0 /
        NULLIF(
            COUNT(DISTINCT r.room_id) *
            (DATEDIFF(m.month_end, m.month_start) + 1),
            0
        ), 2
    ) AS occupancy_rate,

    ROUND(
        COALESCE(SUM(
            CASE
                WHEN b.booking_id IS NOT NULL
                THEN b.nightly_rate *
                    DATEDIFF(
                        LEAST(b.check_out_date, DATE_ADD(m.month_end, INTERVAL 1 DAY)),
                        GREATEST(b.check_in_date, m.month_start)
                    )
                ELSE 0
            END
        ), 0) /
        NULLIF(
            SUM(
                CASE
                    WHEN b.booking_id IS NOT NULL
                    THEN DATEDIFF(
                        LEAST(b.check_out_date, DATE_ADD(m.month_end, INTERVAL 1 DAY)),
                        GREATEST(b.check_in_date, m.month_start)
                    )
                    ELSE 0
                END
            ), 0
        ), 2
    ) AS ADR,

    ROUND(
        COALESCE(SUM(
            CASE
                WHEN b.booking_id IS NOT NULL
                THEN b.nightly_rate *
                    DATEDIFF(
                        LEAST(b.check_out_date, DATE_ADD(m.month_end, INTERVAL 1 DAY)),
                        GREATEST(b.check_in_date, m.month_start)
                    )
                ELSE 0
            END
        ), 0) /
        NULLIF(
            COUNT(DISTINCT r.room_id) *
            (DATEDIFF(m.month_end, m.month_start) + 1),
            0
        ), 2
    ) AS RevPAR

FROM hotels h

CROSS JOIN dim_months m

JOIN rooms r
    ON h.hotel_id = r.hotel_id
    AND r.is_active = TRUE

LEFT JOIN bookings b
    ON r.room_id = b.room_id
    AND b.booking_status = 'Completed'
    AND b.check_in_date <= m.month_end
    AND b.check_out_date > m.month_start

GROUP BY
    h.hotel_id,
    h.hotel_name,
    m.month_start,
    m.month_end;

ALTER TABLE agg_hotel_monthly_performance
ADD PRIMARY KEY (hotel_id, month_start);


-- Guest satisfaction aggregation

CREATE TABLE agg_guest_satisfaction AS

SELECT
    h.hotel_id,
    h.hotel_name,
    m.month_start,

    COUNT(f.feedback_id) AS total_feedback,

    ROUND(AVG(f.rating), 2) AS avg_satisfaction_score,

    SUM(CASE WHEN f.rating >= 4 THEN 1 ELSE 0 END)
        AS positive_feedback,

    ROUND(
        SUM(CASE WHEN f.rating >= 4 THEN 1 ELSE 0 END)
        * 100.0 / NULLIF(COUNT(f.feedback_id), 0),
        2
    ) AS positive_feedback_rate

FROM hotels h

CROSS JOIN dim_months m

LEFT JOIN rooms r
    ON h.hotel_id = r.hotel_id

LEFT JOIN bookings b
    ON r.room_id = b.room_id

LEFT JOIN guest_feedback f
    ON b.booking_id = f.booking_id
    AND f.feedback_date BETWEEN m.month_start AND m.month_end

GROUP BY
    h.hotel_id,
    h.hotel_name,
    m.month_start;

ALTER TABLE agg_guest_satisfaction
ADD PRIMARY KEY (hotel_id, month_start);

-- Employee turnover aggregation


CREATE TABLE agg_employee_turnover AS

SELECT
    h.hotel_id,
    h.hotel_name,
    m.month_start,

    SUM(
        CASE
            WHEN e.hire_date < m.month_start
            AND (
                e.termination_date IS NULL
                OR e.termination_date >= m.month_start
            )
            THEN 1 ELSE 0
        END
    ) AS opening_headcount,

    SUM(
        CASE
            WHEN e.hire_date <= m.month_end
            AND (
                e.termination_date IS NULL
                OR e.termination_date > m.month_end
            )
            THEN 1 ELSE 0
        END
    ) AS closing_headcount,

    SUM(
        CASE
            WHEN e.termination_date
                BETWEEN m.month_start AND m.month_end
            THEN 1 ELSE 0
        END
    ) AS employees_exited,

    ROUND(
        (
            SUM(
                CASE
                    WHEN e.hire_date < m.month_start
                    AND (
                        e.termination_date IS NULL
                        OR e.termination_date >= m.month_start
                    )
                    THEN 1 ELSE 0
                END
            )
            +
            SUM(
                CASE
                    WHEN e.hire_date <= m.month_end
                    AND (
                        e.termination_date IS NULL
                        OR e.termination_date > m.month_end
                    )
                    THEN 1 ELSE 0
                END
            )
        ) / 2.0,
        2
    ) AS avg_headcount,

    ROUND(
        SUM(
            CASE
                WHEN e.termination_date
                    BETWEEN m.month_start AND m.month_end
                THEN 1 ELSE 0
            END
        ) * 100.0 /
        NULLIF(
            (
                SUM(
                    CASE
                        WHEN e.hire_date < m.month_start
                        AND (
                            e.termination_date IS NULL
                            OR e.termination_date >= m.month_start
                        )
                        THEN 1 ELSE 0
                    END
                )
                +
                SUM(
                    CASE
                        WHEN e.hire_date <= m.month_end
                        AND (
                            e.termination_date IS NULL
                            OR e.termination_date > m.month_end
                        )
                        THEN 1 ELSE 0
                    END
                )
            ) / 2.0,
            0
        ),
        2
    ) AS turnover_rate

FROM hotels h

CROSS JOIN dim_months m

LEFT JOIN employees e
    ON h.hotel_id = e.hotel_id

GROUP BY
    h.hotel_id,
    h.hotel_name,
    m.month_start;

ALTER TABLE agg_employee_turnover
ADD PRIMARY KEY (hotel_id, month_start);



