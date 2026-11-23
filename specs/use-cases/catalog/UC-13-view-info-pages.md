# UC-13: Xem trang giới thiệu, chính sách, FAQ

## Metadata
- **ID:** UC-13
- **Module:** catalog
- **Liên quan tới BR:** BR-002
- **Status:** ready

## Actor
Khách vãng lai, Khách hàng

## Trigger
Người dùng bấm vào liên kết Giới thiệu, Chính sách hoặc FAQ (ở chân trang - Footer của storefront), hoặc truy cập trực tiếp đường dẫn URL tương ứng.

## Preconditions
- Website đang hoạt động.

## Main Flow
1. Người dùng bấm vào liên kết của một trang thông tin ở chân trang (Footer) trên storefront: "Giới thiệu" (`/about`), "Chính sách" (`/policy`), hoặc "FAQ" (`/faq`).
2. Trình duyệt gửi request HTMX (kèm header `HX-Request: true`) đến endpoint tương ứng của hệ thống.
3. Hệ thống tiếp nhận và render nội dung template HTML tĩnh của trang thông tin được yêu cầu.
4. Hệ thống trả về mảnh HTML nội dung tương ứng kèm HTTP header `Cache-Control: private, no-cache` và `Vary: HX-Request` (không có header `ETag`).
5. Trình duyệt nạp mảnh nội dung vào vùng hiển thị chính (`#main-content`) và cập nhật URL trên thanh địa chỉ theo đường dẫn của trang (`hx-push-url="true"`).
6. Nội dung trang thông tin hiển thị hoàn chỉnh theo đúng loại trang được chọn:
   - **Trang Giới thiệu (`/about`):** Thông tin thương hiệu đồ bơi Soobie, sứ mệnh, hotline và thông tin liên hệ của cửa hàng.
   - **Trang Chính sách (`/policy`):** Quy định mua hàng, vận chuyển, bảo mật thông tin và hướng dẫn giải quyết đổi/trả ngoài hệ thống.
   - **Trang FAQ (`/faq`):** Danh sách các câu hỏi thường gặp và câu trả lời liên quan đến sản phẩm, chọn size, cách đặt hàng và thanh toán.

## Alternative Flows
- **1a. Truy cập trực tiếp qua đường dẫn URL (Direct URL / Full page reload):**
  - 1a1. Người dùng nhập trực tiếp URL `/about`, `/policy`, hoặc `/faq` trên thanh địa chỉ trình duyệt (hoặc mở từ bookmark, chia sẻ liên kết, tải lại trang F5).
  - 1a2. Trình duyệt gửi request HTTP thông thường (không có header `HX-Request`).
  - 1a3. Hệ thống render toàn bộ trang HTML hoàn chỉnh (bao gồm layout chung: header, thanh menu, giỏ hàng, thông tin phiên người dùng, nội dung trang thông tin tương ứng và footer).
  - 1a4. Hệ thống trả về toàn bộ trang HTML hoàn chỉnh kèm HTTP header `Cache-Control: private, no-cache` và `Vary: HX-Request`.
  - 1a5. Trình duyệt hiển thị toàn bộ trang web; tiếp tục như bước 6 của Main Flow.
- **6a. Chuyển đổi giữa các trang thông tin:**
  - 6a1. Người dùng đang ở một trang thông tin (ví dụ `/about`) và bấm liên kết tới trang thông tin khác (ví dụ `/faq` ở Footer hoặc menu phụ).
  - 6a2. Hệ thống thực hiện nạp mảnh nội dung từ bước 2 của Main Flow để thay thế nội dung trang mới mà không cần tải lại toàn bộ trang.

## Exceptions
- **E1. Đường dẫn trang thông tin không tồn tại (HTTP 404):**
  - E1.1. Người dùng truy cập một đường dẫn trang thông tin không hợp lệ hoặc không tồn tại (ví dụ: `/info/khong-ton-tai` hoặc gõ sai URL) qua request HTTP thông thường hoặc request HTMX.
  - E1.2. Hệ thống xác định trang không tồn tại và trả về mã trạng thái HTTP 404 Not Found.
  - E1.3. Hệ thống hiển thị thông báo lỗi "Không tìm thấy trang" kèm liên kết/nút quay về Trang chủ:
    - Nếu là request HTTP thông thường (Full page): render toàn bộ trang lỗi 404 hoàn chỉnh cùng layout website.
    - Nếu là request HTMX: trả về mã HTTP 404 kèm mảnh HTML thông báo lỗi 404, phía client cho phép swap nội dung vào vùng `#main-content` (qua sự kiện `htmx:beforeSwap` xử lý riêng mã trạng thái 404 và target `#main-content`), nội dung thông báo lỗi xuất hiện trong DOM và nút quay về Trang chủ hoạt động bình thường.

## Postconditions
- Nội dung trang thông tin tương ứng được hiển thị cho người dùng; dữ liệu nội dung trang và dữ liệu nghiệp vụ (catalog, giỏ hàng, đơn hàng...) không thay đổi (ngoại trừ cập nhật kỹ thuật gia hạn phiên đăng nhập `identity.session` nếu người dùng đã đăng nhập theo BR-GIAIDOAN1 Constraints chung — Xác thực).

## Acceptance Criteria

### AC-1: Xem trang Giới thiệu qua liên kết Footer (HTMX)
Given: người dùng đang ở bất kỳ trang nào của storefront  
When: người dùng bấm liên kết "Giới thiệu" ở chân trang  
Then: request gửi đi chứa header `HX-Request: true` đến đường dẫn `/about`  
And: hệ thống trả về mảnh HTML nội dung trang giới thiệu cửa hàng  
And: thanh địa chỉ trình duyệt cập nhật URL thành `/about`  
And: nội dung giới thiệu thương hiệu và sứ mệnh của Soobie được hiển thị  

### AC-2: Xem trang Chính sách qua liên kết Footer (HTMX)
Given: người dùng đang ở bất kỳ trang nào của storefront  
When: người dùng bấm liên kết "Chính sách" ở chân trang  
Then: request gửi đi chứa header `HX-Request: true` đến đường dẫn `/policy`  
And: hệ thống trả về mảnh HTML nội dung trang chính sách chung  
And: thanh địa chỉ trình duyệt cập nhật URL thành `/policy`  
And: nội dung chính sách mua hàng, giao nhận, bảo mật và hướng dẫn quy định chung được hiển thị  

### AC-3: Xem trang FAQ qua liên kết Footer (HTMX)
Given: người dùng đang ở bất kỳ trang nào của storefront  
When: người dùng bấm liên kết "FAQ" ở chân trang  
Then: request gửi đi chứa header `HX-Request: true` đến đường dẫn `/faq`  
And: hệ thống trả về mảnh HTML nội dung câu hỏi thường gặp  
And: thanh địa chỉ trình duyệt cập nhật URL thành `/faq`  
And: danh sách câu hỏi và câu trả lời thường gặp được hiển thị  

### AC-4: Truy cập trực tiếp đường dẫn URL của trang thông tin (Full page reload)
Given: người dùng nhập trực tiếp đường dẫn `/about`, `/policy`, hoặc `/faq` trên thanh địa chỉ trình duyệt  
When: người dùng gửi request không có header `HX-Request`  
Then: hệ thống trả về toàn bộ trang HTML hoàn chỉnh với mã trạng thái HTTP 200  
And: trang hiển thị đầy đủ layout chung (header, menu, footer) cùng nội dung của trang thông tin tương ứng  

### AC-5: Đường dẫn trang không tồn tại qua request thông thường (HTTP 404)
Given: người dùng truy cập một đường dẫn trang thông tin không tồn tại  
When: hệ thống nhận request thông thường (không có header `HX-Request`)  
Then: hệ thống trả về mã trạng thái HTTP 404 Not Found  
And: hiển thị toàn bộ trang giao diện thông báo "Không tìm thấy trang" kèm liên kết quay về Trang chủ  

### AC-6: Đường dẫn trang không tồn tại qua request HTMX (HTTP 404)
Given: người dùng gửi request HTMX (chứa header `HX-Request: true`) đến đường dẫn trang thông tin không tồn tại  
When: hệ thống nhận request  
Then: hệ thống trả về mã trạng thái HTTP 404 Not Found kèm mảnh HTML thông báo lỗi 404  
And: sự kiện `htmx:beforeSwap` cho phép swap response 404 vào vùng target `#main-content` (`detail.shouldSwap = true`, `detail.isError = false`)  
And: nội dung thông báo "Không tìm thấy trang" thực sự xuất hiện trong DOM tại `#main-content`  
And: nút quay về Trang chủ hiển thị và hoạt động  

### AC-7: Kiểm tra HTTP response headers cho trang thông tin
Given: request hợp lệ đến bất kỳ trang thông tin nào (`/about`, `/policy`, `/faq`)  
When: hệ thống phản hồi kết quả  
Then: response có header `Cache-Control: private, no-cache`  
And: response có header `Vary: HX-Request`  
And: response không có header `ETag`  

### AC-8: Không thay đổi dữ liệu nghiệp vụ
Given: người dùng duyệt qua các trang thông tin (`/about`, `/policy`, `/faq`)  
When: thao tác xem trang hoàn tất  
Then: không có bất kỳ dữ liệu nghiệp vụ nào (thông tin trang, sản phẩm, giỏ hàng, đơn hàng...) bị thay đổi hoặc thêm mới  
And: ngoại trừ thao tác kỹ thuật gia hạn phiên đăng nhập (`identity.session`) đối với người dùng đã đăng nhập theo quy định tại BR-GIAIDOAN1  

## Dependencies
- **Upstream UC:** không có
- **Downstream UC:** [UC-09: Xem trang chủ](UC-09-view-home-page.md) (liên kết quay lại trang chủ từ trang lỗi 404)
- **External Systems:** không có

## Notes
- Áp dụng constraint cache & SSR (BR-GIAIDOAN1, Constraints chung — Cache): Website render phía server (FastAPI + Jinja + HTMX). Không lưu dữ liệu các trang thông tin cố định trong Redis; HTML render trực tiếp từ template và trả HTTP header `Cache-Control: private, no-cache`, `Vary: HX-Request`, không dùng `ETag` (đã chốt 21/11/2026).
- Áp dụng constraint xác thực & phiên (BR-GIAIDOAN1, Constraints chung — Xác thực): Mỗi request hợp lệ từ tài khoản đã đăng nhập gia hạn `identity.session` (tính từ lần thao tác cuối).
- Out of Scope (BR-GIAIDOAN1): blog, trang cộng đồng, góp ý, CMS chỉnh sửa nội dung trang thông tin.

### Quyết định đã chốt
- Nội dung trang giới thiệu, chính sách, FAQ cố định, không chỉnh sửa trên hệ thống; chỉ thông tin sản phẩm là sửa được (đã chốt 15/11/2026).
- Chỉ có một trang chính sách chung duy nhất (đã chốt 22/11/2026, giải quyết [GD]).
- Đường dẫn URL cố định cấp root: `/about`, `/policy`, `/faq`; trang không tồn tại trả HTTP 404 và hiển thị giao diện thông báo lỗi thân thiện kèm liên kết quay lại trang chủ (đã chốt 22/11/2026).
- Cơ chế render: hỗ trợ cả truy cập URL trực tiếp (render đầy đủ layout) và nạp mảnh nội dung qua HTMX (kèm `hx-push-url="true"`) khi bấm liên kết từ footer; HTTP response header gồm `Cache-Control: private, no-cache` và `Vary: HX-Request`, không dùng `ETag` (đã chốt 22/11/2026 theo BR-GIAIDOAN1).
- Lưu trữ nội dung: nội dung 3 trang được nhúng trực tiếp trong các template HTML/Jinja tĩnh phía backend, không tạo bảng trong database và không lưu Redis (đã chốt 22/11/2026).
- Xử lý lỗi 404 khi điều hướng HTMX: Sử dụng sự kiện `htmx:beforeSwap` trên giao diện storefront, khi `evt.detail.xhr.status === 404` và target là `#main-content` thì đặt `detail.shouldSwap = true` và `detail.isError = false` để nạp mảnh lỗi vào DOM. Không bật swap cho toàn bộ 4xx/5xx, giữ nguyên xử lý lỗi session 401/403 (đã chốt 23/11/2026).

### Giả định [GD]
- Không có (toàn bộ giả định đã được developer phê duyệt và chốt).

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt nội dung trang giới thiệu, chính sách, FAQ cố định, không chỉnh sửa
- v3 (2026-11-22): chốt toàn bộ giả định [GD] (1 trang chính sách chung, URL chuẩn `/about`, `/policy`, `/faq`, HTTP 404, SSR/HTMX fragment, cache headers); hoàn thiện Main Flow, Alternative Flows, Exceptions và Acceptance Criteria chuẩn Given/When/Then; chuyển trạng thái sang ready
- v4 (2026-11-22): làm rõ AC-8 và Postconditions về việc không thay đổi dữ liệu nghiệp vụ, đồng bộ với cơ chế kỹ thuật gia hạn identity.session theo BR-GIAIDOAN1; chi tiết hóa xử lý lỗi HTTP 404 cho cả request thông thường và request HTMX (AC-5, AC-6)
- v5 (2026-11-23): ghi nhận [GD] cho phát hiện #8 về contract swap 404 qua HTMX (E1.3, AC-6, UC-13-Q5); chuẩn hóa dùng sự kiện htmx:beforeSwap (detail.shouldSwap / isError) theo tài liệu chính thức HTMX; chuyển status về draft chờ developer chốt phương án
- v6 (2026-11-23): developer duyệt chốt xử lý swap 404 HTMX bằng sự kiện htmx:beforeSwap (Phương án 1), gỡ bỏ nhãn [GD] tại E1.3 và AC-6, cập nhật mục Quyết định đã chốt, chuyển trạng thái sang ready
