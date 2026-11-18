# Danwa Hotel Table Reservation System

## 1. Project Overview

The Danwa Hotel Table Reservation System is a backend application developed using Django and Django REST Framework with PostgreSQL as its database.

The application provides REST APIs for managing restaurants, dining tables, customer reservations, table availability, reservation approvals, cancellations, table assignments, and notifications.

Customers can create reservations at restaurants, check available dining tables, and manage their own bookings. Restaurant managers can approve or reject reservations and manage dining table assignments.

The system includes reservation validation, restaurant operating-hour validation, table capacity checking, and prevention of overlapping confirmed reservations.

## 2. Technologies Used


| Technology | Version / Details |
|---|---|
| Python | 3.12 |
| Django | 6.1.3 |
| Django REST Framework | 3.18.3 |
| PostgreSQL | Database |
| psycopg | 3.3.8 |
| SQL | Database queries |

## 3. Project Structure

```text
danwa_hotel_table_reservation/
│
├── danwa_backend/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── shops/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── reservations/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── availability.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── notifications/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 4. Project Applications

### 4.1 Shops Application

The Shops application manages restaurant information and dining table details.

**Functionalities:**

- Restaurant management
- Dining table management
- Table capacity management
- Restaurant operating hours
- Restaurant staff management
- Manager and staff role management
- Active and inactive restaurant/table status

**Models:**

- Shop
- DiningTable
- ShopOperatingHours
- ShopStaff

### 4.2 Reservations Application

The Reservations application manages customer table bookings.

**Functionalities:**

- Create customer reservations
- Retrieve reservation details
- List customer reservations
- Check table availability
- Validate reservation details
- Validate restaurant operating hours
- Check dining table capacity
- Prevent overlapping confirmed reservations
- Approve reservations
- Reject reservations
- Cancel reservations
- Assign dining tables

**Models:**

- Reservation
- ReservationTable

### 4.3 Notifications Application

The Notifications application manages reservation-related notifications.

**Functionalities:**

- Booking received notifications
- Booking confirmation notifications
- Booking rejection notifications
- Booking cancellation notifications
- Notification delivery status tracking
- Notification read status tracking

**Model:**

- Notification

## 5. Database Configuration

The application uses PostgreSQL as its database.

| Configuration | Value |
|---|---|
| Database engine | PostgreSQL |
| Database name | danwa_hotel_reservation_db |
| Database user | postgres |
| Host | localhost |
| Port | 5432 |
| Time zone | Asia/Kolkata |

The database connection is configured in:

`danwa_backend/settings.py`

Create the PostgreSQL database before running migrations.

Keep database credentials and Django secret keys private. Do not commit sensitive configuration to GitHub.

## 6. Database Design

The application contains seven custom database models across three Django applications.

### 6.1 Shop

Stores restaurant information.

| Field | Description |
|---|---|
| id | Primary key |
| shop_name | Restaurant name |
| address | Restaurant address |
| city | Restaurant city |
| phone | Optional restaurant phone number |
| is_active | Restaurant active status |
| created_at | Creation timestamp |
| last_update | Last modification timestamp |

### 6.2 DiningTable

Stores restaurant dining table information.

| Field | Description |
|---|---|
| id | Primary key |
| shop | Foreign key to Shop |
| table_number | Table identifier |
| capacity | Maximum seating capacity |
| is_active | Table active status |
| created_at | Creation timestamp |

**Constraint:** `unique_table_number_per_shop`

Ensures that table numbers are unique within each restaurant.

### 6.3 ShopOperatingHours

Stores restaurant opening and closing times.

| Field | Description |
|---|---|
| id | Primary key |
| shop | Foreign key to Shop |
| weekday | Day of the week |
| opening_time | Restaurant opening time |
| closing_time | Restaurant closing time |
| is_closed | Restaurant closed status |

**Constraint:** `unique_shop_weekday`

Ensures that a shop has only one operating-hours record for each weekday.

### 6.4 ShopStaff

Stores restaurant staff assignments.

| Field | Description |
|---|---|
| id | Primary key |
| shop | Foreign key to Shop |
| user | Foreign key to Django User |
| role | MANAGER or STAFF |
| is_active | Staff active status |
| created_at | Creation timestamp |

**Constraint:** `unique_active_staff_per_shop`

Prevents duplicate active staff assignments for the same user and restaurant.

### 6.5 Reservation

Stores customer reservation information.

| Field | Description |
|---|---|
| id | Primary key |
| booking_code | Unique reservation reference |
| shop | Foreign key to Shop |
| user | Foreign key to Django User |
| reservation_date | Reservation date |
| start_time | Reservation start time |
| duration_minutes | Reservation duration |
| guests | Number of guests |
| customer_name | Customer name |
| customer_phone | Customer mobile number |
| special_request | Optional customer request |
| status | Reservation status |
| cancellation_reason | Cancellation reason |
| confirmed_at | Confirmation timestamp |
| cancelled_at | Cancellation timestamp |
| created_at | Creation timestamp |
| last_update | Last modification timestamp |

**Reservation statuses:**

- PENDING
- CONFIRMED
- REJECTED
- CANCELLED
- COMPLETED
- NO_SHOW

**Database constraints:**

- `reservation_guests_gt_zero`
- `reservation_duration_gt_zero`
- Unique booking code

### 6.6 ReservationTable

Stores reservation and dining table assignments.

| Field | Description |
|---|---|
| id | Primary key |
| reservation | Foreign key to Reservation |
| dining_table | Foreign key to DiningTable |
| created_at | Assignment timestamp |

**Constraint:** `unique_reservation_table_assignment`

Ensures that each reservation can have at most one dining table assignment.

### 6.7 Notification

Stores reservation-related notification information.

| Field | Description |
|---|---|
| id | Primary key |
| reservation | Foreign key to Reservation |
| notification_type | Notification type |
| delivery_channel | Delivery method |
| delivery_status | Delivery status |
| message | Notification message |
| is_read | Read status |
| read_at | Read timestamp |
| created_at | Creation timestamp |
| sent_at | Sent timestamp |

**Notification types:**

- BOOKING_RECEIVED
- BOOKING_CONFIRMED
- BOOKING_REJECTED
- BOOKING_CANCELLED
- BOOKING_MODIFIED
- BOOKING_REMINDER

**Delivery channels:**

- IN_APP
- SMS
- EMAIL
- PUSH

**Delivery statuses:**

- PENDING
- SENT
- FAILED

## 7. Database Relationships

| Parent Model | Related Model | Relationship |
|---|---|---|
| Shop | DiningTable | One-to-many |
| Shop | ShopOperatingHours | One-to-many |
| Shop | ShopStaff | One-to-many |
| Shop | Reservation | One-to-many |
| Django User | ShopStaff | One-to-many |
| Django User | Reservation | One-to-many |
| Reservation | ReservationTable | One-to-zero-or-one |
| DiningTable | ReservationTable | One-to-many |
| Reservation | Notification | One-to-many |

All listed foreign-key relationships use `on_delete=models.CASCADE`.

A reservation can exist without a table assignment while pending. Each reservation can have at most one table assignment.

## 8. Reservation Business Logic and Validation

### 8.1 Reservation Input Validation

The system validates:

- Required reservation fields
- Valid reservation date and time
- Positive guest count
- Positive reservation duration
- Valid customer phone number
- Valid restaurant
- Active restaurant status
- Restaurant operating hours
- Future reservation date and time

### 8.2 Customer Phone Validation

The customer phone number must:

- Contain exactly 10 digits.
- Start with 6, 7, 8, or 9.
- Contain digits only.

Invalid phone numbers are rejected by serializer validation.

### 8.3 Table Capacity Validation

The system selects active dining tables belonging to the requested restaurant whose capacity is greater than or equal to the requested guest count.

For example:

- Guests: 4
- Table T01 capacity: 4
- Table T02 capacity: 6

Both tables satisfy the capacity requirement.

### 8.4 Restaurant Operating Hours

Reservations are accepted only when:

- The restaurant is active.
- Operating hours exist for the requested weekday.
- The restaurant is not closed on that weekday.
- The requested start time is not before opening time.
- The requested end time does not exceed closing time.

### 8.5 Table Availability

The system checks existing confirmed reservations and identifies dining tables that are not occupied during the requested reservation period.

Pending, rejected, and cancelled reservations do not block tables in the confirmed-reservation availability check.

### 8.6 Overlapping Reservation Prevention

The system prevents two confirmed reservations from using the same dining table during overlapping time periods.

The overlap condition is:

`requested_start < existing_end AND requested_end > existing_start`

This allows reservations to use the same table when their time periods do not overlap.

### 8.7 Table Selection and Assignment

The system follows a single-table assignment strategy.

- One reservation can have at most one dining table.
- Combined table assignments are not supported.
- The table must have sufficient capacity.
- The table must be active and belong to the same restaurant.
- The smallest suitable available table is selected first during approval.
- Table availability is checked again during approval.

### 8.8 Reservation Status Management

The system supports:

- PENDING
- CONFIRMED
- REJECTED
- CANCELLED
- COMPLETED
- NO_SHOW

Only pending reservations can be approved or rejected.

Customers can cancel their own eligible reservations. Reservations that are already cancelled, completed, rejected, or marked as no-show cannot be cancelled through the cancellation API.

## 9. Reservation API Documentation

**API Base URL:**

`http://127.0.0.1:8000/api/`

All reservation APIs use the `/api/reservations/` URL prefix.

### 9.1 API Endpoint Summary

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/api/reservations/` | List reservations | Authenticated customer |
| POST | `/api/reservations/` | Create reservation | Authenticated customer |
| GET | `/api/reservations/{id}/` | Retrieve reservation details | Reservation owner |
| POST | `/api/reservations/{id}/cancel/` | Cancel reservation | Reservation owner |
| POST | `/api/reservations/{id}/approve/` | Approve reservation | Shop manager |
| POST | `/api/reservations/{id}/reject/` | Reject reservation | Shop manager |
| POST | `/api/reservations/{reservation_id}/assign-table/` | Assign dining table | Active shop manager |
| GET | `/api/reservations/availability/` | Check available tables | Public |

### 9.2 Reservation List API

**Endpoint:**

`GET /api/reservations/`

Returns reservations belonging to the authenticated customer.

**Optional query parameters:**

| Parameter | Description |
|---|---|
| shop_id | Filter reservations by restaurant |
| reservation_date | Filter reservations by date |

**Example:**

`GET /api/reservations/?shop_id=2`

**Combined filters:**

`GET /api/reservations/?shop_id=2&reservation_date=2026-11-23`

**Success response:** HTTP 200 OK.

### 9.3 Create Reservation API

**Endpoint:**

`POST /api/reservations/`

**Example request:**

```json
{
    "shop": 2,
    "reservation_date": "2026-11-23",
    "start_time": "18:00:00",
    "duration_minutes": 90,
    "guests": 4,
    "customer_name": "Arun Kumar",
    "customer_phone": "9876543210",
    "special_request": "Window seating preferred"
}
```

**Field descriptions:**

| Field | Description |
|---|---|
| shop | Restaurant ID |
| reservation_date | Reservation date |
| start_time | Reservation start time |
| duration_minutes | Reservation duration |
| guests | Number of guests |
| customer_name | Customer name |
| customer_phone | Valid 10-digit Indian mobile number |
| special_request | Optional special request |

The following fields are generated or assigned automatically:

- `id`
- `booking_code`
- `user`
- `status`
- `cancellation_reason`
- `confirmed_at`
- `cancelled_at`
- `created_at`
- `last_update`

The authenticated user is assigned automatically.

The booking code is generated in the format `RES-` followed by 12 uppercase hexadecimal characters.

The initial reservation status is `PENDING`.

**Success response:** HTTP 201 Created.

**Example response:**

```json
{
    "id": 25,
    "booking_code": "RES-XXXXXXXXXXXX",
    "shop": 2,
    "user": 1,
    "reservation_date": "2026-11-23",
    "start_time": "18:00:00",
    "duration_minutes": 90,
    "guests": 4,
    "customer_name": "Arun Kumar",
    "customer_phone": "9876543210",
    "special_request": "Window seating preferred",
    "status": "PENDING",
    "cancellation_reason": null,
    "confirmed_at": null,
    "cancelled_at": null,
    "created_at": "2026-11-18T10:00:00Z",
    "last_update": "2026-11-18T10:00:00Z"
}
```

The response values are illustrative examples, not actual database records.

### 9.4 Reservation Detail API

**Endpoint:**

`GET /api/reservations/{id}/`

**Example:**

`GET /api/reservations/23/`

Retrieves reservation details for the authenticated reservation owner.

**Success response:** HTTP 200 OK.

Users cannot retrieve another customer's reservation through this endpoint.

### 9.5 Reservation Cancellation API

**Endpoint:**

`POST /api/reservations/{id}/cancel/`

**Example:**

`POST /api/reservations/23/cancel/`

**Example request:**

```json
{
    "cancellation_reason": "Change of plans"
}
```

The cancellation reason is optional.

**Success response:** HTTP 200 OK.

The system:

1. Checks reservation ownership.
2. Checks whether cancellation is permitted.
3. Changes the status to CANCELLED.
4. Stores the cancellation reason.
5. Updates the cancellation timestamp.
6. Creates a BOOKING_CANCELLED notification.

**Example response:**

```json
{
    "id": 23,
    "booking_code": "RES-XXXXXXXXXXXX",
    "status": "CANCELLED",
    "cancellation_reason": "Change of plans"
}
```

The example shows selected response fields for illustration; the actual serializer returns all its declared fields.

### 9.6 Reservation Approval API

**Endpoint:**

`POST /api/reservations/{id}/approve/`

**Example:**

`POST /api/reservations/23/approve/`

No request body is required.

Only an authorized shop manager can approve a pending reservation.

The system:

1. Locks the reservation within a database transaction.
2. Checks manager permissions.
3. Verifies that the reservation is PENDING.
4. Checks available dining tables.
5. Locks candidate tables during availability checking.
6. Selects the smallest suitable available table.
7. Changes the reservation status to CONFIRMED.
8. Saves the confirmation timestamp.
9. Creates the reservation-table assignment.
10. Creates a BOOKING_CONFIRMED notification.

**Success response:** HTTP 200 OK.

The response contains reservation fields and an additional `assigned_table` object.

**Example response:**

```json
{
    "id": 23,
    "booking_code": "RES-XXXXXXXXXXXX",
    "status": "CONFIRMED",
    "assigned_table": {
        "id": 1,
        "table_number": "T01",
        "capacity": 4
    }
}
```

If no suitable table is available, the API returns HTTP 409 Conflict.

If the reservation is not pending, the API returns HTTP 400 Bad Request.

### 9.7 Reservation Rejection API

**Endpoint:**

`POST /api/reservations/{id}/reject/`

**Example:**

`POST /api/reservations/23/reject/`

No request body is required.

Only an authorized shop manager can reject a pending reservation.

The system:

1. Retrieves the reservation.
2. Checks manager permissions.
3. Verifies that the reservation is PENDING.
4. Changes the status to REJECTED.
5. Creates a BOOKING_REJECTED notification.

**Success response:** HTTP 200 OK.

If the reservation is not pending, the API returns HTTP 400 Bad Request.

### 9.8 Reservation Table Assignment API

**Endpoint:**

`POST /api/reservations/{reservation_id}/assign-table/`

**Example:**

`POST /api/reservations/23/assign-table/`

**Example request:**

```json
{
    "dining_table": 1
}
```

The system validates:

- The authenticated user is an active manager of the reservation's shop.
- The reservation is CONFIRMED.
- The dining table is active.
- The dining table belongs to the same restaurant.
- The dining table has sufficient seating capacity.
- The reservation does not already have an assignment.
- The selected table does not have an overlapping confirmed reservation.

**Success response:** HTTP 201 Created.

**Example response:**

```json
{
    "id": 10,
    "reservation": 23,
    "dining_table": 1,
    "created_at": "2026-11-18T10:00:00Z"
}
```

The approval API already assigns a table automatically. Therefore, this separate endpoint is intended for confirmed reservations that do not yet have an assignment.

### 9.9 Reservation Availability API

**Endpoint:**

`GET /api/reservations/availability/`

**Example request:**

`GET /api/reservations/availability/?shop_id=2&reservation_date=2026-11-23&start_time=18:00&guests=4&duration_minutes=90`

**Required query parameters:**

| Parameter | Description |
|---|---|
| shop_id | Restaurant ID |
| reservation_date | Date in YYYY-MM-DD format |
| start_time | Time in HH:MM format |
| guests | Number of guests |
| duration_minutes | Reservation duration; defaults to 90 |

**Example response:**

```json
{
    "shop_id": 2,
    "reservation_date": "2026-11-23",
    "start_time": "18:00:00",
    "guests": 4,
    "duration_minutes": 90,
    "available_tables": [
        {
            "id": 1,
            "table_number": "T01",
            "capacity": 4
        },
        {
            "id": 2,
            "table_number": "T02",
            "capacity": 6
        }
    ]
}
```

The API checks:

- Restaurant active status
- Restaurant operating hours
- Reservation date and time
- Number of guests
- Reservation duration
- Active dining tables
- Table capacity
- Existing overlapping confirmed reservations

When the restaurant is closed or the requested time is outside operating hours, the API returns HTTP 200 with an empty `available_tables` list.

## 10. Authentication and Permissions

The application uses Django REST Framework authentication and custom permission classes.

Access is controlled according to the operation and the authenticated user's relationship with the restaurant.

- Customers can list their own reservations.
- Customers can create reservations.
- Customers can retrieve their own reservation details.
- Customers can cancel their own eligible reservations.
- Customers cannot approve or reject reservations.
- Authorized restaurant managers can approve reservations.
- Authorized restaurant managers can reject reservations.
- Active managers can assign dining tables.
- Availability checking is accessible without authentication.

## 11. Notifications

Notifications are created for reservation-related events.

| Event | Notification Type |
|---|---|
| Reservation created | BOOKING_RECEIVED |
| Reservation approved | BOOKING_CONFIRMED |
| Reservation rejected | BOOKING_REJECTED |
| Reservation cancelled | BOOKING_CANCELLED |

The notification model also defines the following delivery channels:

- IN_APP
- SMS
- EMAIL
- PUSH

And delivery statuses:

- PENDING
- SENT
- FAILED

The model stores delivery and read-status information. External SMS, email, and push delivery integrations are not established by the reservation views documented here.

## 12. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
```

Navigate into the project directory:

```bash
cd danwa_hotel_table_reservation
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Create PostgreSQL Database

Create a database named:

```text
danwa_hotel_reservation_db
```

Make sure PostgreSQL is running and the database connection is configured correctly.

### Step 6: Configure Django Settings

Configure the PostgreSQL connection and required private settings in:

```text
danwa_backend/settings.py
```

Do not expose secret keys or database credentials in a public repository.

### Step 7: Apply Database Migrations

```bash
python manage.py migrate
```

### Step 8: Create a Django Superuser

```bash
python manage.py createsuperuser
```

### Step 9: Start the Development Server

```bash
python manage.py runserver
```

The application will run at:

`http://127.0.0.1:8000/`

The Django administration panel is available at:

`http://127.0.0.1:8000/admin/`

## 13. Testing

Run all automated tests:

```bash
python manage.py test
```

Run reservation application tests:

```bash
python manage.py test reservations
```

Check Django configuration:

```bash
python manage.py check
```

Check whether model changes require migrations:

```bash
python manage.py makemigrations --check --dry-run
```

Show migration status:

```bash
python manage.py showmigrations
```

The project includes automated tests for reservation availability and database constraints.

## 14. Git and Repository Management

The project uses Git for version control.

The `.gitignore` file excludes unnecessary files such as:

- Python virtual environments
- Python cache files
- SQLite local database files
- Environment variable files
- IDE configuration files
- Generated static files
- Local project structure reports

The `requirements.txt` file contains the Python dependencies required to set up the project.

## 15. Security Considerations

- Keep Django secret keys private.
- Do not commit database passwords or credentials.
- Do not upload `.env` files.
- Do not upload the Python virtual environment.
- Disable Django debug mode before production deployment.
- Configure appropriate allowed hosts and production security settings.
- Use secure database credentials in production.

## 16. Project Status

The core backend implementation includes:

- Restaurant and dining table management
- Restaurant operating hours
- Staff and manager management
- Customer reservation management
- Reservation input validation
- Table availability checking
- Overlapping booking prevention
- Reservation approval and rejection
- Reservation cancellation
- Dining table assignment
- Reservation notifications
- Automated testing

## 17. Future Enhancements

Potential future improvements include:

- Online payment integration
- SMS and email notification delivery
- Push notifications
- Reservation modification
- Customer booking history
- Restaurant analytics and reports
- Production deployment and monitoring

---

**Project:** Danwa Hotel Table Reservation System

**Backend Framework:** Django REST Framework

**Database:** PostgreSQL