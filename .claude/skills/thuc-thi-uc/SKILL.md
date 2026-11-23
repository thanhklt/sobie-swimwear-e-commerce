---
name: thuc-thi-uc
description: Thực thi từng use-case (UC-XX) của Sobie swimwear e-commerce theo quy trình plan → dev duyệt → Codex thực thi → Claude kiểm chứng theo UC → test AC pass → báo dev quyết định commit. Dùng khi dev yêu cầu "thực thi UC", "triển khai UC-XX", "làm UC tiếp theo" hoặc chạy lần lượt các UC của một module (identity, catalog, shopping, ordering, payment, promotion, inventory, shipping, reporting).
---

# Thực thi use-case qua Codex

Chép từ skill `thuc-thi-uc` của xBike MRP (chốt 15/11/2026) và chỉnh cho Sobie ngày 23/11/2026. Làm **từng UC một**, theo thứ tự mã UC trong module, không gộp nhiều UC vào một plan.

Luôn tuân `AGENTS.md` (đọc lại mỗi phiên), đặc biệt:

- **Không tự ý `git commit` / `git push`** — chỉ làm khi dev yêu cầu rõ trong chat.
- Source of truth là `specs/`. Quyết định lệch `specs/` → báo dev, không tự chọn.
- Mọi giả định phải gắn tag `[GD]` và đưa vào danh sách **câu hỏi mở**.
- Không dùng skill superpowers và gitnexus.
- Kiến trúc 3 tầng `router` → `service` → `repository` → DB; module chỉ gọi service công khai của module khác, không đụng repository/bảng của module khác.
- Tiền là số nguyên VND hoặc `Decimal` (`ROUND_HALF_UP`), không `float`. Thời gian lưu UTC (`timestamptz`), chỉ đổi sang `Asia/Ho_Chi_Minh` khi hiển thị/báo cáo.
- Trừ tồn kho, áp mã giảm giá, tạo đơn phải chạy chung một transaction.
- Không hardcode secret; nạp qua `.env` / `pydantic-settings` (`app/config/settings.py`).
- Không xóa/seed lại DB, không đổi dependency/`poetry.lock` khi chưa được phép.

## Vòng lặp cho mỗi UC

### 1. Đọc và khảo sát

- Spec: `specs/use-cases/<module>/UC-XX-<slug>.md` (Main Flow, Alternative Flows, Exceptions E#, Acceptance Criteria AC-n, Notes: "Quyết định đã chốt" và "Câu hỏi mở [GD]").
- `specs/use-cases/README.md` (module, tác nhân, quy ước test).
- BR liên quan trong `specs/business-requirements/BR-GIAIDOAN1.md`; `specs/entity-model/data_model_v2.{md,dbml}`, `specs/entity-model/entity_diagram_v2.md`; `specs/diagrams/`; `infra/postgres/init.sql`, `infra/postgres/seed.sql`.
- Code hiện có: `app/modules/<module>/{router,service,repository,models,schemas}.py` (identity có thêm `session.py`), `app/main.py`, `app/config/`, `app/database/{engine,transaction}.py`, `app/security/`, `app/error/`, `app/shared/{money.py,web/}`, template Jinja/HTMX (`app/shared/web/templates/base.html`, template của module), test trong `tests/<module>/`.
- Plan của UC trước trong `docs/plans/` `[GD]` để giữ quyết định đã chốt.
- **Câu hỏi mở `[GD]` của chính UC**: UC còn `[GD]` chưa chốt chạm tới phần sắp làm → đưa vào mục D của plan, không tự chọn.
- Chạy baseline và ghi số liệu (xem mục Kiểm chứng).

### 2. Lập plan — `docs/plans/UC-XX.md` `[GD]`

Gồm:

- Goal; Context read.
- **Bảng hiện trạng so với UC**: mỗi bước Main Flow / Alternative Flow / Exception → hiện trạng code → việc cần làm.
- **Quyết định cần dev xác nhận** (D1, D2, …) kèm đề xuất. Mọi điểm spec / code / data model / `init.sql` lệch nhau, `[GD]` còn mở trong spec, hoặc chỗ spec chưa nói rõ phải nằm ở đây, gắn `[GD]`, không tự chọn.
- Quy ước comment UC (mục bên dưới), liệt kê **đích danh** các hàm router/service sẽ được comment.
- Bảng file → thay đổi cho: router, service, repository, models, schemas, template Jinja/HTMX.
- **Bảng test ↔ AC**: mỗi AC có ít nhất một test, ghi rõ assert gì. Chỉ sinh test ứng với AC; test chỉ để kiểm code (không ứng AC) đặt trong `.artifact/`.
- **Sơ đồ sequence**: mỗi endpoint thêm/đổi phải có một sơ đồ sequence trong `docs/sequence/` (AGENTS.md §5); ghi rõ tên file sẽ tạo/sửa `[GD]`.
- Ràng buộc cho Codex; lệnh kiểm chứng; điều kiện đạt; message commit đề xuất; ngoài phạm vi; mục "Kết quả: _Chưa thực thi._".
- **Câu hỏi mở**: tổng hợp mọi `[GD]` trong plan.

Báo dev tóm tắt plan + các D cần chốt, rồi **dừng chờ duyệt**. Không chạy Codex khi chưa có câu duyệt rõ ràng của dev trong chat. Khi duyệt, ghi vào đầu plan: "dev đã duyệt <ngày> (…)".

### 3. Gọi Codex

Viết prompt vào scratchpad, chạy nền (codex-cli 0.170: không có `--full-auto`; dùng `-s workspace-write`):

```bash
codex exec -s workspace-write -C "D:/Workspace/soobin-swimwear-e-commerce" -o "<scratchpad>/codex-uc-XX-last.md" - < "<scratchpad>/codex-uc-XX-prompt.md" > "<scratchpad>/codex-uc-XX.log" 2>&1
```

Prompt cho Codex phải nêu:

- Thực thi plan đã duyệt `docs/plans/UC-XX.md`, spec `specs/use-cases/<module>/UC-XX-<slug>.md`; đọc `AGENTS.md` trước.
- Các D đã duyệt thế nào; D nào không làm.
- Quy ước comment UC và comment test (nguyên văn mục bên dưới), danh sách hàm được comment.
- Không commit, không push, không migration, không động DB/Docker/`infra/`/seed, không đổi dependency/`poetry.lock`, chỉ sửa file trong plan (nếu buộc phải sửa file khác thì báo lý do).
- Giữ kiến trúc 3 tầng và ranh giới module; tiền dùng int VND/`Decimal`; thời gian UTC.
- Không sửa test fail sẵn ngoài phạm vi UC (liệt kê theo baseline).
- Chạy test bằng `poetry run pytest ...` (lệnh ở mục Kiểm chứng).
- Chạy đủ lệnh kiểm chứng, báo file đã sửa, kết quả thực tế từng lệnh, điểm lệch plan. Không sửa mục "Kết quả" của plan.

Codex chạy nền: không theo dõi, không poll log, không can thiệp giữa chừng; trong lúc chờ có thể làm việc khác không đụng file của UC. Khi có thông báo Codex chạy xong: đọc `codex-uc-XX-last.md` và log. Nếu exit lỗi do cờ CLI, xem `codex exec --help` và chạy lại.

### 4. Kiểm chứng (Claude làm, không tin báo cáo của Codex)

- `git diff` + `git status`: chỉ đúng file trong plan; không có thay đổi ngoài phạm vi, không đổi `poetry.lock`/`pyproject.toml`.
- Đối chiếu từng bước Main Flow, Alternative Flow, Exception của spec với code thật (status code/redirect, thông báo lỗi, transaction, quyền theo vai trò).
- Kiểm tra kiến trúc: router không gọi repository/DB; không truy cập repository/bảng module khác; tiền không dùng `float`; thời gian UTC; không hardcode secret.
- Mỗi hàm router/service trong danh sách có comment UC đúng bước/luồng; gỡ comment ở hàm phụ trợ không thuộc luồng.
- Mỗi test đặt tên `test_ucXX_acN_<slug>` và có comment `UC-XX AC-n`; đủ mọi AC trong bảng test ↔ AC; assert đúng ý AC (không assert lỏng, không test rỗng, không làm yếu test cũ).
- Mỗi endpoint mới/đổi có sơ đồ sequence trong `docs/sequence/`.
- Tự chạy lại các lệnh kiểm chứng và đọc kết quả.
- Lệch hoặc thiếu: sửa nhỏ trực tiếp, hoặc gửi Codex một prompt sửa cụ thể rồi kiểm chứng lại. Lệch nghiệp vụ chưa rõ → hỏi dev.

### 5. Báo kết quả và chờ dev quyết định commit

Khi **toàn bộ test ứng với AC pass** và không có lỗi mới so với baseline:

- Điền mục "Kết quả" trong plan (file đã sửa, số pass/fail từng lệnh, bảng AC → test → kết quả, giới hạn còn lại, câu hỏi mở `[GD]` còn lại).
- Báo dev: tóm tắt thay đổi, kết quả test, danh sách file của UC, message commit đề xuất `feat(UC-XX): <mô tả ngắn tiếng Việt>`.
- **Không commit / push.** Chỉ khi dev yêu cầu rõ trong chat:
  - `git add` đúng các file của UC (code, test, template, docs, plan) — không `git add -A` mù.
  - Commit message kết thúc bằng dòng `Co-Authored-By` theo chỉ dẫn attribution hiện hành.
  - Push chỉ khi dev yêu cầu push; không force push.
- Sau đó chuyển sang lập plan UC kế tiếp (quay lại bước 1). Không tự chạy Codex cho UC kế tiếp khi chưa được duyệt.

Nếu test AC không pass được: báo dev test nào fail, nguyên nhân, đề xuất.

## Quy ước comment UC (bắt buộc)

- Hàm router/service: comment ngay trên định nghĩa hàm
  `# UC-XX <Tên UC> — <bước/luồng: Main 2–6; 1a, 4a; E1, E3> (specs/use-cases/<module>/UC-XX-<slug>.md)`
- Test: comment ngay trên hàm test `# UC-XX AC-n: <tên AC>`.
- Tên hàm test theo `specs/use-cases/README.md`: `test_ucXX_acN_<slug>`.
- File test mới: `tests/<module>/test_ucXX_<slug>.py`.

## Kiểm chứng và điều kiện đạt

Mức test: pytest trong `tests/<module>/`; nhóm phụ thuộc `test` có `pytest` và `aiosqlite` — dùng SQLite in-memory hay repository giả do plan chốt `[GD]`. Không bắt buộc Playwright hay PostgreSQL thật trừ khi dev yêu cầu.

```bash
poetry run pytest -q -p no:cacheprovider tests/<module>/test_ucXX_<slug>.py
poetry run pytest -q -p no:cacheprovider tests
```

Đạt khi: test của UC pass 100%; toàn bộ `tests/` không có lỗi mới so với baseline.

Lint: dự án chưa khai báo ruff/flake8 trong `pyproject.toml` nên chưa có bước lint `[GD]`.

Baseline: `tests/` hiện chỉ có `.gitkeep` theo module (chưa có test, 23/11/2026). Cập nhật baseline sau mỗi UC hoàn tất.

Bài học từ xBike: Codex có xu hướng gắn comment UC tràn lan vào hàm phụ trợ — trong plan hãy liệt kê đích danh các hàm được comment, và khi kiểm chứng gỡ comment ở hàm không thuộc luồng. Mỗi UC viết prompt Codex mới, không sửa từ prompt UC trước.

## Môi trường

- Python ≥ 3.11, quản lý bằng Poetry (virtualenv nằm trong cache của Poetry, không có `.venv` trong repo). Chạy lệnh qua `poetry run`. Không `poetry add` / `poetry lock` khi chưa được phép.
- Biến môi trường: chép `.env.example` thành `.env` (không commit `.env`).
- Nhánh hiện tại: `main`. Không tự tạo nhánh, commit hay push khi dev chưa yêu cầu.

## Câu hỏi mở [GD] của chính skill

- `[GD]` Giữ Codex làm bên thực thi code cho Sobie (codex-cli 0.170 đã có trên máy), hay Claude tự viết code?
- `[GD]` Plan mỗi UC đặt tại `docs/plans/UC-XX.md`?
- `[GD]` Đặt tên file sequence: `docs/sequence/<module>/<endpoint>.md` hay một file mỗi UC?
- `[GD]` Test dùng SQLite in-memory (`aiosqlite`) hay repository giả?
- `[GD]` Có thêm bước lint (ruff) không? Hiện chưa có trong dependency.
- `[GD]` Template Jinja của module đặt ở `app/modules/<module>/templates/`?
