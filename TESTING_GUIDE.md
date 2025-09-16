# AgentAI Testing Guide - Playwright MCP Integration

## Overview
This guide provides comprehensive testing scenarios for the AgentAI platform using Playwright MCP. The tests cover security fixes, UI functionality, and end-to-end workflows.

## Test Environment Setup

### Prerequisites
- AgentAI platform running on `http://localhost:8000`
- Ollama service running with `llama3.1:8b` model
- Playwright MCP configured and connected

### Test Data
```json
{
  "testProject": {
    "name": "Test E-commerce App",
    "description": "A simple e-commerce application with user authentication",
    "features": ["User registration", "Product catalog", "Shopping cart"],
    "constraints": "Use Python Flask, SQLite database"
  },
  "maliciousInputs": {
    "xss": "<script>alert('XSS')</script>",
    "injection": "'; DROP TABLE projects; --",
    "html": "<img src=x onerror=alert('XSS')>"
  }
}
```

## Test Scenarios

### 1. Security Testing (Critical Priority)

#### 1.1 XSS Prevention Test
**Objective**: Verify HTML sanitization prevents XSS attacks
**URL**: `http://localhost:8000`

**Steps**:
1. Navigate to project creation form
2. Enter malicious script in project name: `<script>alert('XSS')</script>`
3. Enter malicious HTML in description: `<img src=x onerror=alert('XSS')>`
4. Submit form
5. Verify no alert dialogs appear
6. Check that content is properly escaped in DOM

**Expected Result**: Malicious scripts are sanitized, no JavaScript execution

#### 1.2 Code Injection Prevention Test
**Objective**: Verify input validation prevents code injection
**URL**: `http://localhost:8000/api/projects`

**Steps**:
1. Intercept API requests
2. Modify project data to include injection payloads
3. Submit malicious payloads: `'; DROP TABLE projects; --`
4. Verify server responds with validation errors
5. Check that no code execution occurs

**Expected Result**: Server rejects malicious input with proper error messages

#### 1.3 Secure Notification System Test
**Objective**: Verify notification system uses secure methods
**URL**: `http://localhost:8000`

**Steps**:
1. Trigger various notifications (success, error, info)
2. Verify notifications appear in designated container
3. Check that no `alert()` or `confirm()` dialogs are used
4. Verify notification content is properly escaped

**Expected Result**: All notifications use secure DOM-based system

### 2. UI/UX Testing

#### 2.1 Design Language Consistency Test
**Objective**: Verify UI follows unified design language
**URL**: `http://localhost:8000`

**Steps**:
1. Navigate through all pages
2. Verify color palette consistency (brand blue `#007bff`)
3. Check typography uses consistent font family and scale
4. Verify button styles (primary, secondary, ghost)
5. Check card components have consistent styling
6. Verify modal overlays and animations

**Expected Result**: All UI elements follow design system specifications

#### 2.2 Modal Functionality Test
**Objective**: Test modal behavior and accessibility
**URL**: `http://localhost:8000`

**Steps**:
1. Open project creation modal
2. Verify modal overlay appears with proper styling
3. Test modal close functionality (X button, ESC key)
4. Verify modal is centered and responsive
5. Check modal animations (fade-in/slide-up)
6. Test form validation within modal

**Expected Result**: Modal functions correctly with proper UX

#### 2.3 Responsive Design Test
**Objective**: Verify responsive behavior across devices
**URL**: `http://localhost:8000`

**Steps**:
1. Test on desktop viewport (1920x1080)
2. Test on tablet viewport (768x1024)
3. Test on mobile viewport (375x667)
4. Verify grid system adapts properly
5. Check button and card scaling
6. Verify navigation remains functional

**Expected Result**: UI adapts seamlessly across all viewports

### 3. Functional Testing

#### 3.1 Project Creation Workflow Test
**Objective**: Test complete project creation flow
**URL**: `http://localhost:8000`

**Steps**:
1. Click "Create New Project" button
2. Fill project form with valid data
3. Submit form and verify project appears in dashboard
4. Check project status updates in real-time
5. Verify kanban board reflects project state
6. Test project deletion functionality

**Expected Result**: Project lifecycle works end-to-end

#### 3.2 AI Analysis Workflow Test
**Objective**: Test AI requirements analysis
**URL**: `http://localhost:8000`

**Steps**:
1. Create project with specific requirements
2. Wait for AI analysis phase to complete
3. Verify technology stack recommendations appear
4. Test approval/rejection workflow
5. Check that rework requests function properly
6. Verify progress tracking updates

**Expected Result**: AI analysis workflow completes successfully

#### 3.3 Real-time Updates Test
**Objective**: Verify real-time dashboard updates
**URL**: `http://localhost:8000`

**Steps**:
1. Open dashboard in multiple browser tabs
2. Create project in one tab
3. Verify updates appear in other tabs
4. Test WebSocket connection stability
5. Check progress bar updates in real-time
6. Verify status changes propagate correctly

**Expected Result**: Real-time updates work across all clients

### 4. API Testing

#### 4.1 Project API Endpoints Test
**Objective**: Test all project-related API endpoints
**Base URL**: `http://localhost:8000/api`

**Endpoints to Test**:
- `GET /projects` - List all projects
- `POST /projects` - Create new project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `POST /projects/{id}/approve` - Approve AI recommendations
- `POST /projects/{id}/reject` - Reject AI recommendations

**Steps**:
1. Test each endpoint with valid data
2. Test with invalid/malicious data
3. Verify proper HTTP status codes
4. Check response data structure
5. Test authentication/authorization
6. Verify error handling

**Expected Result**: All APIs function correctly with proper validation

#### 4.2 WebSocket Connection Test
**Objective**: Test real-time WebSocket functionality
**URL**: `ws://localhost:8000/ws`

**Steps**:
1. Establish WebSocket connection
2. Verify connection acknowledgment
3. Test message broadcasting
4. Check connection recovery after disconnect
5. Verify message format and structure
6. Test concurrent connections

**Expected Result**: WebSocket communication works reliably

### 5. Performance Testing

#### 5.1 Page Load Performance Test
**Objective**: Verify acceptable page load times
**URL**: `http://localhost:8000`

**Steps**:
1. Measure initial page load time
2. Check resource loading (CSS, JS, images)
3. Verify Time to First Contentful Paint (FCP)
4. Check Largest Contentful Paint (LCP)
5. Measure Cumulative Layout Shift (CLS)
6. Test with network throttling

**Expected Result**: Page loads within 3 seconds on 3G connection

#### 5.2 AI Processing Performance Test
**Objective**: Test AI agent processing times
**URL**: `http://localhost:8000`

**Steps**:
1. Create multiple projects simultaneously
2. Monitor processing queue behavior
3. Verify timeout handling
4. Check resource usage during processing
5. Test with various project complexities
6. Verify progress reporting accuracy

**Expected Result**: AI processing completes within reasonable timeframes

### 6. Error Handling Testing

#### 6.1 Network Error Handling Test
**Objective**: Test behavior during network issues
**URL**: `http://localhost:8000`

**Steps**:
1. Simulate network disconnection
2. Attempt to create/update projects
3. Verify error messages are user-friendly
4. Test automatic retry mechanisms
5. Check offline state handling
6. Verify recovery after reconnection

**Expected Result**: Graceful error handling with clear user feedback

#### 6.2 Server Error Handling Test
**Objective**: Test behavior during server errors
**URL**: `http://localhost:8000`

**Steps**:
1. Simulate server 500 errors
2. Test with invalid API responses
3. Verify error boundaries prevent crashes
4. Check error logging and reporting
5. Test fallback mechanisms
6. Verify user notification of issues

**Expected Result**: Application remains stable during server issues

## Playwright MCP Test Commands

### Basic Navigation Tests
```javascript
// Navigate to dashboard
await page.goto('http://localhost:8000');
await expect(page).toHaveTitle(/AgentAI/);

// Test project creation modal
await page.click('[data-testid="create-project-btn"]');
await expect(page.locator('.modal-overlay')).toBeVisible();
```

### Security Tests
```javascript
// XSS prevention test
await page.fill('[data-testid="project-name"]', '<script>alert("XSS")</script>');
await page.click('[data-testid="submit-btn"]');
await expect(page.locator('script')).toHaveCount(0);
```

### UI Consistency Tests
```javascript
// Check design system colors
const primaryButton = page.locator('[data-testid="primary-btn"]');
await expect(primaryButton).toHaveCSS('background-color', 'rgb(0, 123, 255)');
```

## Test Execution Checklist

- [ ] Security tests pass (XSS, injection, notifications)
- [ ] UI/UX follows design language specifications
- [ ] All functional workflows complete successfully
- [ ] API endpoints respond correctly
- [ ] Real-time updates work properly
- [ ] Performance meets acceptable thresholds
- [ ] Error handling is graceful and informative
- [ ] Responsive design works across devices
- [ ] Accessibility standards are met
- [ ] Cross-browser compatibility verified

## Test Reporting

### Success Criteria
- All security vulnerabilities are properly mitigated
- UI components follow unified design language
- End-to-end workflows complete without errors
- Performance metrics meet defined thresholds
- Error handling provides clear user feedback

### Failure Investigation
1. Capture screenshots of failed tests
2. Record network activity during failures
3. Check browser console for errors
4. Verify server logs for backend issues
5. Document reproduction steps
6. Create bug reports with detailed information

## Continuous Testing Integration

### Pre-commit Hooks
- Run security tests before code commits
- Validate UI component consistency
- Check API endpoint functionality

### CI/CD Pipeline
- Automated test execution on pull requests
- Performance regression testing
- Cross-browser compatibility checks
- Security vulnerability scanning

This comprehensive testing guide ensures the AgentAI platform maintains high quality, security, and user experience standards while leveraging Playwright MCP for automated testing capabilities.