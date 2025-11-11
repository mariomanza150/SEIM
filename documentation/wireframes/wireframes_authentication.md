# SEIM Authentication Wireframes

---

## Login Flow

```mermaid
flowchart TD
    A["Login Page"] --> B["Email (Institutional)"]
    A --> C["Password"]
    A --> D["Language Selector"]
    A --> E["Forgot Password?"]
    A --> F["Login Button"]
    A -.-> G["Future: Social Login"]
    F --> H["Account Lockout after 10 failed attempts"]
    H --> I["Reactivate via Email or Admin"]
```

---

## Registration Flow (Student)

```mermaid
flowchart TD
    A["Registration Page"] --> B["Institutional Email"]
    A --> C["Password (Strength Requirements)"]
    A --> D["Confirm Password"]
    A --> E["Language Selector"]
    A --> F["Register Button"]
    F --> G["Email Verification Sent"]
    G --> H["Verify Email Link"]
    H --> I["Account Activated"]
```

---

## Password Reset Flow

```mermaid
flowchart TD
    A["Forgot Password Page"] --> B["Enter Email"]
    A --> C["Language Selector"]
    B --> D["Send Reset Link"]
    D --> E["Email with Reset Link"]
    E --> F["Set New Password (Strength Requirements)"]
    F --> G["Password Updated"]
```

---

## Profile Update Flow

```mermaid
flowchart TD
    A["Profile Page"] --> B["Update Name"]
    A --> C["Change Password"]
    A --> D["Add/Change Secondary Email"]
    A --> E["Primary Email (Institutional, Not Editable)"]
    A --> F["Language Selector"]
```

---

## Admin Account Management

```mermaid
flowchart TD
    A["Admin Panel"] --> B["Create Coordinator/Admin Account"]
    A --> C["Reactivate Locked Account"]
    C --> D["Send Reactivation Email"]
```

---

> Future plans: Social login and MFA may be added in later versions.

All authentication screens support language selection from the start. 