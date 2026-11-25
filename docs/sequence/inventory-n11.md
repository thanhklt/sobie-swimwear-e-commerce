# N11 — GET /api/v1/inventory/staff/goods-receipts/{receipt_key}

Coverage: UC-33 AC-7,14; UC-34 AC-1,4,7. Authority: Inventory Todoist endpoint N11 and specs/use-cases/inventory/.

```mermaid
sequenceDiagram
    actor Staff
    participant Web as Session middleware / Inventory route
    participant Identity as Identity public service
    participant Service as Inventory service
    participant Repo as Inventory repository
    participant DB as PostgreSQL
    Staff->>Web: GET /api/v1/inventory/staff/goods-receipts/{receipt_key}
    Web->>Identity: authenticate portal_session and renew valid session
    Identity-->>Web: current account and role
    Web->>Web: require EMPLOYEE (Admin/Customer denied)
    Web->>Service: get_receipt(receipt_key)
    Service->>DB: BEGIN (shared transaction)
    participant Catalog as Catalog public service
    participant CatalogRepo as Catalog repository
    Service->>Catalog: metadata / variants / categories (same session)
    Catalog->>CatalogRepo: read Catalog-owned tables only
    CatalogRepo->>DB: SELECT current metadata / stable filtered page
    Service->>Repo: read receipt, supplier and details; enrich variant metadata via Catalog; show form only if DRAFT
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

read receipt, supplier and details; enrich variant metadata via Catalog; show form only if DRAFT.
