# Labs System API Documentation

## Overview
The Labs System provides a comprehensive platform for external practice environments with points integration, secure redirection, and progress tracking.

## Authentication
All endpoints require authentication unless specified otherwise. Use JWT tokens in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
/api/labs/
```

## Lab Management Endpoints

### 1. List Labs
**GET** `/api/labs/`

Lists all available labs with user-specific context.

**Query Parameters:**
- `category` (string): Filter by lab category
- `difficulty` (string): Filter by difficulty level (beginner, intermediate, advanced, expert)
- `status` (string): Filter by lab status (active, inactive, maintenance)
- `featured` (boolean): Show only featured labs

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/labs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "SQL Injection Basics",
      "description": "Learn fundamental SQL injection techniques",
      "objectives": ["Understand SQL injection", "Practice basic attacks"],
      "category": "web_security",
      "difficulty_level": "beginner",
      "status": "active",
      "lab_url": "https://external-lab.com/sql-basics",
      "estimated_time": 45,
      "max_score": 100,
      "min_score": 70,
      "base_points": 50,
      "bonus_points": 20,
      "cooldown_minutes": 60,
      "max_attempts_per_day": 3,
      "can_attempt": true,
      "user_attempts_count": 2,
      "user_best_score": 85,
      "user_has_passed": true,
      "cooldown_remaining": 0,
      "attempts_today": 1,
      "created_at": "2025-07-07T10:00:00Z"
    }
  ]
}
```

### 2. Get Lab Details
**GET** `/api/labs/{lab_id}/`

Get detailed information about a specific lab.

**Response:**
```json
{
  "id": 1,
  "name": "SQL Injection Basics",
  "description": "Learn fundamental SQL injection techniques",
  "objectives": ["Understand SQL injection", "Practice basic attacks"],
  "category": "web_security",
  "difficulty_level": "beginner",
  "status": "active",
  "lab_url": "https://external-lab.com/sql-basics",
  "external_lab_id": "sql_basic_001",
  "estimated_time": 45,
  "max_score": 100,
  "min_score": 70,
  "perfect_score_bonus": 25,
  "base_points": 50,
  "bonus_points": 20,
  "cooldown_minutes": 60,
  "max_attempts_per_day": 3,
  "requires_prerequisites": false,
  "tags": ["sql", "injection", "web"],
  "is_featured": true,
  "can_attempt": true,
  "user_attempts_count": 2,
  "user_best_score": 85,
  "user_has_passed": true,
  "cooldown_remaining": 0,
  "attempts_today": 1,
  "created_at": "2025-07-07T10:00:00Z",
  "updated_at": "2025-07-07T10:00:00Z"
}
```

### 3. Check Lab Access
**GET** `/api/labs/{lab_id}/access-check/`

Check if the current user can attempt a specific lab.

**Response:**
```json
{
  "can_attempt": true,
  "message": "You can attempt this lab",
  "cooldown_remaining": 0,
  "attempts_today": 1,
  "max_attempts_per_day": 3,
  "prerequisites_met": true,
  "missing_prerequisites": []
}
```

### 4. Start Lab Attempt
**POST** `/api/labs/{lab_id}/start/`

Start a new lab attempt and get secure redirection URL.

**Response:**
```json
{
  "redirect_url": "https://external-lab.com/sql-basics?token=abc123&session=xyz789&user_id=1&lab_id=1",
  "return_url": "http://localhost:8000/api/labs/return/abc123/",
  "session_token": "xyz789",
  "expires_at": "2025-07-07T14:00:00Z",
  "attempt_id": 15,
  "estimated_time": 45
}
```

### 5. Lab Return Handler
**GET/POST** `/api/labs/return/{token}/`

Handle return from external lab system.

**GET Response (session check):**
```json
{
  "message": "Lab session is still active",
  "status": "active",
  "attempt_id": 15,
  "lab_name": "SQL Injection Basics"
}
```

**POST Request (submit results):**
```json
{
  "score": 85,
  "time_spent": 42,
  "notes": "Completed all challenges",
  "external_attempt_id": "ext_12345"
}
```

**POST Response:**
```json
{
  "message": "Lab results submitted successfully",
  "attempt_id": 15,
  "score": 85,
  "passed": true,
  "points_earned": 70,
  "perfect_score": false
}
```

## User Lab Attempts

### 6. List User Attempts
**GET** `/api/labs/attempts/`

List current user's lab attempts.

**Query Parameters:**
- `lab_id` (integer): Filter by specific lab
- `status` (string): Filter by attempt status
- `passed` (boolean): Filter by pass/fail status

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 15,
      "lab": 1,
      "lab_name": "SQL Injection Basics",
      "lab_category": "web_security",
      "lab_difficulty": "beginner",
      "attempt_number": 3,
      "status": "completed",
      "started_at": "2025-07-07T12:00:00Z",
      "ended_at": "2025-07-07T12:42:00Z",
      "time_spent": 42,
      "score": 85,
      "max_possible_score": 100,
      "is_passed": true,
      "is_perfect_score": false,
      "base_points_earned": 50,
      "bonus_points_earned": 20,
      "total_points_earned": 70,
      "duration_minutes": 42,
      "score_percentage": 85.0,
      "created_at": "2025-07-07T12:00:00Z"
    }
  ]
}
```

### 7. Get Attempt Details
**GET** `/api/labs/attempts/{attempt_id}/`

Get detailed information about a specific attempt.

### 8. User Lab Statistics
**GET** `/api/labs/attempts/stats/`

Get comprehensive statistics for the current user.

**Response:**
```json
{
  "total_attempts": 25,
  "completed_attempts": 20,
  "passed_attempts": 18,
  "perfect_scores": 5,
  "total_points_earned": 1250,
  "average_score": 82.5,
  "labs_completed": 12,
  "total_time_spent": 1080,
  "recent_attempts": [...]
}
```

## Leaderboards

### 9. Lab Leaderboard
**GET** `/api/labs/{lab_id}/leaderboard/`

Get leaderboard for a specific lab.

**Response:**
```json
{
  "lab": {...},
  "leaderboard": [
    {
      "rank": 1,
      "username": "hacker123",
      "score": 100,
      "time_spent": 35,
      "perfect_score": true,
      "completed_at": "2025-07-07T11:30:00Z"
    }
  ]
}
```

### 10. Overall Leaderboard
**GET** `/api/labs/leaderboard/`

Get overall points leaderboard.

**Response:**
```json
{
  "leaderboard": [
    {
      "username": "hacker123",
      "total_points": 2500,
      "labs_completed": 25,
      "perfect_scores": 10
    }
  ]
}
```

## External System Integration

### 11. Submit Lab Results (External)
**POST** `/api/labs/external/submit/`

Endpoint for external lab systems to submit results.

**Request:**
```json
{
  "redirect_token": "abc123",
  "external_attempt_id": "ext_12345",
  "score": 85,
  "time_spent": 42,
  "notes": "Additional feedback",
  "metadata": {"challenge_scores": [10, 8, 9]}
}
```

**Response:**
```json
{
  "success": true,
  "attempt_id": 15,
  "points_awarded": 70,
  "passed": true,
  "return_url": "http://localhost:8000/api/labs/return/abc123/"
}
```

## Points System Integration

The labs system is fully integrated with the global points system:

- **Base Points**: Awarded for completing any lab
- **Bonus Points**: Additional points for high scores or perfect scores
- **Perfect Score Bonus**: Extra points for achieving maximum score
- **Cooldown System**: Prevents point farming with time restrictions
- **Daily Limits**: Limits attempts per day to maintain challenge

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "error": "Insufficient permissions",
  "detail": "You must wait 45 minutes before attempting this lab again"
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden (cooldown, prerequisites, etc.)
- `404`: Not Found
- `410`: Gone (expired session)
- `500`: Internal Server Error

## External Lab Integration Guide

### Overview
External labs are independent websites that integrate with the main platform to provide hands-on practice environments. The integration uses secure token-based authentication and result submission.

### Integration Flow
1. User starts lab from main platform
2. Platform generates secure tokens and redirects to external lab
3. External lab authenticates user and provides practice environment
4. External lab submits results back to platform
5. User is redirected back to main platform with results

### Authentication
External labs receive these parameters in the redirect URL:
- `token`: Secure redirect token for this session
- `session`: Session identifier
- `user_id`: User's ID on the main platform
- `lab_id`: Lab identifier

### Result Submission
External labs must submit results to:
```
POST /api/labs/external/submit/
```

Required payload:
```json
{
  "redirect_token": "received_token",
  "score": 85,
  "time_spent": 42
}
```

Optional fields:
```json
{
  "external_attempt_id": "your_internal_id",
  "notes": "Additional feedback",
  "metadata": {"custom": "data"}
}
```

### Security Considerations
- Always validate the redirect token
- Use HTTPS for all communications
- Don't store sensitive user data
- Implement session timeouts
- Validate score ranges (0 to lab.max_score)

### Return URL Handling
After submitting results, redirect users to the return_url provided in the initial redirect or use the return_url from the submission response.
