# Contact Us API Documentation

## Base URL
```
http://localhost:8000/api/contact/
```

## Authentication
- **Public APIs**: No authentication required
- **Admin APIs**: JWT authentication required with admin privileges

---

## 📧 PUBLIC APIS (No Authentication Required)

### 1. Submit Contact Message
**Endpoint**: `POST /message/`  
**Auth**: None required  
**Description**: Submit a new contact message

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "company": "Tech Corp",
  "subject": "general",
  "message": "I would like to inquire about your services and pricing options."
}
```

**Required Fields**: `name`, `email`, `message`  
**Optional Fields**: `phone`, `company`

**Subject Options**:
- `general` - General Inquiry
- `support` - Technical Support
- `business` - Business Partnership
- `feedback` - Feedback
- `bug_report` - Bug Report
- `feature_request` - Feature Request
- `other` - Other

**Example Request**:
```javascript
fetch('/api/contact/message/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: "John Doe",
    email: "john.doe@example.com",
    phone: "+1234567890",
    company: "Tech Corp",
    subject: "general",
    message: "I would like to inquire about your services and pricing options."
  })
})
```

**Example Response**:
```json
{
  "message": "Your message has been sent successfully! We will get back to you soon.",
  "id": 15,
  "created_at": "2025-07-07T10:30:00Z"
}
```

**Error Response**:
```json
{
  "name": ["This field is required."],
  "email": ["Enter a valid email address."],
  "message": ["Message must be at least 10 characters long."]
}
```

### 2. Get Community Information
**Endpoint**: `GET /settings/`
**Auth**: None required
**Description**: Get public community information and contact details

**Example Request**:
```javascript
fetch('/api/contact/settings/')
```

**Example Response**:
```json
{
  "community_description": "Security Eagles is a cybersecurity community focused on education, collaboration, and professional development. We bring together security professionals, students, and enthusiasts to share knowledge and grow together.",
  "contact_email": "contact@securityeagles.com",
  "discord_server": "https://discord.gg/securityeagles",
  "availability_info": "Our community is most active during:\n• Weekdays: 9:00 AM - 6:00 PM PST\n• Discord: 24/7 community support\n• Events: Weekends and evenings",
  "website_url": "https://securityeagles.com",
  "github_url": "https://github.com/securityeagles",
  "twitter_url": "https://twitter.com/securityeagles",
  "linkedin_url": "https://linkedin.com/company/securityeagles",
  "youtube_url": "https://youtube.com/@securityeagles"
}
```

### 3. Get Subject Choices
**Endpoint**: `GET /subjects/`  
**Auth**: None required  
**Description**: Get available subject options for contact forms

**Example Request**:
```javascript
fetch('/api/contact/subjects/')
```

**Example Response**:
```json
[
  {
    "value": "general",
    "label": "General Inquiry"
  },
  {
    "value": "support",
    "label": "Technical Support"
  },
  {
    "value": "business",
    "label": "Business Partnership"
  },
  {
    "value": "feedback",
    "label": "Feedback"
  },
  {
    "value": "bug_report",
    "label": "Bug Report"
  },
  {
    "value": "feature_request",
    "label": "Feature Request"
  },
  {
    "value": "other",
    "label": "Other"
  }
]
```

---

## 🔐 ADMIN APIS (Authentication Required)

### 4. List Contact Messages
**Endpoint**: `GET /admin/messages/`  
**Auth**: Admin required  
**Description**: Get paginated list of contact messages with filtering

**Query Parameters**:
- `status` - Filter by status (new, in_progress, resolved, closed)
- `subject` - Filter by subject
- `is_read` - Filter by read status (true/false)
- `search` - Search in name, email, or message content
- `page` - Page number
- `page_size` - Items per page

**Example Request**:
```javascript
fetch('/api/contact/admin/messages/?status=new&is_read=false&page=1', {
  headers: {
    'Authorization': 'Bearer ' + adminToken
  }
})
```

**Example Response**:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/contact/admin/messages/?page=2",
  "previous": null,
  "results": [
    {
      "id": 15,
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "company": "Tech Corp",
      "subject": "general",
      "subject_display": "General Inquiry",
      "message": "I would like to inquire about your services and pricing options.",
      "status": "new",
      "status_display": "New",
      "is_read": false,
      "created_at": "2025-07-07T10:30:00Z",
      "updated_at": "2025-07-07T10:30:00Z"
    }
  ]
}
```

### 5. Get/Update Message Details
**Endpoint**: `GET /admin/messages/{id}/`  
**Endpoint**: `PUT /admin/messages/{id}/`  
**Auth**: Admin required  
**Description**: View and update contact message details

**Example GET Request**:
```javascript
fetch('/api/contact/admin/messages/15/', {
  headers: {
    'Authorization': 'Bearer ' + adminToken
  }
})
```

**Example GET Response**:
```json
{
  "id": 15,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "company": "Tech Corp",
  "subject": "general",
  "subject_display": "General Inquiry",
  "message": "I would like to inquire about your services and pricing options.",
  "status": "new",
  "status_display": "New",
  "is_read": true,
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
  "created_at": "2025-07-07T10:30:00Z",
  "updated_at": "2025-07-07T10:30:00Z"
}
```

**Example PUT Request** (Update status):
```javascript
fetch('/api/contact/admin/messages/15/', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + adminToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    status: "resolved",
    is_read: true
  })
})
```

### 6. Get/Update Contact Settings
**Endpoint**: `GET /admin/settings/`  
**Endpoint**: `POST /admin/settings/`  
**Auth**: Admin required  
**Description**: Manage contact settings and configuration

**Example GET Request**:
```javascript
fetch('/api/contact/admin/settings/', {
  headers: {
    'Authorization': 'Bearer ' + adminToken
  }
})
```

**Example POST Request** (Update settings):
```javascript
fetch('/api/contact/admin/settings/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + adminToken,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    community_description: "Security Eagles is a cybersecurity community focused on education and collaboration.",
    contact_email: "contact@securityeagles.com",
    discord_server: "https://discord.gg/securityeagles",
    availability_info: "Our community is most active during weekdays 9 AM - 6 PM PST",
    website_url: "https://securityeagles.com",
    github_url: "https://github.com/securityeagles",
    auto_response_enabled: true,
    auto_response_message: "Thank you for contacting our community! We will respond within 24 hours.",
    admin_notification_enabled: true,
    admin_notification_emails: "admin@securityeagles.com,support@securityeagles.com"
  })
})
```

### 7. Get Contact Statistics
**Endpoint**: `GET /admin/stats/`  
**Auth**: Admin required  
**Description**: Get contact message statistics and analytics

**Example Request**:
```javascript
fetch('/api/contact/admin/stats/', {
  headers: {
    'Authorization': 'Bearer ' + adminToken
  }
}
```

---

## 🚀 FRONTEND INTEGRATION EXAMPLES

### React Contact Form Component
```javascript
// ContactForm.jsx
import React, { useState, useEffect } from 'react';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    subject: 'general',
    message: ''
  });
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchSubjects();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await fetch('/api/contact/subjects/');
      const data = await response.json();
      setSubjects(data);
    } catch (error) {
      console.error('Error fetching subjects:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: null
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const response = await fetch('/api/contact/message/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSuccess(true);
        setFormData({
          name: '',
          email: '',
          phone: '',
          company: '',
          subject: 'general',
          message: ''
        });
      } else {
        const errorData = await response.json();
        setErrors(errorData);
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setErrors({ general: 'An error occurred. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="success-message">
        <h3>Thank you for your message!</h3>
        <p>We have received your inquiry and will get back to you soon.</p>
        <button onClick={() => setSuccess(false)}>Send Another Message</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="contact-form">
      <div className="form-group">
        <label htmlFor="name">Name *</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
        {errors.name && <span className="error">{errors.name[0]}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="email">Email *</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
        {errors.email && <span className="error">{errors.email[0]}</span>}
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="phone">Phone</label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="company">Company</label>
          <input
            type="text"
            id="company"
            name="company"
            value={formData.company}
            onChange={handleChange}
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="subject">Subject *</label>
        <select
          id="subject"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          required
        >
          {subjects.map(subject => (
            <option key={subject.value} value={subject.value}>
              {subject.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="message">Message *</label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          rows={5}
          required
          placeholder="Please describe your inquiry in detail..."
        />
        {errors.message && <span className="error">{errors.message[0]}</span>}
      </div>

      {errors.general && (
        <div className="error general-error">{errors.general}</div>
      )}

      <button type="submit" disabled={loading} className="submit-btn">
        {loading ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
};

export default ContactForm;
```

### Contact Information Component
```javascript
// ContactInfo.jsx
import React, { useState, useEffect } from 'react';

const ContactInfo = () => {
  const [contactInfo, setContactInfo] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchContactInfo();
  }, []);

  const fetchContactInfo = async () => {
    try {
      const response = await fetch('/api/contact/settings/');
      const data = await response.json();
      setContactInfo(data);
    } catch (error) {
      console.error('Error fetching contact info:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading contact information...</div>;
  }

  return (
    <div className="contact-info">
      <h3>Connect with Our Community</h3>

      {contactInfo.community_description && (
        <div className="info-item">
          <h4>�️ About Our Community</h4>
          <p>{contactInfo.community_description}</p>
        </div>
      )}

      {contactInfo.contact_email && (
        <div className="info-item">
          <h4>✉️ Email</h4>
          <p>
            <a href={`mailto:${contactInfo.contact_email}`}>
              {contactInfo.contact_email}
            </a>
          </p>
        </div>
      )}

      {contactInfo.discord_server && (
        <div className="info-item">
          <h4>💬 Discord Community</h4>
          <p>
            <a href={contactInfo.discord_server} target="_blank" rel="noopener noreferrer">
              Join our Discord Server
            </a>
          </p>
        </div>
      )}

      {contactInfo.availability_info && (
        <div className="info-item">
          <h4>🕒 Community Activity</h4>
          <pre>{contactInfo.availability_info}</pre>
        </div>
      )}

      <div className="community-links">
        <h4>Find Us Online</h4>
        <div className="link-icons">
          {contactInfo.website_url && (
            <a href={contactInfo.website_url} target="_blank" rel="noopener noreferrer">
              🌐 Website
            </a>
          )}
          {contactInfo.github_url && (
            <a href={contactInfo.github_url} target="_blank" rel="noopener noreferrer">
              🐙 GitHub
            </a>
          )}
          {contactInfo.twitter_url && (
            <a href={contactInfo.twitter_url} target="_blank" rel="noopener noreferrer">
              🐦 Twitter
            </a>
          )}
          {contactInfo.linkedin_url && (
            <a href={contactInfo.linkedin_url} target="_blank" rel="noopener noreferrer">
              💼 LinkedIn
            </a>
          )}
          {contactInfo.youtube_url && (
            <a href={contactInfo.youtube_url} target="_blank" rel="noopener noreferrer">
              📺 YouTube
            </a>
          )}
        </div>
      </div>
    </div>
  );
};

export default ContactInfo;
```

---

## 🔐 ERROR HANDLING

### Common HTTP Status Codes
- **200 OK**: Successful GET requests
- **201 Created**: Successful message submission
- **400 Bad Request**: Invalid form data
- **401 Unauthorized**: Authentication required (admin endpoints)
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### Error Response Format
```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

---

## 📱 BEST PRACTICES

1. **Form Validation**: Validate on both client and server side
2. **Error Handling**: Show clear, user-friendly error messages
3. **Loading States**: Show loading indicators during form submission
4. **Success Feedback**: Provide clear confirmation after successful submission
5. **Accessibility**: Use proper labels and ARIA attributes
6. **Rate Limiting**: Consider implementing rate limiting for spam protection
7. **Email Validation**: Use proper email validation patterns
8. **Phone Formatting**: Allow flexible phone number formats
9. **Message Length**: Enforce reasonable message length limits
10. **Auto-save**: Consider auto-saving draft messages for longer forms)
```

**Example Response**:
```json
{
  "total_messages": 156,
  "unread_messages": 12,
  "recent_messages": 23,
  "status_breakdown": {
    "new": 12,
    "in_progress": 8,
    "resolved": 120,
    "closed": 16
  },
  "subject_breakdown": {
    "general": 45,
    "support": 38,
    "business": 22,
    "feedback": 18,
    "bug_report": 15,
    "feature_request": 12,
    "other": 6
  }
}
```
