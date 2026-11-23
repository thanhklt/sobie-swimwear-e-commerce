# Agent Rules

## 1. Nguyên tắc cốt lõi (Core Rules)
- **Không tự ý git commit hoặc git push**: Tuyệt đối không tự ý push hay commit code trừ khi có yêu cầu rõ ràng từ developer.
- **Source of Truth**: Luôn đọc từ `source_of_true` mỗi khi bắt đầu phiên mới: là specs/
- **Xử lý lệch thông tin**: Khi quyết định hiện tại lệch với thông tin từ `source_of_true`, hãy báo cho developer biết để quyết định.
- **Xử lý vấn đề mơ hồ**: Khi gặp vấn đề mơ hồ, không tự ý giả định mà hãy báo cho developer biết để chờ developer quyết định.
- **Quy định gắn tag giả định [GD]**: Mọi thông tin, luồng xử lý hoặc quyết định mà agent giả định bắt buộc phải được gắn tag `[GD]` và tổng hợp đưa vào danh sách **câu hỏi mở** để chờ developer quyết định.
- **Không xài skill superpower và gitnexus**

## 2. Kiến trúc & Phân tầng (Architecture & Boundaries)
- **Tuân thủ nghiêm ngặt 3 tầng (3-Layer Pattern)**: Luôn đi theo luồng `Route` → `Service` → `Repository` → `Database`. Tuyệt đối không gọi tắt (Route không gọi trực tiếp Repository hoặc DB).
- **Ranh giới Modular Monolith**: Các module nghiệp vụ (catalog, cart, orders,...) giao tiếp với nhau qua Service/Interface công khai; không truy cập trực tiếp Repository hoặc database table của module khác.

## 3. Quy ước Dữ liệu
- **Tiền tệ & Số học tài chính**: Tiền tệ luôn biểu diễn bằng số nguyên VND hoặc kiểu `Decimal` trong Python, làm tròn theo `ROUND_HALF_UP`. Tuyệt đối không dùng `float` để tránh sai số tính toán đơn hàng / khuyến mãi.
- **Thời gian & Múi giờ**: Lưu trữ và xử lý thời gian trong DB luôn ở dạng UTC (`timestamptz`). Chỉ định dạng sang múi giờ `Asia/Ho_Chi_Minh` khi xuất báo cáo hoặc hiển thị lên giao diện.

## 4. Kiểm thử & Toàn vẹn dữ liệu (Testing & Data Integrity)
- Chỉ sinh test ứng với AC trong UC. Đối với những test để valid code thì tạo trong .artifact/
- **Toàn vẹn Transaction**: Các thao tác nhạy cảm như trừ tồn kho, kiểm tra/áp mã giảm giá và tạo đơn hàng phải luôn chạy trong cùng một Database Transaction để chống race condition.

## 5. Bảo mật & Quản lý Source Code
- **Bảo vệ Secret & Cấu hình**: Không bao giờ hardcode credentials, tokens, secrets vào mã nguồn. Luôn nạp qua biến môi trường (`.env`, `pydantic-settings`).
- **Phạm vi tác động tối thiểu**: Chỉ chỉnh sửa đúng phạm vi task được yêu cầu; bảo toàn comments, docstrings và cấu trúc code có sẵn không liên quan.
- Mỗi 1 endpoint phải gắn liền với 1 sơ đồ sequence. Vị trí của lược đồ sequence tại /docs/sequence/..... .md