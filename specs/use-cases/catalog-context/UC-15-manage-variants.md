# UC-15: Quản lý biến thể màu × size

## Metadata
- **ID:** UC-15
- **Bounded Context:** catalog-context
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở mục Biến thể của một sản phẩm.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Sản phẩm đã tồn tại (UC-14).
- Giá trị màu và size đã có trong thuộc tính (UC-17).

## Main Flow
1. Hệ thống hiển thị danh sách biến thể của sản phẩm: màu, size, tồn kho.
2. Nhân viên chọn các màu và các size cần tạo.
3. Hệ thống tạo các biến thể theo tổ hợp màu × size chưa tồn tại, tồn kho ban đầu = 0 `[GD]`.
4. Hệ thống hiển thị danh sách biến thể đã cập nhật.

## Alternative Flows
- **2a. Xóa biến thể:** chỉ xóa được biến thể chưa phát sinh đơn hàng hoặc phiếu nhập và có tồn kho = 0 `[GD]`.
- **3a. Một số tổ hợp đã tồn tại:** hệ thống bỏ qua các tổ hợp đó và chỉ tạo tổ hợp mới.

## Exceptions
- **E1. Không chọn màu hoặc không chọn size:** hệ thống không tạo và nhắc chọn đủ.
- **E2. Xóa biến thể đã phát sinh giao dịch hoặc còn tồn kho:** hệ thống từ chối và báo lý do.

## Postconditions
- Sản phẩm có danh sách biến thể màu × size mới; mỗi tổ hợp màu × size là duy nhất trong sản phẩm.

## Acceptance Criteria

### AC-1: Tạo biến thể theo tổ hợp
Given: sản phẩm A chưa có biến thể
When: Nhân viên chọn màu Đỏ, Xanh và size S, M rồi lưu
Then: hệ thống tạo 4 biến thể: Đỏ×S, Đỏ×M, Xanh×S, Xanh×M
And: tồn kho mỗi biến thể = 0

### AC-2: Không tạo trùng
Given: sản phẩm A đã có biến thể Đỏ×S
When: Nhân viên chọn màu Đỏ và size S, L rồi lưu
Then: hệ thống chỉ tạo thêm Đỏ×L

### AC-3: Thiếu màu hoặc size
Given: Nhân viên đang tạo biến thể
When: Nhân viên chỉ chọn màu, không chọn size và lưu
Then: hệ thống không tạo biến thể và nhắc chọn size

### AC-4: Tồn kho không sửa tay
Given: Nhân viên xem danh sách biến thể
When: Nhân viên muốn thay đổi tồn kho của một biến thể
Then: hệ thống không cho sửa trực tiếp tồn kho trên màn hình này

### AC-5: Chặn xóa biến thể còn tồn kho hoặc có giao dịch
Given: biến thể Đỏ×M có tồn kho = 5
When: Nhân viên xóa biến thể Đỏ×M
Then: hệ thống từ chối và báo "Biến thể còn tồn kho hoặc đã phát sinh giao dịch"

### AC-6: Xóa biến thể hợp lệ
Given: biến thể Xanh×L có tồn kho = 0 và chưa có trong đơn hàng hoặc phiếu nhập nào
When: Nhân viên xóa Xanh×L
Then: biến thể bị xóa khỏi sản phẩm

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-14 Quản lý sản phẩm, UC-17 Quản lý danh mục, bộ sưu tập và thuộc tính
- **Downstream UC:** UC-12 Xem chi tiết sản phẩm, UC-16 Quản lý giá bán theo size, UC-18 Quản lý giỏ hàng, UC-33 Lập phiếu nhập, UC-34 Xác nhận phiếu nhập
- **External Systems:** không có

## Notes
- Tồn kho của biến thể chỉ thay đổi qua inventory-context (xác nhận phiếu nhập, đặt/hủy đơn, giao không thành công). Tồn kho không bao giờ âm (BR-005).
- Giá vốn tính riêng cho từng biến thể (BR-007).

### Giả định [GD]
- Biến thể mới tạo có tồn kho = 0; tồn kho không sửa tay.
- Chỉ xóa được biến thể có tồn kho = 0 và chưa có trong đơn hàng hoặc phiếu nhập.

## History
- v1 (2026-11-15): initial
