# Handoff Config

## Verification Commands
test:
typecheck:
lint:
build:

> Dự án chưa chốt stack: `pyproject.toml` chưa khai báo thư viện (chưa có pytest, ruff, mypy).
> Khi thêm, điền `pytest` / `ruff check` / `mypy app` vào các trường trên.
> Thay đổi schema / dữ liệu mẫu được kiểm bằng cách chạy `infra/postgres/init.sql` + `seed.sql`
> trên container `postgres:16-alpine` tạm (xem Verification plan của từng plan).

## Conventions
response_language: vi
handoff_dir:       .handoff
commit_style:      conventional
convention_docs:   AGENTS.md

## Project Documentation Index

### Agent guidance
- [AGENTS.md](AGENTS.md) — quy tắc agent (3 tầng, envelope, tiền, giờ, [GD])
- [CLAUDE.md](CLAUDE.md) — trỏ tới AGENTS.md

### Project docs
- [README.md](README.md) — tổng quan, module, trạng thái
- [specs/business-requirements/BR-GIAIDOAN1.md](specs/business-requirements/BR-GIAIDOAN1.md) — business requirements giai đoạn 1
- [specs/entity-model/data_model_v2.dbml](specs/entity-model/data_model_v2.dbml) — data model (nguồn chính)
- [specs/entity-model/data_model_v2.md](specs/entity-model/data_model_v2.md) — bản vẽ Mermaid của DBML
- [specs/entity-model/entity_diagram_v2.md](specs/entity-model/entity_diagram_v2.md) — entity model, quy tắc nghiệp vụ
- [specs/use-cases/README.md](specs/use-cases/README.md) — danh sách UC, quyết định, giả định
- [infra/postgres/init.sql](infra/postgres/init.sql) — schema PostgreSQL
- [infra/postgres/seed.sql](infra/postgres/seed.sql) — dữ liệu mẫu dev / demo
- [infra/docker-compose.yml](infra/docker-compose.yml) — PostgreSQL cho dev

### Detected toolchain
- package manager: poetry-core (chưa có dependency)
- monorepo: không
- frameworks: chưa chốt (dự kiến FastAPI + Jinja + HTMX, PostgreSQL 16, Redis)
