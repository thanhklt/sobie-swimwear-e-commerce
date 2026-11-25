# N02 — GET /api/v1/inventory/staff/suppliers/new

Coverage: UC-32 AC-1,2. Authority: Inventory Todoist endpoint N02 and specs/use-cases/inventory/.

```mermaid
sequenceDiagram
    actor Staff
    participant Web as Session middleware / Inventory route
    participant Identity as Identity public service
    participant Service as Inventory service
    participant Repo as Inventory repository
    participant DB as PostgreSQL
    Staff->>Web: GET /api/v1/inventory/staff/suppliers/new
    Web->>Identity: authenticate portal_session and renew valid session
    Identity-->>Web: current account and role
    Web->>Web: require EMPLOYEE (Admin/Customer denied)
    Web-->>Staff: 200 supplier form
    Note over Web,Staff: Cache-Control no-store; Vary HX-Request; private DOM history disabled.
```

Invalid filters/page/UUID: 400 where applicable; missing entity: 404; data-access failure: 503. Unauthenticated requests use the shared portal-login/error flow; authenticated Admin and Customer requests are denied (403).

render empty supplier form.
