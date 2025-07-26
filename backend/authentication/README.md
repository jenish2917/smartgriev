# Authentication API Documentation

## Base URL
`/api/auth/`

## Endpoints

### 1. User Registration
- **URL:** `register/`
- **Method:** `POST`
- **Auth Required:** No
- **Request Body:**
```json
{
    "username": "string",
    "password": "string",
    "confirm_password": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "mobile": "string",
    "address": "string",
    "language": "string",
    "is_officer": "boolean"
}
```
- **Success Response:** `201 CREATED`
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "mobile": "string",
    "address": "string",
    "language": "string",
    "is_officer": "boolean"
}
```

### 2. User Login
- **URL:** `login/`
- **Method:** `POST`
- **Auth Required:** No
- **Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```
- **Success Response:** `200 OK`
```json
{
    "access": "string",
    "refresh": "string",
    "user_id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "is_officer": "boolean",
    "language": "string"
}
```

### 3. User Profile
- **URL:** `profile/`
- **Method:** `GET`, `PATCH`
- **Auth Required:** Yes (Bearer Token)
- **Headers:**
```
Authorization: Bearer <access_token>
```
- **GET Response:** `200 OK`
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "mobile": "string",
    "address": "string",
    "language": "string",
    "is_officer": "boolean"
}
```
- **PATCH Request Body:** (all fields optional)
```json
{
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "mobile": "string",
    "address": "string",
    "language": "string"
}
```

### 4. Change Password
- **URL:** `change-password/`
- **Method:** `PUT`
- **Auth Required:** Yes (Bearer Token)
- **Headers:**
```
Authorization: Bearer <access_token>
```
- **Request Body:**
```json
{
    "old_password": "string",
    "new_password": "string",
    "confirm_new_password": "string"
}
```
- **Success Response:** `200 OK`
```json
{
    "message": "Password updated successfully."
}
```

### 5. Token Refresh
- **URL:** `/api/token/refresh/`
- **Method:** `POST`
- **Auth Required:** No
- **Request Body:**
```json
{
    "refresh": "string"
}
```
- **Success Response:** `200 OK`
```json
{
    "access": "string"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "field_name": [
        "error message"
    ]
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

## Password Requirements
- Minimum 8 characters
- Must include uppercase and lowercase letters
- Must include at least one number
- Must include at least one special character

## Language Codes
Available language codes:
- `en` - English
- `hi` - Hindi
- `gu` - Gujarati

## Token Usage
1. After login, store the access and refresh tokens securely
2. Include the access token in the Authorization header for protected endpoints:
   ```
   Authorization: Bearer <access_token>
   ```
3. When the access token expires, use the refresh token to get a new access token
4. If the refresh token expires, user needs to login again

## Security Notes
1. All endpoints use HTTPS in production
2. Passwords are hashed using Django's default PBKDF2 algorithm
3. JWT tokens are signed with HS256
4. Access tokens expire after 60 minutes
5. Refresh tokens expire after 24 hours
