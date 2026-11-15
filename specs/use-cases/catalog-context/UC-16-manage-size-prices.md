# UC-16: Quản lý giá bán theo size

## Metadata
- **ID:** UC-16
- **Bounded Context:** catalog-context
- **Liên quan tới BR:** BR-002
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở mục Giá bán của một sản phẩm.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).
- Sản phẩm đã có biến thể (UC-15).

## Main Flow
1. Hệ thống hiển thị các size của sản phẩm và giá bán hiện tại của từng size.
2. Nhân viên nhập hoặc sửa giá bán cho từng size.
3. Hệ thống kiểm tra giá là số nguyên VND lớn hơn 0 và lưu.
4. Hệ thống ghi cùng giá đó vào `variant_sell_price` của mọi biến thể cùng sản phẩm và cùng size (mọi màu của size đó), trong cùng một transaction; giá mới hiển thị ngay trên storefront.

## Alternative Flows
- **2a. Size chưa có giá:** hệ thống đánh dấu size đó "Chưa có giá"; sản phẩm chưa thể chuyển Đang bán (UC-14, E3).

## Exceptions
- **E1. Giá không hợp lệ (để trống, ≤ 0, không phải số nguyên):** hệ thống không lưu và báo lỗi tại size tương ứng.

## Postconditions
- Mỗi size có đúng một giá bán hiện hành; mọi biến thể cùng sản phẩm và cùng size có cùng `variant_sell_price`.

## Acceptance Criteria

### AC-1: Đặt giá theo size
Given: sản phẩm A có size S, M
When: Nhân viên nhập giá S = 300.000đ, M = 320.000đ và lưu
Then: trang chi tiết sản phẩm A hiển thị 300.000đ khi chọn S và 320.000đ khi chọn M

### AC-2: Mọi màu cùng size dùng chung giá
Given: sản phẩm A có biến thể Đỏ×M và Xanh×M, giá size M = 320.000đ
When: người dùng chọn Đỏ×M rồi Xanh×M trên trang chi tiết
Then: cả hai đều hiển thị 320.000đ

### AC-3: Đặt giá ghi cho mọi biến thể cùng size
Given: sản phẩm A có biến thể Đỏ×M, Xanh×M và Đỏ×L
When: Nhân viên đặt giá size M = 320.000đ và lưu
Then: biến thể Đỏ×M và Xanh×M đều có giá bán 320.000đ
And: giá của biến thể Đỏ×L không đổi

### AC-4: Giá không hợp lệ
Given: Nhân viên đang sửa giá
When: Nhân viên nhập giá size S = 0 và lưu
Then: hệ thống không lưu và báo "Giá bán phải lớn hơn 0"

### AC-5: Đổi giá không ảnh hưởng đơn đã tạo
Given: đơn hàng X đã đặt sản phẩm A size M với giá 320.000đ
When: Nhân viên đổi giá size M thành 350.000đ
Then: đơn hàng X vẫn giữ giá 320.000đ
And: đơn mới đặt sau đó dùng giá 350.000đ

## Dependencies
- **Upstream UC:** UC-02 Đăng nhập, UC-15 Quản lý biến thể màu × size
- **Downstream UC:** UC-10, UC-12, UC-14 (điều kiện chuyển Đang bán), UC-18 Quản lý giỏ hàng, UC-19, UC-20, UC-28 Quản lý khuyến mãi theo sản phẩm
- **External Systems:** không có

## Notes
- Tiền là số nguyên VND (AGENTS.md).

### Quyết định đã chốt
- Giá bán theo size; mọi màu cùng size dùng chung một giá (đã chốt 15/11/2026).
- Giữ `variant_sell_price` ở biến thể theo ERD: khi Nhân viên đặt giá cho một size, hệ thống ghi cùng giá cho mọi biến thể cùng sản phẩm và cùng size (đã chốt 15/11/2026, theo data model v1 — ưu tiên ERD). Không còn lệch ERD.

### Giả định [GD]
- Đổi giá không ảnh hưởng đơn hàng đã tạo.
- Không lưu lịch sử giá.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt giá theo size, mọi màu cùng size chung giá; ghi chú lệch ERD (`variant_sell_price`)
- v3 (2026-11-15): theo data model v1 — giữ `variant_sell_price`, đặt giá theo size ghi cho mọi biến thể cùng size; thêm AC-3
