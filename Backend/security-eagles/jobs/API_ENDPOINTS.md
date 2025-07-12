# Jobs System API Endpoints

This document provides comprehensive API endpoint documentation for the Jobs System frontend integration.

## Base URL
```
http://localhost:8000/api/jobs/
```

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Job Categories

### GET `/categories/`
**Description**: Get list of all active job categories  
**Permission**: Authenticated users  
**Response**:
```json
[
  {
    "id": 1,
    "name": "Software Development",
    "description": "Programming and software engineering jobs",
    "job_count": 15,
    "is_active": true
  }
]
```

---

## 💼 Jobs (Public Views)

### GET `/`
**Description**: Get paginated list of published jobs with filtering  
**Permission**: Authenticated users  
**Query Parameters**:
- `search` - Search in title, description, company name, requirements
- `category` - Filter by category ID
- `job_type` - Filter by job type (job, internship, freelance, contract)
- `employment_type` - Filter by employment type (full_time, part_time, contract, temporary, volunteer)
- `experience_level` - Filter by experience level (entry, junior, mid, senior, lead, executive)
- `is_remote` - Filter by remote availability (true/false)
- `remote_type` - Filter by remote type (fully_remote, hybrid, on_site)
- `location` - Filter by location (contains search)
- `salary_min` - Minimum salary filter
- `salary_max` - Maximum salary filter
- `tags` - Filter by tags (comma-separated)
- `is_featured` - Filter featured jobs (true/false)
- `is_urgent` - Filter urgent jobs (true/false)
- `page` - Page number for pagination
- `page_size` - Items per page (max 100)

**Response**:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/jobs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Senior Full Stack Developer",
      "company_name": "TechCorp Inc",
      "company_logo_url": "http://localhost:8000/media/company_logos/logo.png",
      "location": "San Francisco, CA",
      "job_type": "job",
      "employment_type": "full_time",
      "experience_level": "senior",
      "category_name": "Software Development",
      "is_remote": true,
      "remote_type": "hybrid",
      "salary_range_display": "$120,000 - $180,000 Per Year",
      "tags": ["React", "Node.js", "PostgreSQL"],
      "application_deadline": "2025-08-15T23:59:59Z",
      "days_until_deadline": 40,
      "is_featured": true,
      "is_urgent": false,
      "application_count": 12,
      "view_count": 156,
      "is_applied": false,
      "is_active": true,
      "created_at": "2025-07-06T10:30:00Z"
    }
  ]
}
```

### GET `/<int:id>/`
**Description**: Get detailed information about a specific job  
**Permission**: Authenticated users  
**Response**: Full job details including description, requirements, responsibilities, benefits, company info, etc.

---

## 📝 Job Applications

### POST `/applications/create/`
**Description**: Apply for a job  
**Permission**: Authenticated users  
**Request Body**:
```json
{
  "job": 1,
  "cover_letter": "I am very interested in this position...",
  "portfolio_links": ["https://github.com/user", "https://portfolio.com"]
}
```
**Response**: Created application details

### GET `/applications/`
**Description**: Get user's job applications  
**Permission**: Authenticated users (own applications only)  
**Response**: Paginated list of user's applications with job details

### GET `/applications/<int:pk>/`
**Description**: Get specific application details  
**Permission**: Authenticated users (own applications only)  

### PUT/PATCH `/applications/<int:pk>/`
**Description**: Update application (cover letter, portfolio links)  
**Permission**: Authenticated users (own applications only)  

### POST `/applications/<int:pk>/withdraw/`
**Description**: Withdraw a job application  
**Permission**: Authenticated users (own applications only)  
**Response**:
```json
{
  "detail": "Application withdrawn successfully."
}
```

---

## 🔧 Admin Endpoints

### GET `/admin/jobs/`
**Description**: Get all jobs (admin view)  
**Permission**: Admin users only  
**Features**: Same filtering as public job list + draft/closed jobs

### POST `/admin/jobs/`
**Description**: Create new job posting  
**Permission**: Admin users only  
**Request Body**: Full job data (see JobDetailSerializer)

### GET `/admin/jobs/<int:pk>/`
**Description**: Get specific job (admin view)  
**Permission**: Admin users only  

### PUT/PATCH `/admin/jobs/<int:pk>/`
**Description**: Update job posting  
**Permission**: Admin users only  

### DELETE `/admin/jobs/<int:pk>/`
**Description**: Delete job posting  
**Permission**: Admin users only  

### GET `/admin/applications/`
**Description**: Get all job applications (admin view)  
**Permission**: Admin users only  
**Query Parameters**:
- `status` - Filter by application status
- `job` - Filter by job ID
- `job__category` - Filter by job category
- `job__job_type` - Filter by job type

### GET `/admin/applications/<int:pk>/`
**Description**: Get specific application (admin view)  
**Permission**: Admin users only  

### PUT/PATCH `/admin/applications/<int:pk>/`
**Description**: Update application status, add admin notes, rating  
**Permission**: Admin users only  

---

## 📊 Data Models

### Job Status Choices
- `draft` - Draft
- `published` - Published
- `closed` - Closed
- `filled` - Filled

### Application Status Choices
- `pending` - Pending Review
- `reviewing` - Under Review
- `shortlisted` - Shortlisted
- `interview_scheduled` - Interview Scheduled
- `interview_completed` - Interview Completed
- `accepted` - Accepted
- `rejected` - Rejected
- `withdrawn` - Withdrawn by Applicant

### Job Type Choices
- `job` - Job
- `internship` - Internship
- `freelance` - Freelance
- `contract` - Contract

### Employment Type Choices
- `full_time` - Full-Time
- `part_time` - Part-Time
- `contract` - Contract
- `temporary` - Temporary
- `volunteer` - Volunteer

### Experience Level Choices
- `entry` - Entry Level
- `junior` - Junior
- `mid` - Mid Level
- `senior` - Senior
- `lead` - Lead
- `executive` - Executive

### Remote Type Choices
- `fully_remote` - Fully Remote
- `hybrid` - Hybrid
- `on_site` - On-Site

---

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "detail": "Already applied to this job."
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
  "detail": "Job not found."
}
```

---

## 📱 Frontend Integration Tips

1. **Pagination**: Use `page` and `page_size` parameters for job listings
2. **Search & Filters**: Combine multiple query parameters for advanced filtering
3. **Real-time Updates**: Check `is_applied` field to show application status
4. **File Uploads**: Use FormData for resume uploads in applications
5. **Error Handling**: Always handle 400/401/403/404 responses appropriately
6. **Loading States**: Show loading indicators for API calls
7. **Caching**: Consider caching job categories and static data

## 🔄 Legacy Endpoints (Deprecated)

These endpoints exist for backward compatibility but should not be used in new development:
- `GET/POST /legacy/` - Use `/` and `/admin/jobs/` instead
- `POST /legacy/<job_id>/apply/` - Use `/applications/create/` instead
- `POST /legacy/<job_id>/unapply/` - Use `/applications/<pk>/withdraw/` instead

---

## 💡 Example Frontend Usage

### Fetch Jobs with Filters
```javascript
const fetchJobs = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/jobs/?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};

// Usage
const jobs = await fetchJobs({
  search: 'React Developer',
  category: 1,
  is_remote: true,
  experience_level: 'mid',
  page: 1,
  page_size: 12
});
```

### Apply for a Job
```javascript
const applyForJob = async (jobId, applicationData) => {
  const response = await fetch('/api/jobs/applications/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      job: jobId,
      cover_letter: applicationData.coverLetter,
      portfolio_links: applicationData.portfolioLinks
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Application failed');
  }

  return response.json();
};
```

### Create Job (Admin)
```javascript
const createJob = async (jobData) => {
  const response = await fetch('/api/jobs/admin/jobs/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(jobData)
  });
  return response.json();
};
```

---

## 🎯 Common Use Cases

### Job Board Homepage
1. Fetch featured jobs: `GET /?is_featured=true&page_size=6`
2. Fetch job categories: `GET /categories/`
3. Show recent jobs: `GET /?page_size=12`

### Job Search Page
1. Implement search with filters
2. Use pagination for results
3. Show applied status for logged-in users

### Job Detail Page
1. Fetch job details: `GET /<job_id>/`
2. Check if user already applied
3. Show apply button or application status

### User Dashboard
1. Fetch user applications: `GET /applications/`
2. Show application status and dates
3. Allow withdrawal of pending applications

### Admin Dashboard
1. Manage all jobs: `GET /admin/jobs/`
2. Review applications: `GET /admin/applications/`
3. Update application statuses
4. Create/edit job postings

---

## 🔐 Security Notes

1. **Authentication Required**: All endpoints require valid JWT token
2. **Permission Levels**:
   - Regular users: Can view jobs and manage own applications
   - Admin users: Can manage all jobs and applications
3. **Data Validation**: All input is validated server-side
4. **Rate Limiting**: Consider implementing rate limiting for production
5. **File Uploads**: Resume uploads are validated for file type and size
