
import uuid
import random
import getpass
from datetime import date, timedelta

import pandas as pd
import mysql.connector
from faker import Faker

# --------------------------------------------------
# 1. INITIAL CONFIGURATION
# --------------------------------------------------

random.seed(42)
rng = random.Random(42)

fake = Faker("en_IN")
Faker.seed(42)

START_DATE = date(2021, 1, 1)
END_DATE = date(2025, 12, 31)

def new_id():
    return str(uuid.uuid4())


# --------------------------------------------------
# 2. HOTEL DATA
# --------------------------------------------------

hotel_details = [
    ("Grand Palace", "Chennai", "Tamil Nadu", "Luxury", 0.02),
    ("Ocean View", "Goa", "Goa", "Resort", 0.05),
    ("Royal Heritage", "Jaipur", "Rajasthan", "Luxury", 0.03),
    ("City Comfort", "Bengaluru", "Karnataka", "Business", 0.01),
    ("Mountain Retreat", "Manali", "Himachal Pradesh", "Resort", 0.06),
    ("Lake Residency", "Udaipur", "Rajasthan", "Premium", -0.02),
    ("Green Valley", "Coimbatore", "Tamil Nadu", "Business", 0.04),
    ("Metro Suites", "Hyderabad", "Telangana", "Premium", -0.01)
]

hotels = []
hotel_map = {}

for name, city, state, category, trend in hotel_details:
    hid = new_id()

    hotels.append({
        "hotel_id": hid,
        "hotel_name": name,
        "city": city,
        "state": state,
        "hotel_category": category
    })

    hotel_map[hid] = {
        "city": city,
        "category": category,
        "trend": trend
    }


# --------------------------------------------------
# 3. ROOM DATA
# --------------------------------------------------

rooms = []
room_map = {}

room_types = {
    "Standard": 2500,
    "Deluxe": 4000,
    "Suite": 6500,
    "Executive": 5000
}

for hotel in hotels:
    for i in range(1, 41):
        room_id = new_id()
        room_type = list(room_types.keys())[(i - 1) % 4]
        base_rate = room_types[room_type]

        rooms.append({
            "room_id": room_id,
            "hotel_id": hotel["hotel_id"],
            "room_number": f"{i:03d}",
            "room_type": room_type,
            "base_rate": base_rate,
            "is_active": True
        })

        room_map[room_id] = {
            "hotel_id": hotel["hotel_id"],
            "base_rate": base_rate
        }


# --------------------------------------------------
# 4. GUEST DATA
# --------------------------------------------------

guests = []
guest_ids = []

for _ in range(15000):
    gid = new_id()
    guest_ids.append(gid)

    guests.append({
        "guest_id": gid,
        "guest_name": fake.name(),
        "guest_email": fake.unique.email(),
        "guest_city": fake.city()
    })


# --------------------------------------------------
# 5. BOOKING DATA
# --------------------------------------------------

bookings = []

for room in rooms:

    room_id = room["room_id"]
    hotel_id = room["hotel_id"]

    hotel_info = hotel_map[hotel_id]
    base_rate = room_map[room_id]["base_rate"]
    trend = hotel_info["trend"]
    category = hotel_info["category"]

    next_available = START_DATE

    current_date = START_DATE

    while current_date <= END_DATE:

        # Avoid overlapping completed stays
        if current_date < next_available:
            current_date += timedelta(days=1)
            continue

        month = current_date.month
        year_index = current_date.year - 2021

        # Seasonal demand
        if month in [10, 11, 12, 1]:
            seasonal_factor = 1.35
        elif month in [4, 5, 6]:
            seasonal_factor = 1.10
        elif month in [7, 8, 9]:
            seasonal_factor = 0.75
        else:
            seasonal_factor = 0.95

        # Resort-specific summer and winter demand
        if category == "Resort" and month in [4, 5, 6]:
            seasonal_factor *= 1.15

        # Gradual hotel-specific demand trend
        demand_probability = (
            0.14
            * seasonal_factor
            * (1 + trend * year_index)
        )

        demand_probability = max(
            0.04, min(demand_probability, 0.30)
        )

        if rng.random() < demand_probability:

            nights = rng.choices(
                [1, 2, 3, 4, 5],
                weights=[15, 35, 25, 15, 10]
            )[0]

            checkout = current_date + timedelta(days=nights)

            status = rng.choices(
                ["Completed", "Cancelled", "No Show"],
                weights=[90, 6, 4]
            )[0]

            booking_date = current_date - timedelta(
                days=rng.randint(1, 90)
            )

            # Seasonal pricing
            if month in [10, 11, 12, 1]:
                price_factor = 1.25
            elif month in [7, 8, 9]:
                price_factor = 0.85
            else:
                price_factor = 1.0

            price_factor *= (1 + 0.02 * year_index)

            nightly_rate = round(
                base_rate
                * price_factor
                * rng.uniform(0.90, 1.10),
                2
            )

            bookings.append({
                "booking_id": new_id(),
                "guest_id": rng.choice(guest_ids),
                "room_id": room_id,
                "booking_date": booking_date,
                "check_in_date": current_date,
                "check_out_date": checkout,
                "nightly_rate": nightly_rate,
                "booking_status": status
            })

            # Only completed stays occupy rooms
            if status == "Completed":
                next_available = checkout

        current_date += timedelta(days=1)


# --------------------------------------------------
# 6. EMPLOYEE DATA
# --------------------------------------------------

employees = []

for hotel in hotels:

    for _ in range(65):

        hire_date = fake.date_between(
            start_date=date(2019, 1, 1),
            end_date=END_DATE
        )

        termination_date = None

        if rng.random() < 0.28 and hire_date < END_DATE:

            possible_exit = hire_date + timedelta(
                days=rng.randint(60, 1800)
            )

            if possible_exit <= END_DATE:
                termination_date = possible_exit

        employees.append({
            "employee_id": new_id(),
            "hotel_id": hotel["hotel_id"],
            "employee_name": fake.name(),
            "position": rng.choice([
                "Manager",
                "Receptionist",
                "Housekeeping",
                "Chef",
                "Waiter",
                "Security",
                "Maintenance"
            ]),
            "hire_date": hire_date,
            "termination_date": termination_date,
            "employment_status": (
                "Terminated" if termination_date
                else "Active"
            )
        })


# --------------------------------------------------
# 7. GUEST FEEDBACK DATA
# --------------------------------------------------

feedback = []

for booking in bookings:

    if booking["booking_status"] != "Completed":
        continue

    # Not every guest submits feedback
    if rng.random() > 0.65:
        continue

    hotel_id = room_map[booking["room_id"]]["hotel_id"]
    trend = hotel_map[hotel_id]["trend"]

    month = booking["check_in_date"].month

    # Crowding can affect guest satisfaction
    crowding_penalty = (
        0.25 if month in [10, 11, 12, 1] else 0
    )

    mean_rating = (
        4.1
        + trend * 3
        - crowding_penalty
    )

    rating = round(
        max(1, min(5, rng.gauss(mean_rating, 0.55))),
        2
    )

    feedback.append({
        "feedback_id": new_id(),
        "booking_id": booking["booking_id"],
        "rating": rating,
        "feedback_date": booking["check_out_date"]
                        + timedelta(days=rng.randint(0, 7)),
        "comments": fake.sentence()
    })


# --------------------------------------------------
# 8. CREATE PANDAS DATAFRAMES
# --------------------------------------------------

dataframes = {
    "hotels": pd.DataFrame(hotels),
    "rooms": pd.DataFrame(rooms),
    "guests": pd.DataFrame(guests),
    "employees": pd.DataFrame(employees),
    "bookings": pd.DataFrame(bookings),
    "guest_feedback": pd.DataFrame(feedback)
}

print("\nDATA GENERATION COMPLETED")

for table, df in dataframes.items():
    print(f"{table}: {len(df):,} records")


# --------------------------------------------------
# 9. MYSQL CONNECTION
# --------------------------------------------------

print("\nConnecting to MySQL...")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=getpass.getpass("Enter MySQL password: "),
    database="hospitality_analytics"
)

cursor = connection.cursor()

# Prevent accidental duplicate loading
for table in dataframes:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")

    if cursor.fetchone()[0] > 0:
        raise RuntimeError(
            f"Table {table} is not empty. "
            "Load cancelled to prevent duplicates."
        )


# --------------------------------------------------
# 10. LOAD DATA INTO MYSQL
# --------------------------------------------------

try:

    for table, df in dataframes.items():

        columns = list(df.columns)

        column_names = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        query = (
            f"INSERT INTO {table} "
            f"({column_names}) "
            f"VALUES ({placeholders})"
        )

        rows = [
            tuple(
                None if pd.isna(value) else value
                for value in row
            )
            for row in df.itertuples(index=False, name=None)
        ]

        # Insert in batches
        for i in range(0, len(rows), 1000):
            cursor.executemany(
                query,
                rows[i:i + 1000]
            )

        print(f"Loaded {len(rows):,} records into {table}")

    connection.commit()

    print("\nALL DATA SUCCESSFULLY LOADED!")

except Exception:
    connection.rollback()
    raise

finally:
    cursor.close()
    connection.close()


# --------------------------------------------------
# 11. FINAL SUMMARY
# --------------------------------------------------

print("\nFINAL DATASET SUMMARY")

for table, df in dataframes.items():
    print(f"{table:20s}: {len(df):,}")
