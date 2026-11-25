# N10 — POST /api/v1/inventory/staff/goods-receipts/new

Coverage: UC-33 AC-1–4,6. Authority: Inventory Todoist endpoint N10 and specs/use-cases/inventory/.

```mermaid
sequenceDiagram
    actor Staff
    participant Web as Session middleware / Inventory route
    participant Identity as Identity public service
    participant Service as Inventory service
    participant Repo as Inventory repository
    participant DB as PostgreSQL
    Staff->>Web: POST /api/v1/inventory/staff/goods-receipts/new
    Web->>Identity: authenticate portal_session and renew valid session
    Identity-->>Web: current account and role
    Web->>Web: require EMPLOYEE (Admin/Customer denied)
    Web->>Web: require same Origin; parse and validate form
    Web->>Service: save_receipt(ReceiptInput,account_key)
    Service->>DB: BEGIN (shared transaction)
    participant Catalog as Catalog public service
    participant CatalogRepo as Catalog repository
    Service->>Catalog: metadata / variants / categories (same session)
    Catalog->>CatalogRepo: read Catalog-owned tables only
    CatalogRepo->>DB: SELECT current metadata / stable filtered page
    Service->>Repo: lock supplier and require ACTIVE; validate variants via Catalog; allocate PN sequence; insert DRAFT header and all details
    Repo->>DB: lock / validate / write Inventory-owned rows
    DB-->>Repo: current rows
    Repo-->>Service: result
    Service->>DB: COMMIT
    Service-->>Web: result
    Web-->>Staff: 303 supplier list or receipt detail
    Note over Service,DB: Database write/commit failure rolls back entire transaction; no success or cache increment.
    Note over Web,Staff: Cache-Control no-store; Vary HX-Request; private DOM history disabled.
```

Input errors: 400; missing entity: 404; business conflict: 409; persistence failure: 503. Destructive/status actions require `confirm=yes`. Unauthenticated requests use the shared portal-login/error flow; authenticated Admin and Customer requests are denied (403).

lock supplier and require ACTIVE; validate variants via Catalog; allocate PN sequence; insert DRAFT header and all details.
