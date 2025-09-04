# SmartStay Hostel Management System - API Documentation

## Overview
The SmartStay Hostel Management System provides a comprehensive REST API for managing hostel operations including student management, room allocation, payments, complaints, and more.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### 1. User Management

#### Register User
```
POST /api/register/
```
**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword",
    "password_confirm": "securepassword",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890",
    "date_of_birth": "2000-01-01",
    "address": "123 Main St",
    "emergency_contact": "9876543210",
    "role": "student"
}
```

#### Get Current User
```
GET /api/users/me/
```

#### Get All Users
```
GET /api/users/
```
**Query Parameters:**
- `role`: Filter by role (student, admin, warden)
- `is_active`: Filter by active status
- `search`: Search by username, first_name, last_name, email
- `ordering`: Order by created_at, username

#### Get Students
```
GET /api/users/students/
```

### 2. Room Management

#### Get All Rooms
```
GET /api/rooms/
```
**Query Parameters:**
- `room_type`: Filter by room type (single, double, triple, quad)
- `status`: Filter by status (available, occupied, maintenance)
- `floor`: Filter by floor number
- `search`: Search by room number, description
- `ordering`: Order by number, monthly_rent, created_at

#### Get Available Rooms
```
GET /api/rooms/available/
```

#### Get Room Statistics
```
GET /api/rooms/stats/
```
**Response:**
```json
{
    "total_rooms": 50,
    "available_rooms": 30,
    "occupied_rooms": 18,
    "maintenance_rooms": 2,
    "occupancy_rate": 36.0
}
```

#### Create Room
```
POST /api/rooms/
```
**Request Body:**
```json
{
    "number": "101",
    "capacity": 2,
    "floor": 1,
    "room_type": "double",
    "monthly_rent": 5000.00,
    "amenities": "WiFi, AC, Study Table",
    "description": "Spacious double room with modern amenities"
}
```

### 3. Attendance Management

#### Get Attendance Records
```
GET /api/attendance/
```
**Query Parameters:**
- `date`: Filter by specific date
- `present`: Filter by attendance status
- `ordering`: Order by date, marked_at

#### Mark Attendance
```
POST /api/attendance/mark/
```

#### Get Attendance Statistics
```
GET /api/attendance/stats/
```

### 4. Complaint Management

#### Get Complaints
```
GET /api/complaints/
```
**Query Parameters:**
- `status`: Filter by status (open, in_progress, resolved)
- `room`: Filter by room ID
- `search`: Search by title, description
- `ordering`: Order by created_at, status

#### Create Complaint
```
POST /api/complaints/
```
**Request Body:**
```json
{
    "room": 1,
    "title": "Broken AC",
    "description": "The air conditioner in room 101 is not working properly"
}
```

#### Update Complaint Status
```
PATCH /api/complaints/{id}/update_status/
```
**Request Body:**
```json
{
    "status": "in_progress"
}
```

### 5. Payment Management

#### Get Payments
```
GET /api/payments/
```
**Query Parameters:**
- `status`: Filter by status (pending, success, failed, refunded)
- `payment_type`: Filter by payment type (rent, security, maintenance, penalty, other)
- `ordering`: Order by created_at, amount, due_date

#### Create Payment Order
```
POST /api/payments/create_order/
```
**Request Body:**
```json
{
    "amount": 5000.00,
    "payment_type": "rent",
    "description": "Monthly rent for January 2024"
}
```

#### Get Pending Payments
```
GET /api/payments/pending/
```

#### Get Payment Statistics
```
GET /api/payments/stats/
```

### 6. Feedback Management

#### Get Feedback
```
GET /api/feedback/
```
**Query Parameters:**
- `rating`: Filter by rating (1-5)
- `ordering`: Order by created_at, rating

#### Create Feedback
```
POST /api/feedback/
```
**Request Body:**
```json
{
    "rating": 5,
    "comments": "Great hostel with excellent facilities",
    "category": "general",
    "is_anonymous": false
}
```

#### Get Feedback Statistics
```
GET /api/feedback/stats/
```

### 7. Room Allocation

#### Get Room Allocations
```
GET /api/allocations/
```
**Query Parameters:**
- `status`: Filter by status (active, inactive, terminated)
- `room`: Filter by room ID
- `ordering`: Order by start_date, created_at

#### Get Active Allocations
```
GET /api/allocations/active/
```

#### Create Room Allocation
```
POST /api/allocations/
```
**Request Body:**
```json
{
    "user": 1,
    "room": 1,
    "start_date": "2024-01-01",
    "monthly_rent": 5000.00,
    "security_deposit": 10000.00
}
```

### 8. Notice Management

#### Get Notices
```
GET /api/notices/
```
**Query Parameters:**
- `priority`: Filter by priority (low, medium, high, urgent)
- `target_audience`: Filter by target audience (student, admin, warden, all)
- `is_active`: Filter by active status
- `search`: Search by title, content
- `ordering`: Order by created_at, priority

#### Create Notice
```
POST /api/notices/
```
**Request Body:**
```json
{
    "title": "Hostel Rules Update",
    "content": "Please note the updated hostel rules...",
    "priority": "high",
    "target_audience": "student"
}
```

### 9. Maintenance Management

#### Get Maintenance Requests
```
GET /api/maintenance/
```
**Query Parameters:**
- `status`: Filter by status (pending, in_progress, completed, cancelled)
- `priority`: Filter by priority (low, medium, high, urgent)
- `room`: Filter by room ID
- `search`: Search by title, description
- `ordering`: Order by created_at, priority

#### Create Maintenance Request
```
POST /api/maintenance/
```
**Request Body:**
```json
{
    "room": 1,
    "title": "Plumbing Issue",
    "description": "Water leakage in bathroom",
    "priority": "high"
}
```

#### Assign Maintenance Request
```
PATCH /api/maintenance/{id}/assign/
```
**Request Body:**
```json
{
    "assigned_to": 2
}
```

### 10. Dashboard Statistics

#### Get Dashboard Statistics
```
GET /api/dashboard/stats/
```
**Response:**
```json
{
    "total_students": 150,
    "total_rooms": 50,
    "occupied_rooms": 18,
    "available_rooms": 30,
    "pending_payments": 5,
    "pending_complaints": 3,
    "pending_maintenance": 2,
    "monthly_revenue": 90000.00
}
```

## Error Responses

### 400 Bad Request
```json
{
    "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "detail": "A server error occurred."
}
```

## Pagination

Most list endpoints support pagination:
```
GET /api/rooms/?page=2&page_size=20
```

**Response:**
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/rooms/?page=3",
    "previous": "http://localhost:8000/api/rooms/?page=1",
    "results": [...]
}
```

## Filtering and Searching

### Filtering
Use query parameters to filter results:
```
GET /api/rooms/?room_type=double&status=available&floor=1
```

### Searching
Use the `search` parameter for text search:
```
GET /api/users/?search=john
```

### Ordering
Use the `ordering` parameter to sort results:
```
GET /api/rooms/?ordering=-monthly_rent
```

## File Uploads

For endpoints that accept file uploads (like profile pictures), use `multipart/form-data`:
```
POST /api/users/{id}/
Content-Type: multipart/form-data

{
    "profile_picture": <file>
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:
- 1000 requests per hour for authenticated users
- 100 requests per hour for anonymous users

## Webhooks

The system supports webhooks for real-time notifications:
- Payment status updates
- Complaint status changes
- Maintenance request assignments

## SDKs and Libraries

### Python
```python
import requests

# Get authentication token
response = requests.post('http://localhost:8000/api/token/', {
    'username': 'your_username',
    'password': 'your_password'
})
token = response.json()['access']

# Make authenticated request
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/rooms/', headers=headers)
```

### JavaScript
```javascript
// Get authentication token
const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});
const {access} = await response.json();

// Make authenticated request
const roomsResponse = await fetch('http://localhost:8000/api/rooms/', {
    headers: {'Authorization': `Bearer ${access}`}
});
```

## Support

For API support and questions:
- Email: support@smartstay.com
- Documentation: https://docs.smartstay.com
- GitHub: https://github.com/smartstay/api


