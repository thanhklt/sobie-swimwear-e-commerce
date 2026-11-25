# N04 — GET /api/v1/inventory/staff/suppliers/{supplier_key}/edit

Coverage: UC-32 AC-6,7. Authority: Inventory Todoist endpoint N04 and specs/use-cases/inventory/.

```mermaid
sequenceDiagram
    actor Staff
    participant Web as Session middleware / Inventory route
    participant Identity as Identity public service
    participant Service as Inventory service
    participant Repo as Inventory repository
    participant DB as PostgreSQL
    Staff->>Web: GET /api/v1/inventory/staff/suppliers/{supplier_key}/edit
    Web->>Identity: authenticate portal_session and renew valid session
    Identity-->>Web: current account and role
    Web->>Web: require EMPLOYEE (Admin/Customer denied)
    Web->>Service: get_supplier(supplier_key)
    Service->>DB: BEGIN (shared transaction)
    Service->>Repo: read supplier including inactive; 404 if missing
    Repo->>DB: SELECT Inventory-owned rows
    DB-->>Repo: current rows
    Repo-->>Service: result
    Service->>DB: COMMIT
    Service-->>Web: result
    Web-->>Staff: 200 full HTML or HTMX fragment
    Note over Service,DB: Database write/commit failure rolls back entire transaction; no success or cache increment.
    Note over Web,Staff: Cache-Control no-store; Vary HX-Request; private DOM history disabled.
```

Invalid filters/page/UUID: 400 where applicable; missing entity: 404; data-access failure: 503. Unauthenticated requests use the shared portal-login/error flow; authenticated Admin and Customer requests are denied (403).

read supplier including inactive; 404 if missing.
