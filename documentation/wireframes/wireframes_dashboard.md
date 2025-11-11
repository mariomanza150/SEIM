# SEIM Dashboard Wireframes

Below are simple wireframes for the main dashboard, tailored to each user role.

---

## Student Dashboard

```mermaid
flowchart TD
    A["Dashboard"] --> B["My Applications List"]
    A --> C["Available Exchange Programs"]
    A --> D["Notifications"]
    B --> E["Application Status"]
    B --> F["Upload Documents"]
    B --> G["Post-Exchange Actions"]
```

---

## Coordinator Dashboard

```mermaid
flowchart TD
    A["Dashboard"] --> B["Applications to Review"]
    A --> C["Notifications"]
    B --> D["View Application Details"]
    D --> E["Review Documents"]
    D --> F["Leave Comments"]
    D --> G["Change Status"]
    A --> H["Submit New Program (Draft)"]
```

---

## Admin Dashboard

```mermaid
flowchart TD
    A["Dashboard"] --> B["Analytics Widget"]
    A --> C["All Applications"]
    A --> D["Exchange Program Management"]
    A --> E["Notifications"]
    A --> F["Application Form Builder"]
    A --> G["Document Type/Format Config"]
    B --> H["# Students"]
    B --> I["# Ongoing Applications"]
    B --> J["# Approved"]
    B --> K["# Rejected"]
    C --> L["Override Status"]
    D --> M["Create/Edit Programs"]
```

---

These wireframes provide a high-level overview of the dashboard experience for each role. 