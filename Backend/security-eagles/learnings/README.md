# Learning Management System API Documentation

## Base URL
```
http://localhost:8000/api/learnings/
```

## Authentication
- **Tracks**: No authentication required (public access)
- **Learning Paths**: Authentication required for all operations
- **Comments & Ratings**: Authentication required

Include JWT token in Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📚 TRACKS (Public Access)

### 1. Get All Tracks
**Endpoint**: `GET /tracks/`
**Auth**: None required
**Description**: Get paginated list of all active tracks with filtering

**Query Parameters**:
- `search` - Search in title, description, tags
- `category` - Filter by category (cyber, infrastructure, software_engineering)
- `level` - Filter by level (beginner, intermediate, advanced, expert)
- `tags` - Filter by tags (comma-separated)
- `ordering` - Order by: created_at, title, download_count, duration_hours
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 12)

**Example Request**:
```javascript
// Get cybersecurity tracks for beginners
fetch('/api/learnings/tracks/?category=cyber&level=beginner&page=1&page_size=6')
```

**Example Response**:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/learnings/tracks/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction to Cybersecurity",
      "description": "Learn the fundamentals of cybersecurity including threat analysis, risk assessment, and basic security principles.",
      "category": "cyber",
      "category_display": "Cybersecurity",
      "level": "beginner",
      "level_display": "Beginner",
      "pdf_file_url": "http://localhost:8000/media/tracks/pdfs/intro_cybersecurity.pdf",
      "thumbnail_url": "http://localhost:8000/media/tracks/thumbnails/cyber_intro.jpg",
      "tags": ["security", "fundamentals", "beginner"],
      "duration_hours": 8,
      "prerequisites": "Basic computer knowledge",
      "download_count": 156,
      "is_active": true,
      "created_at": "2025-07-01T10:00:00Z",
      "updated_at": "2025-07-05T14:30:00Z"
    }
  ]
}
```

### 2. Get Track Details
**Endpoint**: `GET /tracks/{id}/`
**Auth**: None required

**Example Request**:
```javascript
fetch('/api/learnings/tracks/1/')
```

**Example Response**:
```json
{
  "id": 1,
  "title": "Introduction to Cybersecurity",
  "description": "Learn the fundamentals of cybersecurity including threat analysis, risk assessment, and basic security principles.",
  "category": "cyber",
  "category_display": "Cybersecurity",
  "level": "beginner",
  "level_display": "Beginner",
  "pdf_file_url": "http://localhost:8000/media/tracks/pdfs/intro_cybersecurity.pdf",
  "thumbnail_url": "http://localhost:8000/media/tracks/thumbnails/cyber_intro.jpg",
  "tags": ["security", "fundamentals", "beginner"],
  "duration_hours": 8,
  "prerequisites": "Basic computer knowledge",
  "download_count": 156,
  "learning_paths_count": 3,
  "is_active": true,
  "created_at": "2025-07-01T10:00:00Z",
  "updated_at": "2025-07-05T14:30:00Z"
}
```

### 3. Download Track PDF
**Endpoint**: `GET /tracks/{id}/download/`
**Auth**: None required
**Description**: Download PDF file and increment download count

**Example Request**:
```javascript
// Trigger download
window.open('/api/learnings/tracks/1/download/', '_blank');
```

**Response**: PDF file download + incremented download_count

---

## 🎓 LEARNING PATHS (Authentication Required)

### 4. Get All Learning Paths
**Endpoint**: `GET /learning-paths/`
**Auth**: Required
**Description**: Get paginated learning paths with user-specific data

**Query Parameters**:
- `search` - Search in title, description
- `category` - Filter by category
- `level` - Filter by level
- `track` - Filter by track ID
- `status` - Filter by status (draft, published, archived)
- `is_featured` - Filter featured paths (true/false)
- `instructor` - Filter by instructor ID
- `ordering` - Order by: created_at, title, enrollment_count, average_rating
- `page` - Page number
- `page_size` - Items per page

**Example Request**:
```javascript
fetch('/api/learnings/learning-paths/?track=1&is_featured=true', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Advanced Penetration Testing",
      "short_description": "Master advanced penetration testing techniques and methodologies",
      "category": "cyber",
      "category_display": "Cybersecurity",
      "level": "advanced",
      "level_display": "Advanced",
      "track": {
        "id": 1,
        "title": "Introduction to Cybersecurity"
      },
      "thumbnail_url": "http://localhost:8000/media/learning_paths/thumbnails/pentest.jpg",
      "intro_video_url": "https://youtube.com/watch?v=example",
      "estimated_duration_hours": 40,
      "instructor_name": "John Doe",
      "sections_count": 12,
      "enrollment_count": 89,
      "completion_count": 23,
      "average_rating": 4.7,
      "total_ratings": 15,
      "is_featured": true,
      "status": "published",
      "is_enrolled": false,
      "user_progress": null,
      "created_at": "2025-07-01T10:00:00Z",
      "published_at": "2025-07-02T09:00:00Z"
    }
  ]
}
```

### 5. Get Learning Path Details
**Endpoint**: `GET /learning-paths/{id}/`
**Auth**: Required

**Example Request**:
```javascript
fetch('/api/learnings/learning-paths/1/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "id": 1,
  "title": "Advanced Penetration Testing",
  "description": "Comprehensive course covering advanced penetration testing methodologies, tools, and real-world scenarios.",
  "short_description": "Master advanced penetration testing techniques and methodologies",
  "category": "cyber",
  "category_display": "Cybersecurity",
  "level": "advanced",
  "level_display": "Advanced",
  "track": {
    "id": 1,
    "title": "Introduction to Cybersecurity",
    "category": "cyber"
  },
  "thumbnail_url": "http://localhost:8000/media/learning_paths/thumbnails/pentest.jpg",
  "intro_video_url": "https://youtube.com/watch?v=example",
  "estimated_duration_hours": 40,
  "prerequisites": "Basic networking knowledge, Linux fundamentals",
  "learning_objectives": [
    "Master advanced reconnaissance techniques",
    "Understand exploitation methodologies",
    "Learn post-exploitation techniques",
    "Develop reporting skills"
  ],
  "tags": ["penetration testing", "security", "advanced", "ethical hacking"],
  "instructor": {
    "id": 2,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe"
  },
  "sections_count": 12,
  "enrollment_count": 89,
  "completion_count": 23,
  "average_rating": 4.7,
  "total_ratings": 15,
  "is_featured": true,
  "status": "published",
  "is_enrolled": true,
  "user_progress": {
    "id": 5,
    "progress_percentage": 65.5,
    "completed_sections_count": 8,
    "status": "in_progress",
    "last_accessed_at": "2025-07-06T14:30:00Z",
    "enrolled_at": "2025-07-01T10:00:00Z"
  },
  "sections": [
    {
      "id": 1,
      "title": "Introduction to Advanced Penetration Testing",
      "content_type": "video",
      "video_url": "https://youtube.com/watch?v=intro",
      "duration_minutes": 45,
      "order": 1,
      "is_completed": true
    },
    {
      "id": 2,
      "title": "Reconnaissance Techniques",
      "content_type": "pdf",
      "pdf_file_url": "http://localhost:8000/media/sections/recon.pdf",
      "duration_minutes": 60,
      "order": 2,
      "is_completed": true
    }
  ],
  "created_at": "2025-07-01T10:00:00Z",
  "published_at": "2025-07-02T09:00:00Z"
}
```

### 6. Enroll in Learning Path
**Endpoint**: `POST /learning-paths/{id}/enroll/`
**Auth**: Required

**Example Request**:
```javascript
fetch('/api/learnings/learning-paths/1/enroll/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
})
```

**Example Response**:
```json
{
  "message": "Successfully enrolled in learning path",
  "enrollment": {
    "id": 15,
    "learning_path": 1,
    "user": 5,
    "progress_percentage": 0.0,
    "status": "not_started",
    "enrolled_at": "2025-07-06T15:00:00Z"
  }
}
```

### 7. Unenroll from Learning Path
**Endpoint**: `POST /learning-paths/{id}/unenroll/`
**Auth**: Required

**Example Request**:
```javascript
fetch('/api/learnings/learning-paths/1/unenroll/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "message": "Successfully unenrolled from learning path"
}
```

---

## 📖 LEARNING SECTIONS

### 8. Get Section Details
**Endpoint**: `GET /sections/{id}/`
**Auth**: Required

**Example Request**:
```javascript
fetch('/api/learnings/sections/1/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "id": 1,
  "title": "Introduction to Advanced Penetration Testing",
  "description": "Overview of advanced penetration testing concepts and methodologies",
  "content_type": "video",
  "video_url": "https://youtube.com/watch?v=intro",
  "pdf_file_url": null,
  "markdown_content": null,
  "duration_minutes": 45,
  "order": 1,
  "learning_path": {
    "id": 1,
    "title": "Advanced Penetration Testing"
  },
  "is_completed": true,
  "comments_count": 8,
  "is_active": true,
  "created_at": "2025-07-01T10:00:00Z"
}
```

### 9. Mark Section as Complete
**Endpoint**: `POST /sections/{id}/complete/`
**Auth**: Required

**Example Request**:
```javascript
fetch('/api/learnings/sections/1/complete/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "message": "Section marked as completed",
  "progress": {
    "section_id": 1,
    "is_completed": true,
    "completed_at": "2025-07-06T15:30:00Z",
    "overall_progress_percentage": 75.5
  }
}
```

---

## 💬 COMMENTS SYSTEM

### 10. Get Section Comments
**Endpoint**: `GET /sections/{section_id}/comments/`
**Auth**: Required
**Description**: Get threaded comments for a specific section

**Query Parameters**:
- `page` - Page number
- `page_size` - Items per page

**Example Request**:
```javascript
fetch('/api/learnings/sections/1/comments/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "content": "Great introduction! Very clear explanation of the concepts.",
      "user": {
        "id": 3,
        "username": "alice_smith",
        "first_name": "Alice",
        "last_name": "Smith"
      },
      "section": 1,
      "parent": null,
      "replies_count": 2,
      "is_active": true,
      "created_at": "2025-07-05T10:30:00Z",
      "updated_at": "2025-07-05T10:30:00Z",
      "replies": [
        {
          "id": 2,
          "content": "I agree! The examples were particularly helpful.",
          "user": {
            "id": 4,
            "username": "bob_jones",
            "first_name": "Bob",
            "last_name": "Jones"
          },
          "section": 1,
          "parent": 1,
          "replies_count": 0,
          "is_active": true,
          "created_at": "2025-07-05T11:00:00Z",
          "updated_at": "2025-07-05T11:00:00Z",
          "replies": []
        }
      ]
    }
  ]
}
```

### 11. Create Comment
**Endpoint**: `POST /sections/{section_id}/comments/`
**Auth**: Required

**Request Body**:
```json
{
  "content": "This section was very informative!",
  "parent": null  // Optional: ID of parent comment for replies
}
```

**Example Request**:
```javascript
fetch('/api/learnings/sections/1/comments/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: "This section was very informative!",
    parent: null
  })
})
```

**Example Response**:
```json
{
  "id": 15,
  "content": "This section was very informative!",
  "user": {
    "id": 5,
    "username": "current_user",
    "first_name": "Current",
    "last_name": "User"
  },
  "section": 1,
  "parent": null,
  "replies_count": 0,
  "is_active": true,
  "created_at": "2025-07-06T15:45:00Z",
  "updated_at": "2025-07-06T15:45:00Z",
  "replies": []
}
```

### 12. Update Comment
**Endpoint**: `PUT /comments/{id}/`
**Auth**: Required (only comment owner)

**Request Body**:
```json
{
  "content": "Updated comment content"
}
```

**Example Request**:
```javascript
fetch('/api/learnings/comments/15/', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    content: "Updated comment content"
  })
})
```

### 13. Delete Comment
**Endpoint**: `DELETE /comments/{id}/`
**Auth**: Required (only comment owner)

**Example Request**:
```javascript
fetch('/api/learnings/comments/15/', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "message": "Comment deleted successfully"
}
```

---

## ⭐ RATINGS SYSTEM

### 14. Get Learning Path Ratings
**Endpoint**: `GET /learning-paths/{id}/ratings/`
**Auth**: Required

**Example Request**:
```javascript
fetch('/api/learnings/learning-paths/1/ratings/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "count": 15,
  "average_rating": 4.7,
  "rating_distribution": {
    "5": 8,
    "4": 5,
    "3": 2,
    "2": 0,
    "1": 0
  },
  "user_rating": {
    "id": 5,
    "rating": 5,
    "review": "Excellent course! Learned a lot.",
    "created_at": "2025-07-05T14:00:00Z"
  },
  "results": [
    {
      "id": 1,
      "rating": 5,
      "review": "Outstanding content and presentation!",
      "user": {
        "id": 3,
        "username": "alice_smith",
        "first_name": "Alice",
        "last_name": "Smith"
      },
      "created_at": "2025-07-04T10:00:00Z",
      "updated_at": "2025-07-04T10:00:00Z"
    }
  ]
}
```

### 15. Create/Update Rating
**Endpoint**: `POST /learning-paths/{id}/rate/`
**Auth**: Required

**Request Body**:
```json
{
  "rating": 5,
  "review": "Excellent course! Very comprehensive and well-structured."
}
```

**Example Request**:
```javascript
fetch('/api/learnings/learning-paths/1/rate/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    rating: 5,
    review: "Excellent course! Very comprehensive and well-structured."
  })
})
```

**Example Response**:
```json
{
  "id": 8,
  "rating": 5,
  "review": "Excellent course! Very comprehensive and well-structured.",
  "user": {
    "id": 5,
    "username": "current_user"
  },
  "learning_path": 1,
  "created_at": "2025-07-06T16:00:00Z",
  "updated_at": "2025-07-06T16:00:00Z",
  "message": "Rating created successfully"
}
```

---

## 📊 USER PROGRESS & DASHBOARD

### 16. Get User Progress
**Endpoint**: `GET /progress/`
**Auth**: Required
**Description**: Get user's learning progress across all enrolled paths

**Query Parameters**:
- `status` - Filter by status (not_started, in_progress, completed)
- `learning_path` - Filter by specific learning path ID

**Example Request**:
```javascript
fetch('/api/learnings/progress/?status=in_progress', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "count": 3,
  "results": [
    {
      "id": 5,
      "learning_path": {
        "id": 1,
        "title": "Advanced Penetration Testing",
        "thumbnail_url": "http://localhost:8000/media/learning_paths/thumbnails/pentest.jpg",
        "estimated_duration_hours": 40,
        "sections_count": 12
      },
      "progress_percentage": 65.5,
      "completed_sections_count": 8,
      "status": "in_progress",
      "last_accessed_at": "2025-07-06T14:30:00Z",
      "enrolled_at": "2025-07-01T10:00:00Z",
      "completed_at": null,
      "completed_sections": [1, 2, 3, 4, 5, 6, 7, 8]
    }
  ]
}
```

### 17. Get User Dashboard Summary
**Endpoint**: `GET /dashboard/`
**Auth**: Required

**Example Request**:
```javascript
fetch('/api/learnings/dashboard/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
```

**Example Response**:
```json
{
  "total_enrollments": 5,
  "completed_paths": 2,
  "in_progress_paths": 3,
  "total_learning_hours": 120,
  "completed_learning_hours": 48,
  "recent_activity": [
    {
      "type": "section_completed",
      "learning_path": "Advanced Penetration Testing",
      "section": "Reconnaissance Techniques",
      "timestamp": "2025-07-06T14:30:00Z"
    },
    {
      "type": "comment_posted",
      "learning_path": "Web Application Security",
      "section": "SQL Injection Basics",
      "timestamp": "2025-07-06T10:15:00Z"
    }
  ],
  "recommended_paths": [
    {
      "id": 3,
      "title": "Advanced Web Security",
      "reason": "Based on your progress in cybersecurity tracks"
    }
  ]
}
```

---

## 🔍 SEARCH & FILTERING

### 18. Global Search
**Endpoint**: `GET /search/`
**Auth**: Optional (results vary based on authentication)

**Query Parameters**:
- `q` - Search query
- `type` - Filter by type (tracks, learning_paths, sections)
- `category` - Filter by category
- `level` - Filter by level

**Example Request**:
```javascript
fetch('/api/learnings/search/?q=penetration testing&type=learning_paths')
```

**Example Response**:
```json
{
  "tracks": {
    "count": 2,
    "results": [
      {
        "id": 1,
        "title": "Introduction to Cybersecurity",
        "type": "track",
        "category": "cyber",
        "level": "beginner"
      }
    ]
  },
  "learning_paths": {
    "count": 3,
    "results": [
      {
        "id": 1,
        "title": "Advanced Penetration Testing",
        "type": "learning_path",
        "category": "cyber",
        "level": "advanced",
        "is_enrolled": false
      }
    ]
  },
  "sections": {
    "count": 8,
    "results": [
      {
        "id": 5,
        "title": "Penetration Testing Methodology",
        "type": "section",
        "learning_path": "Advanced Penetration Testing"
      }
    ]
  }
}
```

---

## 🚀 FRONTEND INTEGRATION EXAMPLES

### React/JavaScript Integration Examples

#### 1. Fetch and Display Tracks
```javascript
// TracksList.jsx
import React, { useState, useEffect } from 'react';

const TracksList = () => {
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    level: '',
    search: ''
  });

  useEffect(() => {
    fetchTracks();
  }, [filters]);

  const fetchTracks = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filters.category) params.append('category', filters.category);
    if (filters.level) params.append('level', filters.level);
    if (filters.search) params.append('search', filters.search);

    try {
      const response = await fetch(`/api/learnings/tracks/?${params}`);
      const data = await response.json();
      setTracks(data.results);
    } catch (error) {
      console.error('Error fetching tracks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (trackId) => {
    window.open(`/api/learnings/tracks/${trackId}/download/`, '_blank');
  };

  return (
    <div className="tracks-list">
      {/* Filter controls */}
      <div className="filters">
        <select
          value={filters.category}
          onChange={(e) => setFilters({...filters, category: e.target.value})}
        >
          <option value="">All Categories</option>
          <option value="cyber">Cybersecurity</option>
          <option value="infrastructure">Infrastructure</option>
          <option value="software_engineering">Software Engineering</option>
        </select>
      </div>

      {/* Tracks grid */}
      <div className="tracks-grid">
        {tracks.map(track => (
          <div key={track.id} className="track-card">
            <img src={track.thumbnail_url} alt={track.title} />
            <h3>{track.title}</h3>
            <p>{track.description}</p>
            <div className="track-meta">
              <span>{track.level_display}</span>
              <span>{track.duration_hours}h</span>
              <span>{track.download_count} downloads</span>
            </div>
            <button onClick={() => handleDownload(track.id)}>
              Download PDF
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### 2. Learning Path Enrollment
```javascript
// LearningPathCard.jsx
import React, { useState } from 'react';

const LearningPathCard = ({ learningPath, token, onEnrollmentChange }) => {
  const [enrolling, setEnrolling] = useState(false);

  const handleEnrollment = async () => {
    setEnrolling(true);
    const endpoint = learningPath.is_enrolled ? 'unenroll' : 'enroll';

    try {
      const response = await fetch(`/api/learnings/learning-paths/${learningPath.id}/${endpoint}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        onEnrollmentChange(learningPath.id, !learningPath.is_enrolled);
      }
    } catch (error) {
      console.error('Enrollment error:', error);
    } finally {
      setEnrolling(false);
    }
  };

  return (
    <div className="learning-path-card">
      <img src={learningPath.thumbnail_url} alt={learningPath.title} />
      <div className="content">
        <h3>{learningPath.title}</h3>
        <p>{learningPath.short_description}</p>

        <div className="meta">
          <span>⭐ {learningPath.average_rating} ({learningPath.total_ratings})</span>
          <span>👥 {learningPath.enrollment_count} enrolled</span>
          <span>⏱️ {learningPath.estimated_duration_hours}h</span>
        </div>

        {learningPath.user_progress && (
          <div className="progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{width: `${learningPath.user_progress.progress_percentage}%`}}
              />
            </div>
            <span>{learningPath.user_progress.progress_percentage}% complete</span>
          </div>
        )}

        <button
          onClick={handleEnrollment}
          disabled={enrolling}
          className={learningPath.is_enrolled ? 'unenroll-btn' : 'enroll-btn'}
        >
          {enrolling ? 'Processing...' :
           learningPath.is_enrolled ? 'Unenroll' : 'Enroll Now'}
        </button>
      </div>
    </div>
  );
};
```

#### 3. Comments System
```javascript
// CommentsSection.jsx
import React, { useState, useEffect } from 'react';

const CommentsSection = ({ sectionId, token }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyTo, setReplyTo] = useState(null);

  useEffect(() => {
    fetchComments();
  }, [sectionId]);

  const fetchComments = async () => {
    try {
      const response = await fetch(`/api/learnings/sections/${sectionId}/comments/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setComments(data.results);
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const submitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const response = await fetch(`/api/learnings/sections/${sectionId}/comments/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: newComment,
          parent: replyTo
        })
      });

      if (response.ok) {
        setNewComment('');
        setReplyTo(null);
        fetchComments(); // Refresh comments
      }
    } catch (error) {
      console.error('Error posting comment:', error);
    }
  };

  const CommentItem = ({ comment, isReply = false }) => (
    <div className={`comment ${isReply ? 'reply' : ''}`}>
      <div className="comment-header">
        <strong>{comment.user.first_name} {comment.user.last_name}</strong>
        <span className="timestamp">{new Date(comment.created_at).toLocaleDateString()}</span>
      </div>
      <p>{comment.content}</p>
      {!isReply && (
        <button onClick={() => setReplyTo(comment.id)}>Reply</button>
      )}

      {comment.replies && comment.replies.map(reply => (
        <CommentItem key={reply.id} comment={reply} isReply={true} />
      ))}
    </div>
  );

  return (
    <div className="comments-section">
      <h4>Comments ({comments.length})</h4>

      <form onSubmit={submitComment} className="comment-form">
        {replyTo && (
          <div className="reply-indicator">
            Replying to comment...
            <button type="button" onClick={() => setReplyTo(null)}>Cancel</button>
          </div>
        )}
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder={replyTo ? "Write a reply..." : "Write a comment..."}
          rows={3}
        />
        <button type="submit">Post Comment</button>
      </form>

      <div className="comments-list">
        {comments.map(comment => (
          <CommentItem key={comment.id} comment={comment} />
        ))}
      </div>
    </div>
  );
};
```

---

## 🔐 ERROR HANDLING

### Common HTTP Status Codes

- **200 OK**: Successful GET requests
- **201 Created**: Successful POST requests (creation)
- **204 No Content**: Successful DELETE requests
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Duplicate enrollment, etc.
- **500 Internal Server Error**: Server error

### Error Response Format
```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Specific field error"]
  }
}
```

---

## 📱 BEST PRACTICES

1. **Authentication**: Always include JWT token for protected endpoints
2. **Error Handling**: Implement proper error handling for all API calls
3. **Loading States**: Show loading indicators during API requests
4. **Pagination**: Handle paginated responses properly
5. **Caching**: Cache frequently accessed data (tracks, learning paths)
6. **Real-time Updates**: Refresh data after user actions (enrollment, comments)
7. **File Downloads**: Handle PDF downloads with proper error handling
8. **Progress Tracking**: Update progress indicators in real-time
9. **Search Debouncing**: Debounce search inputs to avoid excessive API calls
10. **Responsive Design**: Ensure mobile-friendly implementation
```
```