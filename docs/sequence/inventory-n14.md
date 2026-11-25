# N14 — POST /api/v1/inventory/staff/goods-receipts/{receipt_key}/confirm

Coverage: UC-34 AC-1–17. Authority: Inventory Todoist endpoint N14 and specs/use-cases/inventory/.

```mermaid
sequenceDiagram
    actor Staff
    participant Web as Session middleware / Inventory route
    participant Identity as Identity public service
    participant Service as Inventory service
    participant Repo as Inventory repository
    participant DB as PostgreSQL
    Staff->>Web: POST /api/v1/inventory/staff/goods-receipts/{receipt_key}/confirm
    Web->>Identity: authenticate portal_session and renew valid session
    Identity-->>Web: current account and role
    Web->>Web: require EMPLOYEE (Admin/Customer denied)
    Web->>Web: require same Origin; parse and validate form
    Web->>Service: confirm_receipt(receipt_key)
    Service->>DB: BEGIN (shared transaction)
    Service->>Repo: get_receipt(lock=True); recheck DRAFT; receipt_lines
    Repo->>DB: SELECT receipt FOR UPDATE; reread details
    participant Catalog as Catalog public service
    participant CatalogRepo as Catalog repository
    Service->>Catalog: get_inventory_variants(same session, lock=True)
    Catalog->>CatalogRepo: lock all parents ASC, then all variants ASC
    CatalogRepo->>DB: ordered FOR UPDATE; reread metadata after waits
    Service->>Repo: get_stocks(lock=True), ordered variant key ASC
    Repo->>DB: SELECT stock FOR UPDATE; read current quantity and cost
    Service->>Service: weighted average using Decimal, ROUND_HALF_UP
    Service->>Repo: update all stock rows and receipt CONFIRMED
    Repo->>DB: UPDATE stock and receipt
    Service->>DB: COMMIT all changes
    participant Redis
    Service->>Catalog: bump_catalog_version() AFTER commit
    Catalog->>Redis: INCR catalog:version with bounded timeout
    alt Cache failure after commit
        Service->>Service: log receipt ID; no rollback and no retry
    end
    Service-->>Web: committed success
    Web-->>Staff: 303 receipt detail (even if cache failed)
    Note over Service,DB: Database write/commit failure rolls back entire transaction; no success or cache increment.
    Note over Web,Staff: Cache-Control no-store; Vary HX-Request; private DOM history disabled.
```

Input errors: 400; missing entity: 404; business conflict: 409; persistence failure: 503. Destructive/status actions require `confirm=yes`. Unauthenticated requests use the shared portal-login/error flow; authenticated Admin and Customer requests are denied (403).

receipt lock then product locks then variant locks then stock locks; exact weighted cost; one CONFIRMED commit.
