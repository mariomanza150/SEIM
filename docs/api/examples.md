# API Examples

This document provides complete examples of common workflows and integrations with the SEIM API.

## Complete Application Flow

### 1. Student Registration and Login

```javascript
// Register a new student
async function registerStudent(userData) {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: userData.email,
      email: userData.email,
      password: userData.password,
      first_name: userData.firstName,
      last_name: userData.lastName
    })
  });
  
  if (!response.ok) {
    throw new Error('Registration failed');
  }
  
  return response.json();
}

// Login
async function login(email, password) {
  const response = await fetch('/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: email,
      password: password
    })
  });
  
  const data = await response.json();
  
  // Store token
  localStorage.setItem('access_token', data.token);
  localStorage.setItem('user_id', data.user.id);
  
  return data.user;
}
```

### 2. Create Exchange Application

```javascript
class ExchangeApplication {
  constructor(token) {
    this.token = token;
    this.exchangeId = null;
  }
  
  async create(applicationData) {
    const response = await fetch('/api/exchanges/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        first_name: applicationData.firstName,
        last_name: applicationData.lastName,
        email: applicationData.email,
        phone: applicationData.phone,
        university: applicationData.university,
        destination_university: applicationData.destinationUniversity,
        exchange_type: applicationData.exchangeType,
        start_date: applicationData.startDate,
        end_date: applicationData.endDate
      })
    });
    
    const exchange = await response.json();
    this.exchangeId = exchange.id;
    return exchange;
  }
  
  async uploadDocument(file, documentType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('exchange', this.exchangeId);
    formData.append('document_type', documentType);
    formData.append('title', file.name);
    
    const response = await fetch('/api/documents/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });
    
    return response.json();
  }
  
  async submitApplication() {
    const response = await fetch(`/api/exchanges/${this.exchangeId}/transition/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        status: 'submitted',
        comment: 'Application complete and ready for review'
      })
    });
    
    return response.json();
  }
}
```

### 3. Dynamic Form Submission

```javascript
class FormManager {
  constructor(token, exchangeId) {
    this.token = token;
    this.exchangeId = exchangeId;
    this.steps = [];
    this.currentStep = 0;
  }
  
  async loadSteps() {
    const response = await fetch('/api/form-steps/', {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    
    const data = await response.json();
    this.steps = data.results;
  }
  
  async submitStep(stepData) {
    const step = this.steps[this.currentStep];
    
    const response = await fetch('/api/form-submissions/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        exchange: this.exchangeId,
        form_step: step.id,
        data: stepData
      })
    });
    
    if (response.ok) {
      this.currentStep++;
      return response.json();
    }
    
    throw new Error('Form submission failed');
  }
  
  async getProgress() {
    const response = await fetch(`/api/exchanges/${this.exchangeId}/form_progress/`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    
    return response.json();
  }
}
```

## Manager Workflows

### 1. Review Applications

```python
import requests

class ApplicationReviewer:
    def __init__(self, api_url, token):
        self.api_url = api_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def get_pending_applications(self):
        """Get all applications awaiting review"""
        response = requests.get(
            f'{self.api_url}/exchanges/',
            headers=self.headers,
            params={'status': 'submitted'}
        )
        return response.json()['results']
    
    def start_review(self, exchange_id):
        """Move application to under_review status"""
        return requests.post(
            f'{self.api_url}/exchanges/{exchange_id}/transition/',
            headers=self.headers,
            json={
                'status': 'under_review',
                'comment': 'Starting review process'
            }
        ).json()
    
    def check_documents(self, exchange_id):
        """Verify all required documents are present"""
        response = requests.get(
            f'{self.api_url}/documents/',
            headers=self.headers,
            params={'exchange': exchange_id}
        )
        
        documents = response.json()['results']
        required_types = ['passport', 'transcript', 'motivation_letter', 'recommendation']
        
        missing = []
        for doc_type in required_types:
            if not any(d['document_type'] == doc_type for d in documents):
                missing.append(doc_type)
        
        return {
            'complete': len(missing) == 0,
            'missing': missing,
            'documents': documents
        }
    
    def approve_application(self, exchange_id):
        """Approve the application and generate acceptance letter"""
        # First approve
        transition_response = requests.post(
            f'{self.api_url}/exchanges/{exchange_id}/transition/',
            headers=self.headers,
            json={
                'status': 'approved',
                'comment': 'All requirements met. Application approved.'
            }
        )
        
        # Generate acceptance letter
        document_response = requests.post(
            f'{self.api_url}/exchanges/{exchange_id}/generate_document/',
            headers=self.headers,
            json={'document_type': 'acceptance_letter'}
        )
        
        return {
            'transition': transition_response.json(),
            'document': document_response.json()
        }
    
    def bulk_process(self, exchange_ids, action):
        """Process multiple applications at once"""
        return requests.post(
            f'{self.api_url}/exchanges/bulk_transition/',
            headers=self.headers,
            json={
                'exchange_ids': exchange_ids,
                'status': action,
                'comment': f'Bulk {action} processing'
            }
        ).json()

# Usage
reviewer = ApplicationReviewer('http://localhost:8000/api', manager_token)

# Get pending applications
pending = reviewer.get_pending_applications()

for app in pending:
    # Check documents
    doc_check = reviewer.check_documents(app['id'])
    
    if doc_check['complete']:
        # Start review
        reviewer.start_review(app['id'])
        
        # Approve if everything looks good
        result = reviewer.approve_application(app['id'])
        print(f"Approved {app['first_name']} {app['last_name']}")
    else:
        print(f"Missing documents for {app['id']}: {doc_check['missing']}")
```

## React Integration

### Complete React Application

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Configure axios
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [exchanges, setExchanges] = useState([]);
  
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      loadUserData();
    }
  }, []);
  
  const loadUserData = async () => {
    try {
      const response = await api.get('/auth/me/');
      setUser(response.data);
      await loadExchanges();
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };
  
  const loadExchanges = async () => {
    try {
      const response = await api.get('/exchanges/');
      setExchanges(response.data.results);
    } catch (error) {
      console.error('Failed to load exchanges:', error);
    }
  };
  
  if (!user) {
    return <LoginForm onLogin={loadUserData} />;
  }
  
  return (
    <div className="app">
      <Header user={user} onLogout={() => setUser(null)} />
      <ExchangeList exchanges={exchanges} onUpdate={loadExchanges} />
    </div>
  );
}

// Exchange Status Tracker Component
function ExchangeStatusTracker({ exchange }) {
  const [documents, setDocuments] = useState([]);
  const [workflowHistory, setWorkflowHistory] = useState([]);
  const [availableTransitions, setAvailableTransitions] = useState([]);
  
  useEffect(() => {
    loadExchangeDetails();
  }, [exchange.id]);
  
  const loadExchangeDetails = async () => {
    try {
      // Load documents
      const docsResponse = await api.get(`/documents/`, {
        params: { exchange: exchange.id }
      });
      setDocuments(docsResponse.data.results);
      
      // Load workflow history
      const historyResponse = await api.get(`/exchanges/${exchange.id}/workflow_history/`);
      setWorkflowHistory(historyResponse.data.history);
      
      // Load available transitions
      const transitionsResponse = await api.get(`/exchanges/${exchange.id}/available_transitions/`);
      setAvailableTransitions(transitionsResponse.data.available_transitions);
    } catch (error) {
      console.error('Failed to load exchange details:', error);
    }
  };
  
  const performTransition = async (newStatus) => {
    try {
      const response = await api.post(`/exchanges/${exchange.id}/transition/`, {
        status: newStatus,
        comment: 'Status update'
      });
      
      // Reload exchange details
      await loadExchangeDetails();
    } catch (error) {
      console.error('Failed to perform transition:', error);
    }
  };
  
  return (
    <div className="exchange-status-tracker">
      <h3>{exchange.destination_university}</h3>
      <p>Current Status: <strong>{exchange.status}</strong></p>
      
      <div className="documents-section">
        <h4>Documents ({documents.length})</h4>
        <ul>
          {documents.map(doc => (
            <li key={doc.id}>
              {doc.title} - {doc.document_type}
              <a href={`/api/documents/${doc.id}/download/`}>Download</a>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="workflow-section">
        <h4>Available Actions</h4>
        {availableTransitions.map(transition => (
          <button
            key={transition.to_status}
            onClick={() => performTransition(transition.to_status)}
          >
            {transition.label}
          </button>
        ))}
      </div>
      
      <div className="history-section">
        <h4>Status History</h4>
        <ul>
          {workflowHistory.map(entry => (
            <li key={entry.id}>
              {entry.to_status} - {new Date(entry.transitioned_at).toLocaleDateString()}
              <br />
              <small>{entry.comment}</small>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
```

## Testing Examples

### Python Test Suite

```python
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from exchange.models import Exchange
from django.core.files.uploadedfile import SimpleUploadedFile

class ExchangeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_create_exchange(self):
        self.client.force_authenticate(user=self.user)
        
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'university': 'Test University',
            'destination_university': 'Partner University',
            'exchange_type': 'semester',
            'start_date': '2025-09-01',
            'end_date': '2026-01-31'
        }
        
        response = self.client.post('/api/exchanges/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'draft')
        
    def test_workflow_transition(self):
        self.client.force_authenticate(user=self.user)
        
        # Create exchange
        exchange = Exchange.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            university='Test University',
            destination_university='Partner University',
            exchange_type='semester',
            start_date='2025-09-01',
            end_date='2026-01-31'
        )
        
        # Transition to submitted
        response = self.client.post(
            f'/api/exchanges/{exchange.id}/transition/',
            {'status': 'submitted', 'comment': 'Ready for review'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'submitted')
        
    def test_document_upload(self):
        self.client.force_authenticate(user=self.user)
        
        # Create exchange first
        exchange = Exchange.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            university='Test University',
            destination_university='Partner University',
            exchange_type='semester',
            start_date='2025-09-01',
            end_date='2026-01-31'
        )
        
        # Create test file
        test_file = SimpleUploadedFile(
            'test_document.pdf',
            b'fake pdf content',
            content_type='application/pdf'
        )
        
        # Upload document
        response = self.client.post(
            '/api/documents/',
            {
                'file': test_file,
                'exchange': exchange.id,
                'document_type': 'passport',
                'title': 'Test Passport'
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['document_type'], 'passport')

class WorkflowPermissionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='pass123'
        )
        self.manager = User.objects.create_user(
            username='manager@example.com',
            email='manager@example.com',
            password='pass123',
            is_staff=True
        )
        
    def test_student_cannot_approve(self):
        self.client.force_authenticate(user=self.student)
        
        exchange = Exchange.objects.create(
            user=self.student,
            first_name='Test',
            last_name='Student',
            status='under_review'
        )
        
        response = self.client.post(
            f'/api/exchanges/{exchange.id}/transition/',
            {'status': 'approved'}
        )
        
        self.assertEqual(response.status_code, 403)
        
    def test_manager_can_approve(self):
        self.client.force_authenticate(user=self.manager)
        
        exchange = Exchange.objects.create(
            user=self.student,
            first_name='Test',
            last_name='Student',
            status='under_review'
        )
        
        response = self.client.post(
            f'/api/exchanges/{exchange.id}/transition/',
            {'status': 'approved', 'comment': 'Approved by manager'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'approved')
```

### End-to-End Test

```python
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ExchangeApplicationE2ETest:
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.base_url = "http://localhost:3000"
        
    def tearDown(self):
        self.driver.quit()
        
    def test_complete_application_flow(self):
        driver = self.driver
        driver.get(self.base_url)
        
        # Login
        driver.find_element(By.ID, "email").send_keys("student@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "login-button").click()
        
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "create-application"))
        )
        
        # Create new application
        driver.find_element(By.ID, "create-application").click()
        
        # Fill form
        driver.find_element(By.ID, "first_name").send_keys("John")
        driver.find_element(By.ID, "last_name").send_keys("Doe")
        driver.find_element(By.ID, "university").send_keys("Home University")
        driver.find_element(By.ID, "destination_university").send_keys("Partner University")
        
        # Select exchange type
        select = Select(driver.find_element(By.ID, "exchange_type"))
        select.select_by_value("semester")
        
        # Set dates
        driver.find_element(By.ID, "start_date").send_keys("09/01/2025")
        driver.find_element(By.ID, "end_date").send_keys("01/31/2026")
        
        # Submit form
        driver.find_element(By.ID, "submit-form").click()
        
        # Upload document
        driver.find_element(By.ID, "upload-document").send_keys("/path/to/passport.pdf")
        
        # Submit application
        driver.find_element(By.ID, "submit-application").click()
        
        # Verify success message
        success_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        assert "Application submitted successfully" in success_message.text
```

## Common Patterns

### Pagination Handling

```javascript
async function getAllExchanges(token) {
  let allExchanges = [];
  let nextUrl = '/api/exchanges/';
  
  while (nextUrl) {
    const response = await fetch(nextUrl, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    allExchanges = [...allExchanges, ...data.results];
    nextUrl = data.next;
  }
  
  return allExchanges;
}
```

### Error Recovery

```javascript
async function apiRequestWithRetry(url, options, maxRetries = 3) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (response.status === 401) {
        // Token expired, try to refresh
        await refreshToken();
        options.headers.Authorization = `Bearer ${getToken()}`;
        continue;
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      lastError = error;
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
  
  throw lastError;
}
```

### File Progress Tracking

```javascript
function uploadWithProgress(file, exchangeId, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    
    formData.append('file', file);
    formData.append('exchange', exchangeId);
    formData.append('document_type', 'passport');
    
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        onProgress(percentComplete);
      }
    });
    
    xhr.addEventListener('load', () => {
      if (xhr.status === 201) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        reject(new Error('Upload failed'));
      }
    });
    
    xhr.addEventListener('error', () => {
      reject(new Error('Network error'));
    });
    
    xhr.open('POST', '/api/documents/');
    xhr.setRequestHeader('Authorization', `Bearer ${getToken()}`);
    xhr.send(formData);
  });
}

// Usage
const fileInput = document.getElementById('file-input');
const progressBar = document.getElementById('progress-bar');

fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  
  try {
    const result = await uploadWithProgress(file, exchangeId, (progress) => {
      progressBar.style.width = `${progress}%`;
      progressBar.textContent = `${Math.round(progress)}%`;
    });
    
    console.log('Upload complete:', result);
  } catch (error) {
    console.error('Upload failed:', error);
  }
});
```

### WebSocket Integration for Real-time Updates

```javascript
class ExchangeWebSocket {
  constructor(exchangeId, token) {
    this.exchangeId = exchangeId;
    this.token = token;
    this.websocket = null;
    this.handlers = {};
  }
  
  connect() {
    const wsUrl = `ws://localhost:8000/ws/exchanges/${this.exchangeId}/?token=${this.token}`;
    this.websocket = new WebSocket(wsUrl);
    
    this.websocket.onopen = () => {
      console.log('WebSocket connected');
    };
    
    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.websocket.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.connect(), 5000);
    };
  }
  
  handleMessage(data) {
    const { type, payload } = data;
    
    if (this.handlers[type]) {
      this.handlers[type](payload);
    }
  }
  
  on(eventType, handler) {
    this.handlers[eventType] = handler;
  }
  
  send(type, payload) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({ type, payload }));
    }
  }
  
  disconnect() {
    if (this.websocket) {
      this.websocket.close();
    }
  }
}

// Usage
const ws = new ExchangeWebSocket(exchangeId, token);

ws.on('status_changed', (data) => {
  console.log('Status changed to:', data.new_status);
  updateUI(data);
});

ws.on('document_uploaded', (data) => {
  console.log('New document uploaded:', data.document_name);
  addDocumentToList(data);
});

ws.connect();
```

## Summary

These examples demonstrate:

1. Complete application workflows for students and managers
2. Integration with popular frontend frameworks
3. Testing strategies and patterns
4. Error handling and recovery
5. Advanced features like pagination, file uploads with progress, and real-time updates

The SEIM API is designed to be flexible and easy to integrate with any frontend technology stack while maintaining security and data integrity throughout the exchange application process.
