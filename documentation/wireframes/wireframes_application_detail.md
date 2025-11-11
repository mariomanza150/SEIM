# SEIM Application Detail Wireframe

---

## Student View

```mermaid
flowchart TD
    A["Application Detail"] --> B["Status Timeline (Read-only)"]
    A --> C["Submitted Documents"]
    A --> D["Coordinator/Admin Comments"]
    D --> E["Respond to Comment (Once)"]
    A --> F["Withdraw (if Draft)"]
```

---

## Coordinator/Admin View

```mermaid
flowchart TD
    A["Application Detail"] --> B["Status Timeline (Editable)"]
    A --> C["Submitted Documents"]
    C --> D["Request Resubmission"]
    C --> E["Leave Comment (Mark as Private/Visible)"]
    A --> F["Change Status"]
    A --> G["Add Internal Note"]
    A --> H["View Student Response"]
    A --> I["View/Restore Cancelled Applications"]
```

---

This wireframe outlines the main elements and actions for the application detail view for each role. 