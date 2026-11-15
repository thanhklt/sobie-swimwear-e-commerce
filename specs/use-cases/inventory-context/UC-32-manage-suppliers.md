# UC-32: Quản lý nhà cung cấp

## Metadata
- **ID:** UC-32
- **Bounded Context:** inventory-context
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý nhà cung cấp để xem, thêm, sửa hoặc ngừng hợp tác với một nhà cung cấp.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên xem danh sách nhà cung cấp (có phân trang, tìm theo tên `[GD]`).
2. Nhân viên chọn "Thêm nhà cung cấp".
3. Nhân viên nhập tên, số điện thoại, email, địa chỉ.
4. Hệ thống kiểm tra dữ liệu hợp lệ và tên chưa tồn tại `[GD]`.
5. Hệ thống lưu nhà cung cấp ở trạng thái "Đang hợp tác".

## Alternative Flows
- **2a. Sửa nhà cung cấp:** Nhân viên sửa thông tin; hệ thống kiểm tra như bước 4 rồi lưu. Phiếu nhập đã có vẫn tham chiếu đúng nhà cung cấp.
- **2b. Ngừng hợp tác:** nhà cung cấp chuyển sang "Ngừng hợp tác", không chọn được khi lập phiếu nhập mới; dữ liệu cũ giữ nguyên.
- **2c. Xóa nhà cung cấp chưa có phiếu nhập:** hệ thống xóa hẳn `[GD]`.

## Exceptions
- **E1. Thiếu hoặc sai dữ liệu:** thiếu tên, số điện thoại hoặc email sai định dạng → hệ thống báo lỗi theo từng trường, không lưu.
- **E2. Trùng tên:** tên nhà cung cấp đã tồn tại → hệ thống báo lỗi, không lưu `[GD]`.
- **E3. Xóa nhà cung cấp đã có phiếu nhập:** hệ thống từ chối xóa, gợi ý chuyển sang "Ngừng hợp tác" `[GD]`.

## Postconditions
- Thông tin nhà cung cấp được lưu; chỉ nhà cung cấp "Đang hợp tác" được chọn khi lập phiếu nhập (UC-33).

## Acceptance Criteria

### AC-1: Thêm nhà cung cấp hợp lệ
Given: Nhân viên đã đăng nhập, tên "Công ty Biển Xanh" chưa tồn tại
When: Nhân viên thêm nhà cung cấp với tên, số điện thoại, email hợp lệ
Then: nhà cung cấp được lưu với trạng thái "Đang hợp tác"
And: xuất hiện trong danh sách nhà cung cấp

### AC-2: Thiếu dữ liệu bắt buộc
Given: Nhân viên ở màn hình thêm nhà cung cấp
When: Nhân viên lưu khi chưa nhập tên hoặc email sai định dạng
Then: hệ thống báo lỗi tại trường tương ứng, không lưu

### AC-3: Trùng tên
Given: nhà cung cấp "Công ty Biển Xanh" đã tồn tại
When: Nhân viên thêm nhà cung cấp cùng tên
Then: hệ thống báo lỗi trùng tên, không lưu

### AC-4: Ngừng hợp tác
Given: nhà cung cấp X đang hợp tác và đã có phiếu nhập
When: Nhân viên chuyển X sang "Ngừng hợp tác"
Then: X không xuất hiện trong danh sách chọn khi lập phiếu nhập mới
And: các phiếu nhập cũ của X vẫn hiển thị đúng tên X

### AC-5: Không xóa được nhà cung cấp đã có phiếu nhập
Given: nhà cung cấp X đã có ít nhất một phiếu nhập
When: Nhân viên xóa X
Then: hệ thống từ chối xóa và gợi ý chuyển sang "Ngừng hợp tác"

## Dependencies
- **Upstream UC:** UC-02
- **Downstream UC:** UC-33, UC-37
- **External Systems:** không có

## Notes
- Áp dụng constraint cache danh sách (BR-TUAN1, Constraints chung) cho danh sách nhà cung cấp.
- ERD hiện chỉ có cột tên nhà cung cấp; cần bổ sung cột số điện thoại, email, địa chỉ và trạng thái (`supplier_status`).

**Quyết định đã chốt**
- Thông tin nhà cung cấp gồm: tên, số điện thoại, email, địa chỉ (đã chốt 15/11/2026, bổ sung so với ERD).
- Nhà cung cấp có trạng thái "Đang hợp tác" / "Ngừng hợp tác"; chỉ nhà cung cấp "Đang hợp tác" được chọn khi lập phiếu nhập (đã chốt 15/11/2026; ERD sẽ thêm cột `supplier_status`).

**Giả định [GD]**
- Tên nhà cung cấp là bắt buộc và không trùng.
- Danh sách có phân trang và tìm theo tên.
- Nhà cung cấp đã có phiếu nhập không xóa được, chỉ ngừng hợp tác; chưa có phiếu nhập thì xóa hẳn được.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt thông tin nhà cung cấp gồm tên, SĐT, email, địa chỉ; ghi chú ERD cần bổ sung cột
- v3 (2026-11-15): chốt trạng thái nhà cung cấp Đang hợp tác / Ngừng hợp tác (ERD thêm cột `supplier_status`)
