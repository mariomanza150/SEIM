# E2E Test IDs Guide

## Overview

This guide explains how to add and use `data-testid` attributes for reliable E2E testing.

## Why data-testid?

- **Stability**: Not affected by styling changes
- **Clarity**: Makes test intent clear
- **Performance**: Faster than complex CSS selectors
- **Maintainability**: Easy to update when UI changes

## Naming Convention

Use descriptive, lowercase, hyphenated names:

```html
<!-- Good -->
<button data-testid="submit-application">Submit</button>
<input data-testid="username-input" />
<div data-testid="applications-list"></div>

<!-- Bad -->
<button data-testid="btn1">Submit</button>
<input data-testid="input_field" />
<div data-testid="div123"></div>
```

## Common Patterns

### Forms

```html
<!-- Login form -->
<form data-testid="login-form">
    <input name="username" data-testid="username-input" />
    <input name="password" data-testid="password-input" type="password" />
    <button type="submit" data-testid="login-submit">Login</button>
</form>

<!-- Registration form -->
<form data-testid="register-form">
    <input name="email" data-testid="email-input" />
    <input name="username" data-testid="username-input" />
    <input name="password" data-testid="password-input" type="password" />
    <input name="confirm_password" data-testid="confirm-password-input" type="password" />
    <input name="agree_terms" data-testid="agree-terms-checkbox" type="checkbox" />
    <button type="submit" data-testid="register-submit">Register</button>
</form>
```

### Navigation

```html
<!-- Main navigation -->
<nav data-testid="main-nav">
    <a href="/dashboard/" data-testid="nav-dashboard">Dashboard</a>
    <a href="/programs/" data-testid="nav-programs">Programs</a>
    <a href="/applications/" data-testid="nav-applications">Applications</a>
</nav>

<!-- User menu -->
<div data-testid="user-menu">
    <button data-testid="user-menu-button">Account</button>
    <div data-testid="user-menu-dropdown">
        <a href="/profile/" data-testid="menu-profile">Profile</a>
        <a href="/settings/" data-testid="menu-settings">Settings</a>
        <button data-testid="logout-button">Logout</button>
    </div>
</div>
```

### Lists and Cards

```html
<!-- Programs list -->
<div data-testid="programs-list">
    {% for program in programs %}
    <div class="program-card" data-testid="program-{{ program.id }}">
        <h3 data-testid="program-title">{{ program.name }}</h3>
        <p data-testid="program-description">{{ program.description }}</p>
        <button data-testid="view-program-{{ program.id }}">View Details</button>
    </div>
    {% endfor %}
</div>

<!-- Applications list -->
<div data-testid="applications-list">
    {% for application in applications %}
    <div class="application-card" data-testid="application-{{ application.id }}">
        <h4 data-testid="application-title">{{ application.program.name }}</h4>
        <span data-testid="application-status">{{ application.status }}</span>
        <button data-testid="edit-application-{{ application.id }}">Edit</button>
    </div>
    {% endfor %}
</div>
```

### Buttons and Actions

```html
<!-- Primary actions -->
<button data-testid="create-application">Create Application</button>
<button data-testid="submit-application">Submit</button>
<button data-testid="save-draft">Save Draft</button>
<button data-testid="cancel">Cancel</button>

<!-- Delete/destructive actions -->
<button data-testid="delete-application" class="btn-danger">Delete</button>
<button data-testid="withdraw-application">Withdraw</button>

<!-- Secondary actions -->
<button data-testid="edit-profile">Edit Profile</button>
<button data-testid="change-password">Change Password</button>
```

### Modals and Dialogs

```html
<!-- Modal -->
<div class="modal" data-testid="upload-modal" id="uploadModal">
    <div class="modal-header" data-testid="modal-header">
        <h5 data-testid="modal-title">Upload Document</h5>
        <button data-testid="modal-close" class="close">&times;</button>
    </div>
    <div class="modal-body" data-testid="modal-body">
        <input type="file" data-testid="file-input" />
        <select data-testid="document-type-select">
            <option>Select type...</option>
        </select>
    </div>
    <div class="modal-footer" data-testid="modal-footer">
        <button data-testid="modal-cancel">Cancel</button>
        <button data-testid="modal-submit">Upload</button>
    </div>
</div>
```

### Status and Notifications

```html
<!-- Status badges -->
<span class="badge" data-testid="status-badge">{{ status }}</span>
<span class="badge-count" data-testid="notifications-badge">5</span>

<!-- Alert messages -->
<div class="alert alert-success" data-testid="success-message">
    Success! Your application was submitted.
</div>
<div class="alert alert-danger" data-testid="error-message">
    Error: Please correct the form errors.
</div>

<!-- Loading indicators -->
<div class="spinner" data-testid="loading">Loading...</div>
```

### Tables

```html
<!-- Data table -->
<table data-testid="users-table">
    <thead data-testid="table-header">
        <tr>
            <th data-testid="header-username">Username</th>
            <th data-testid="header-email">Email</th>
            <th data-testid="header-role">Role</th>
            <th data-testid="header-actions">Actions</th>
        </tr>
    </thead>
    <tbody data-testid="table-body">
        {% for user in users %}
        <tr data-testid="user-{{ user.id }}">
            <td data-testid="user-username">{{ user.username }}</td>
            <td data-testid="user-email">{{ user.email }}</td>
            <td data-testid="user-role">{{ user.role }}</td>
            <td data-testid="user-actions">
                <button data-testid="edit-user-{{ user.id }}">Edit</button>
                <button data-testid="delete-user-{{ user.id }}">Delete</button>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

## Priority Elements

Add `data-testid` to these elements first:

### High Priority
- Form inputs and buttons
- Navigation links
- Primary action buttons
- Login/logout elements
- User menu

### Medium Priority
- List containers
- Card elements
- Modals and dialogs
- Status indicators
- Notifications

### Lower Priority
- Static text
- Decorative elements
- Footer links

## Templates to Update

Key templates that need data-testid attributes:

1. **templates/frontend/auth/login.html**
2. **templates/frontend/auth/register.html**
3. **templates/frontend/dashboard.html**
4. **templates/frontend/applications/list.html**
5. **templates/frontend/applications/form.html**
6. **templates/frontend/documents/list.html**
7. **templates/frontend/programs/list.html**
8. **templates/frontend/profile.html**
9. **templates/components/navigation/navbar.html**
10. **templates/frontend/admin/dashboard.html**

## Using in Tests

### Selecting Elements

```python
# In page objects
LOGIN_USERNAME_INPUT = '[data-testid="username-input"]'
SUBMIT_BUTTON = '[data-testid="submit-application"]'
APPLICATIONS_LIST = '[data-testid="applications-list"]'

# In tests
page.locator('[data-testid="login-submit"]').click()
page.fill('[data-testid="email-input"]', 'test@example.com')
expect(page.locator('[data-testid="success-message"]')).to_be_visible()
```

### Dynamic IDs

```python
# For items with dynamic IDs
def get_program_card(program_id):
    return f'[data-testid="program-{program_id}"]'

# Usage
page.locator(get_program_card(123)).click()
```

## Migration Strategy

1. **Phase 1**: Add to authentication pages (login, register)
2. **Phase 2**: Add to main navigation and dashboard
3. **Phase 3**: Add to applications and programs
4. **Phase 4**: Add to documents and profile
5. **Phase 5**: Add to admin and coordinator pages

## Checklist

- [ ] Login form
- [ ] Registration form
- [ ] Main navigation
- [ ] User menu
- [ ] Dashboard containers
- [ ] Programs list
- [ ] Application form
- [ ] Applications list
- [ ] Documents list
- [ ] Profile form
- [ ] Settings form
- [ ] Admin dashboard
- [ ] User management table
- [ ] Modals and dialogs
- [ ] Status indicators
- [ ] Notifications

## Best Practices

1. **Be Specific**: Use descriptive names
2. **Be Consistent**: Follow naming conventions
3. **Be Unique**: Each ID should be unique on the page
4. **Document**: Add comments for complex IDs
5. **Test**: Verify IDs work in E2E tests

## Examples

See `tests/e2e_playwright/examples/` for complete examples of using test IDs in tests.

