# Inventory implementation

The staff HTML endpoints are registered at `/api/v1/inventory/staff`; all 15 Todoist Inventory tasks N01–N15 have matching [sequence diagrams](sequence/inventory-n01.md). Inventory accepts only the Employee role and the portal cookie, including full-page and HTMX requests. Every write requires the same-origin `Origin` header. Forms use `name`, `phone_number`, `email`, `address` for suppliers and repeated `variant_key`, `quantity`, `unit_price` fields plus `supplier_key` for receipts. Status/delete actions submit `confirm=yes`.

The user approved Todoist endpoint tasks plus `specs/` as authority because `api_contract_v1.md` is absent, and approved the minimum Catalog integration. UC-35 is `inventory.service.restore_stock` inside the Ordering caller's transaction; Ordering owns order locking, status/history, exactly-once decisions, commit recovery and postcommit cache handling. There is no Inventory restock HTTP endpoint and no Ordering/Shipping state-machine implementation in this change.

## Deployment

Install the updated Poetry lockfile and configure `DATABASE_URL` and `REDIS_URL` from the environment. `tzdata` supplies the IANA Asia/Ho_Chi_Minh display timezone on Windows. Stored timestamps remain timezone-aware UTC. Existing deployments must apply `infra/postgres/inventory-support.sql` once before using the new endpoints; fresh Docker Compose databases load it automatically after `init.sql` and `seed.sql`.

The migration adds two bounded natural-ID sequences and a unique normalized supplier-name index. Its watermark initialization preserves already allocated sequence values and advances past seeded IDs. Existing case/trim-duplicate supplier names cause index creation to fail; resolve such legacy duplicates before applying the migration. Sequence gaps on rollback are intentional; IDs are never reused after deletion. The four-digit code range has a hard limit of 9999.

Catalog invalidation increments Redis `catalog:version` after receipt confirmation commits, with bounded timeouts. Catalog public-data consumers must include that shared version in keys and use the specified 300-second fallback TTL. Public storefront cache readers were already unimplemented and are outside this Inventory change. UC-34 logs a postcommit cache failure with receipt code and still reports confirmation success, without retry. Portal lists always query PostgreSQL.

## Ownership and validation status

Six developer sessions used `antigravity`, model `gemini-4-hydrogen-high`, effort `high`, with one primary Inventory Python file each. Gemini completed models and schemas, and partially implemented the repository. The repository/service/router/Catalog assignments stopped after quota exhaustion; Orca confirmed their terminal processes killed before Sol took ownership. Sol completed the remaining code and ancillary integration following the user's direct instruction to continue due to quota. No replacement developer model was launched.

The user explicitly requested skipping tests for now. The input-validation AC test source already created in `tests/inventory/` is retained but was not run by the manager; no database, race, browser, Redis or endpoint test pass is claimed. Gemini reported isolated inline metadata/schema checks before the skip instruction; these do not verify end-to-end behavior. Python compilation, parsing both Inventory Jinja templates, and `git diff --check` passed. Static review covers route mapping, role/Origin enforcement, integer money, shared transaction boundaries, ordered locks, errors and module boundaries. Runtime verification remains outstanding for final review.

## AC implementation scope

| Use case | Implemented behavior | Runtime verification |
|---|---|---|
| UC-32 AC-1–12 | Supplier CRUD, inactive handling, reference protection, normalized names, search/paging | Skipped |
| UC-33 AC-1–14 | Draft create/edit/cancel, integer line validation, active supplier checks, receipt row locks, rollback and historical filters | Skipped |
| UC-34 AC-1–17 | Ordered receipt/product/variant/stock locks, exact weighted cost, one confirmation, postcommit invalidation | Skipped |
| UC-35 stock portion | Caller-owned restore, complete existing stock rows, ordered locks, cost preservation, atomic transaction participation | Skipped; order state/history/cache recovery remains Ordering's responsibility |
| UC-39 AC-1–20 | Current stock, 20-row stable paging, search/category filter, inactive and zero rows, low threshold 5, no costs or manual edits, no-store | Skipped; upstream ordering/shipping workflows outside this change |

No unresolved business assumptions were introduced. Absent Identity login page implementation means the shared session error handler can render a 401 page instead of resolving the future `portal_login` route; Identity login creation remains outside Inventory scope.
