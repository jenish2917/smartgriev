# 🤝 Contributing to SmartGriev

Thank you for your interest in contributing to SmartGriev! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- Git installed
- Python 3.10+ installed
- Node.js 18+ installed
- Basic knowledge of Django and React
- Gmail account for testing emails
- Google Gemini API key

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/smartgriev.git
   cd smartgriev
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/jenish2917/smartgriev.git
   ```

---

## 💻 Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/local.txt

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend-new

# Install dependencies
npm install

# Run development server
npm run dev
```

---

## 🔄 Contribution Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
# Update your fork
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add/update tests as needed
- Update documentation

### 3. Test Your Changes

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend-new
npm run test
```

### 4. Commit Changes

Follow the commit message guidelines (see below):

```bash
git add .
git commit -m "feat: add email notification for resolved complaints"
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Go to your fork on GitHub
- Click "New Pull Request"
- Select your feature branch
- Fill in the PR template
- Submit the PR

---

## 📏 Coding Standards

### Python (Backend)

Follow **PEP 8** style guide:

```python
# Good
def send_email_notification(user, complaint):
    """Send email notification to user about complaint status."""
    if not user.email:
        logger.warning(f"User {user.id} has no email address")
        return False
    
    return email_service.send_notification(user, complaint)

# Bad
def sendEmailNotification(user,complaint):
    if not user.email: return False
    return email_service.send_notification(user,complaint)
```

**Guidelines:**
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use docstrings for functions and classes
- Use type hints where appropriate
- Organize imports: standard library, third-party, local

**Example:**
```python
from typing import Optional, Dict, List
from django.db import models
from django.conf import settings

from complaints.models import Complaint
from .email_service import email_service
```

### JavaScript/TypeScript (Frontend)

Follow **ESLint** configuration:

```typescript
// Good
interface User {
  id: number;
  username: string;
  email: string;
}

const fetchUserComplaints = async (userId: number): Promise<Complaint[]> => {
  try {
    const response = await complaintApi.getComplaints();
    return response.results;
  } catch (error) {
    console.error('Failed to fetch complaints:', error);
    throw error;
  }
};

// Bad
function fetchUserComplaints(userId) {
  return complaintApi.getComplaints().then(response => response.results)
}
```

**Guidelines:**
- Use 2 spaces for indentation
- Use semicolons
- Prefer `const` over `let`, avoid `var`
- Use arrow functions
- Use TypeScript types
- Use meaningful variable names

---

## 💬 Commit Guidelines

We follow **Conventional Commits** specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

### Examples

```bash
# Feature
git commit -m "feat(chatbot): add voice input support"

# Bug fix
git commit -m "fix(auth): resolve JWT token expiration issue"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Refactoring
git commit -m "refactor(complaints): improve query performance"

# With body
git commit -m "feat(email): add complaint resolution notifications

- Implement email template for resolved complaints
- Add user preference check
- Update notification signals
- Add tests for email delivery"
```

---

## 🔍 Pull Request Process

### Before Submitting

- ✅ All tests pass
- ✅ Code follows style guidelines
- ✅ Documentation is updated
- ✅ Commit messages follow conventions
- ✅ Branch is up-to-date with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test the changes

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Self-review completed
```

### Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged

---

## 🧪 Testing

### Writing Tests

**Backend (pytest):**

```python
# backend/complaints/tests/test_email_notifications.py
from django.test import TestCase
from authentication.models import User
from complaints.models import Complaint
from notifications.email_service import email_service

class EmailNotificationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_complaint_created_email(self):
        """Test email sent when complaint is created"""
        complaint = Complaint.objects.create(
            user=self.user,
            title='Test complaint',
            description='Test description',
            status='pending'
        )
        
        result = email_service.send_complaint_created_email(
            user=self.user,
            complaint=complaint
        )
        
        self.assertTrue(result['success'])
```

**Frontend (Vitest):**

```typescript
// frontend-new/src/components/Button.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    screen.getByText('Click').click();
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

### Running Tests

```bash
# Backend
cd backend
python manage.py test
python manage.py test complaints

# Frontend
cd frontend-new
npm run test
npm run test:watch
npm run test:coverage
```

---

## 📚 Documentation

### Code Documentation

**Python (Docstrings):**

```python
def send_complaint_notification(user, complaint, notification_type):
    """
    Send notification to user about complaint status.
    
    Args:
        user (User): The user to notify
        complaint (Complaint): The complaint object
        notification_type (str): Type of notification ('created', 'updated', 'resolved')
    
    Returns:
        dict: Result with 'success' boolean and optional 'error' message
    
    Raises:
        ValueError: If notification_type is invalid
    
    Example:
        >>> send_complaint_notification(user, complaint, 'created')
        {'success': True, 'message': 'Email sent successfully'}
    """
    pass
```

**TypeScript (JSDoc):**

```typescript
/**
 * Fetch user complaints from API
 * 
 * @param userId - The ID of the user
 * @param filters - Optional filters for complaints
 * @returns Promise resolving to array of complaints
 * @throws {Error} If API request fails
 * 
 * @example
 * ```ts
 * const complaints = await fetchComplaints(123, { status: 'pending' });
 * ```
 */
async function fetchComplaints(
  userId: number,
  filters?: ComplaintFilters
): Promise<Complaint[]> {
  // implementation
}
```

### Feature Documentation

When adding new features, create documentation in `docs/features/`:

```markdown
# Feature Name

## Overview
Brief description

## Usage
How to use the feature

## API
API endpoints

## Configuration
Required settings

## Examples
Code examples
```

---

## 🐛 Reporting Bugs

### Before Reporting

- Check existing issues
- Verify bug exists in latest version
- Gather relevant information

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11]
- Browser: [e.g., Chrome 120]
- Python: [e.g., 3.10]
- Node: [e.g., 18.17]

## Screenshots
If applicable

## Additional Context
Any other relevant information
```

---

## 💡 Feature Requests

We welcome feature suggestions! Please provide:

1. **Use case**: Why is this needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Additional context**: Mockups, examples, etc.

---

## 📞 Getting Help

- **Email**: jenishbarvaliya.it22@scet.ac.in
- **Issues**: [GitHub Issues](https://github.com/jenish2917/smartgriev/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jenish2917/smartgriev/discussions)

---

## 🙏 Recognition

Contributors will be acknowledged in:

- Release notes
- CONTRIBUTORS.md file
- GitHub contributors page

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

<div align="center">

**Thank you for contributing to SmartGriev! 🎉**

Every contribution, no matter how small, makes a difference!

</div>
