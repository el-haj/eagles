# Learning Management System API Endpoints

This document provides comprehensive API endpoint documentation for the Learning Management System frontend integration.

## Base URL
```
http://localhost:8000/api/learnings/
```

## Authentication
Most endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

**Note**: Track endpoints do NOT require authentication, while all learning path endpoints DO require authentication.

---

## 📚 Tracks (No Authentication Required)

### GET `/tracks/`
**Description**: Get paginated list of all active tracks with filtering  
**Permission**: No authentication required  
**Query Parameters**:
- `search` - Search in title, description, or tags
- `category` - Filter by category (cyber, infrastructure, software_engineering)
- `level` - Filter by level (beginner, intermediate, advanced, expert)
- `tags` - Filter by tags (comma-separated)
- `ordering` - Order by: created_at, title, download_count, duration_hours
- `page` - Page number for pagination
- `page_size` - Items per page (max 100)

**Response**:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/learnings/tracks/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction to Cybersecurity",
      "description": "Comprehensive guide to cybersecurity fundamentals",
      "category": "cyber",
      "category_display": "Cybersecurity",
      "level": "beginner",
      "level_display": "Beginner",
      "thumbnail_url": "http://localhost:8000/media/tracks/thumbnails/cyber_intro.jpg",
      "pdf_url": "http://localhost:8000/media/tracks/pdfs/cyber_intro.pdf",
      "tags": ["security", "fundamentals", "networking"],
      "duration_hours": 8,
      "prerequisites": "Basic computer knowledge",
      "download_count": 156,
      "created_at": "2025-07-06T10:30:00Z"
    }
  ]
}
```

### GET `/tracks/<int:id>/`
**Description**: Get track details and increment download count  
**Permission**: No authentication required  
**Response**: Full track details

### GET `/tracks/category/<str:category>/`
**Description**: Get tracks filtered by category  
**Permission**: No authentication required  
**Categories**: `cyber`, `infrastructure`, `software_engineering`

---

## 🎓 Learning Paths (Authentication Required)

### GET `/learning-paths/`
**Description**: Get paginated list of published learning paths with filtering  
**Permission**: Authenticated users  
**Query Parameters**:
- `search` - Search in title, description, or tags
- `category` - Filter by category
- `level` - Filter by level
- `tags` - Filter by tags (comma-separated)
- `is_featured` - Filter featured paths (true/false)
- `min_rating` - Minimum average rating filter
- `ordering` - Order by: created_at, title, average_rating, enrollment_count
- `page` - Page number for pagination

**Response**:
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "title": "Advanced Penetration Testing",
      "short_description": "Master advanced penetration testing techniques",
      "category": "cyber",
      "category_display": "Cybersecurity",
      "level": "advanced",
      "level_display": "Advanced",
      "thumbnail_url": "http://localhost:8000/media/learning_paths/thumbnails/pentest.jpg",
      "estimated_duration_hours": 40,
      "instructor_name": "John Doe",
      "sections_count": 12,
      "enrollment_count": 89,
      "average_rating": 4.7,
      "total_ratings": 23,
      "is_featured": true,
      "is_enrolled": false,
      "user_progress": null,
      "created_at": "2025-07-06T10:30:00Z"
    }
  ]
}
```

### GET `/learning-paths/<int:id>/`
**Description**: Get detailed learning path information with sections  
**Permission**: Authenticated users  
**Response**: Full learning path details including sections, user progress, and rating

### POST `/learning-paths/<int:learning_path_id>/enroll/`
**Description**: Enroll in a learning path  
**Permission**: Authenticated users  
**Response**:
```json
{
  "detail": "Successfully enrolled in learning path",
  "progress": {
    "id": 1,
    "status": "not_started",
    "progress_percentage": 0.00,
    "enrolled_at": "2025-07-06T15:30:00Z"
  }
}
```

### DELETE `/learning-paths/<int:learning_path_id>/unenroll/`
**Description**: Unenroll from a learning path  
**Permission**: Authenticated users  

---

## 📖 Sections & Progress

### POST `/sections/<int:section_id>/complete/`
**Description**: Mark a learning section as complete  
**Permission**: Authenticated users (must be enrolled)  
**Response**: Updated progress information

### GET `/my-progress/`
**Description**: Get user's learning progress across all enrolled paths  
**Permission**: Authenticated users  
**Query Parameters**:
- `status` - Filter by status (not_started, in_progress, completed, paused)
- `ordering` - Order by: enrolled_at, last_accessed_at, progress_percentage

**Response**:
```json
{
  "results": [
    {
      "id": 1,
      "learning_path": {
        "id": 1,
        "title": "Advanced Penetration Testing",
        "thumbnail_url": "...",
        "instructor_name": "John Doe"
      },
      "status": "in_progress",
      "status_display": "In Progress",
      "progress_percentage": 45.50,
      "completed_sections_count": 5,
      "total_sections_count": 11,
      "enrolled_at": "2025-07-01T10:00:00Z",
      "started_at": "2025-07-01T10:30:00Z",
      "last_accessed_at": "2025-07-06T14:20:00Z"
    }
  ]
}
```

---

## 💬 Comments

### GET `/learning-paths/<int:learning_path_id>/comments/`
**Description**: Get comments for a learning path (top-level only)  
**Permission**: Authenticated users  
**Response**: Paginated list of comments

### POST `/learning-paths/<int:learning_path_id>/comments/`
**Description**: Create a new comment on a learning path  
**Permission**: Authenticated users  
**Request Body**:
```json
{
  "content": "Great learning path! Very comprehensive."
}
```

### GET `/comments/<int:pk>/`
**Description**: Get specific comment details  
**Permission**: Authenticated users  

### PUT/PATCH `/comments/<int:pk>/`
**Description**: Update a comment (owner only)  
**Permission**: Authenticated users (comment owner)  

### DELETE `/comments/<int:pk>/`
**Description**: Delete a comment (owner only)  
**Permission**: Authenticated users (comment owner)  

### GET `/comments/<int:comment_id>/replies/`
**Description**: Get replies to a specific comment  
**Permission**: Authenticated users  

### POST `/comments/<int:comment_id>/replies/`
**Description**: Reply to a comment  
**Permission**: Authenticated users  
**Request Body**:
```json
{
  "content": "I agree with your assessment!"
}
```

---

## ⭐ Ratings

### GET `/learning-paths/<int:learning_path_id>/ratings/`
**Description**: Get ratings for a learning path  
**Permission**: Authenticated users  
**Response**: Paginated list of ratings with reviews

### POST `/learning-paths/<int:learning_path_id>/ratings/`
**Description**: Rate a learning path (creates new or updates existing)  
**Permission**: Authenticated users  
**Request Body**:
```json
{
  "rating": 5,
  "review": "Excellent content and well-structured lessons!"
}
```

### GET `/ratings/<int:pk>/`
**Description**: Get specific rating details  
**Permission**: Authenticated users  

### PUT/PATCH `/ratings/<int:pk>/`
**Description**: Update a rating (owner only)  
**Permission**: Authenticated users (rating owner)  

### DELETE `/ratings/<int:pk>/`
**Description**: Delete a rating (owner only)  
**Permission**: Authenticated users (rating owner)  

---

## 📊 Data Models

### Track Categories
- `cyber` - Cybersecurity
- `infrastructure` - Infrastructure
- `software_engineering` - Software Engineering

### Learning Levels
- `beginner` - Beginner
- `intermediate` - Intermediate
- `advanced` - Advanced
- `expert` - Expert

### Learning Progress Status
- `not_started` - Not Started
- `in_progress` - In Progress
- `completed` - Completed
- `paused` - Paused

### Section Content Types
- `video` - Video
- `pdf` - PDF Document
- `markdown` - Markdown Content
- `quiz` - Quiz
- `assignment` - Assignment

### Learning Path Status
- `draft` - Draft
- `published` - Published
- `archived` - Archived

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "detail": "Already enrolled in this learning path."
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
  "detail": "You can only edit your own comments."
}
```

### 404 Not Found
```json
{
  "detail": "Learning path not found."
}
```

---

## 💡 Frontend Integration Tips

1. **Track Access**: Tracks can be accessed without authentication for public learning resources
2. **Learning Paths**: All learning path features require user authentication
3. **Progress Tracking**: Use the progress endpoints to show user advancement
4. **Real-time Updates**: Check enrollment status and progress in list views
5. **Comments & Ratings**: Implement nested comment threads and rating systems
6. **File Downloads**: Handle PDF downloads for tracks and sections
7. **Video Integration**: Support YouTube and other video platforms
8. **Search & Filters**: Implement comprehensive filtering for better UX

## 🔐 Security Notes

1. **Mixed Authentication**: Tracks are public, learning paths require auth
2. **Ownership Validation**: Users can only edit their own comments/ratings
3. **Enrollment Validation**: Section completion requires enrollment
4. **Content Access**: Published content only for learning paths
5. **File Security**: Validate file uploads and access permissions
