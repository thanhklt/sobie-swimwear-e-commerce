# UC-32: Quản lý nhà cung cấp

## Metadata
- **ID:** UC-32
- **Module:** inventory
- **Liên quan tới BR:** BR-005
- **Status:** draft

## Actor
Nhân viên

## Trigger
Nhân viên mở màn hình quản lý nhà cung cấp để xem, thêm, sửa, xóa hoặc ngừng hợp tác với một nhà cung cấp.

## Preconditions
- Nhân viên đã đăng nhập (UC-02).

## Main Flow
1. Nhân viên xem danh sách nhà cung cấp có phân trang và tìm theo tên chứa từ khóa; khi tìm kiếm, bỏ khoảng trắng đầu/cuối của tên và từ khóa, không phân biệt hoa/thường nhưng phân biệt dấu tiếng Việt.
2. Nhân viên chọn "Thêm nhà cung cấp".
3. Nhân viên nhập tên, số điện thoại, email, địa chỉ.
4. Nhân viên chọn "Lưu".
5. Hệ thống kiểm tra dữ liệu hợp lệ theo E1; tên bắt buộc và không trùng với nhà cung cấp khác, kể cả nhà cung cấp "Ngừng hợp tác". Khi so sánh tên, bỏ khoảng trắng đầu/cuối, không phân biệt hoa/thường nhưng phân biệt dấu tiếng Việt. Nếu trùng tên, xử lý theo E2.
6. Hệ thống lưu nhà cung cấp ở trạng thái "Đang hợp tác".
7. Hệ thống hiển thị danh sách có nhà cung cấp vừa thêm.

## Alternative Flows
- **1a. Tìm theo tên:**
  1. Nhân viên nhập từ khóa tên nhà cung cấp và chọn "Tìm kiếm".
  2. Hệ thống hiển thị các nhà cung cấp có tên chứa từ khóa theo quy tắc ở bước 1; nếu không có tên phù hợp thì danh sách kết quả trống.
  3. Nếu kết quả có nhiều trang, Nhân viên chuyển trang theo flow 1b.
- **1b. Chuyển trang danh sách:**
  1. Nhân viên chọn trang khác của danh sách nhà cung cấp hoặc danh sách kết quả tìm kiếm.
  2. Hệ thống hiển thị các nhà cung cấp thuộc trang đã chọn; nếu đang tìm kiếm thì giữ nguyên từ khóa và chỉ phân trang trong tập kết quả phù hợp.
- **2a. Sửa nhà cung cấp:**
  1. Từ danh sách, Nhân viên chọn nhà cung cấp cần sửa và chọn "Sửa".
  2. Nhân viên sửa thông tin và chọn "Lưu".
  3. Hệ thống kiểm tra như bước 5, loại trừ chính nhà cung cấp đang sửa khi kiểm tra trùng tên; nếu thiếu hoặc sai dữ liệu thì xử lý theo E1, nếu trùng tên nhà cung cấp khác thì xử lý theo E2.
  4. Hệ thống lưu thông tin đã sửa và hiển thị thông tin mới trong danh sách. Phiếu nhập đã có vẫn tham chiếu đúng nhà cung cấp.
- **2b. Ngừng hợp tác:**
  1. Từ danh sách, Nhân viên chọn nhà cung cấp "Đang hợp tác" và chọn "Ngừng hợp tác".
  2. Hệ thống chuyển nhà cung cấp sang "Ngừng hợp tác"; tên và các phiếu nhập cũ giữ nguyên.
  3. Nhà cung cấp không còn xuất hiện trong danh sách chọn khi lập phiếu nhập mới; các phiếu nhập cũ vẫn hiển thị đúng tên nhà cung cấp.
- **2c. Xóa nhà cung cấp chưa có phiếu nhập:**
  1. Từ danh sách, Nhân viên chọn nhà cung cấp và chọn "Xóa".
  2. Hệ thống kiểm tra có bất kỳ phiếu nhập nào tham chiếu nhà cung cấp hay không, không phân biệt trạng thái phiếu. Nếu có, xử lý theo E3.
  3. Nếu không có phiếu nhập nào tham chiếu, hệ thống xóa hẳn nhà cung cấp; nhà cung cấp không còn trong danh sách quản lý.

## Exceptions
- **E1. Thiếu hoặc sai dữ liệu:** thiếu tên (kể cả tên chỉ gồm khoảng trắng) hoặc số điện thoại, hoặc email sai định dạng → hệ thống báo lỗi theo từng trường, không lưu.
- **E2. Trùng tên:** tên trùng với nhà cung cấp khác theo quy tắc ở bước 5 → hệ thống báo lỗi tại trường tên, không lưu.
- **E3. Xóa nhà cung cấp đã có phiếu nhập:** nếu có bất kỳ phiếu nhập nào tham chiếu nhà cung cấp, kể cả "Nháp" hoặc "Đã hủy", hệ thống từ chối xóa, gợi ý chuyển sang "Ngừng hợp tác".

## Postconditions
- Thông tin nhà cung cấp được lưu hoặc nhà cung cấp chưa có phiếu nhập được xóa hẳn; chỉ nhà cung cấp "Đang hợp tác" được chọn khi lập phiếu nhập (UC-33).

## Acceptance Criteria

### AC-1: Thêm nhà cung cấp hợp lệ
Given: Nhân viên đã đăng nhập, tên "Công ty Biển Xanh" chưa tồn tại
When: Nhân viên nhập tên, số điện thoại, email hợp lệ và chọn "Lưu"
Then: nhà cung cấp được lưu với trạng thái "Đang hợp tác"
And: xuất hiện trong danh sách nhà cung cấp

### AC-2: Thiếu hoặc sai dữ liệu
Given: Nhân viên ở màn hình thêm hoặc sửa nhà cung cấp
When: Nhân viên lưu khi chưa nhập tên hoặc số điện thoại, tên chỉ gồm khoảng trắng, hoặc email sai định dạng
Then: hệ thống báo lỗi tại trường tương ứng, không lưu
And: không tạo nhà cung cấp mới hoặc thay đổi thông tin nhà cung cấp đã lưu

### AC-3: Trùng tên
Given: nhà cung cấp "Công ty Biển Xanh" đã tồn tại, ở trạng thái "Đang hợp tác" hoặc "Ngừng hợp tác"
When: Nhân viên thêm nhà cung cấp mới hoặc sửa một nhà cung cấp khác thành cùng tên hoặc tên chỉ khác hoa/thường, khoảng trắng đầu/cuối (ví dụ `  công ty biển xanh  `), rồi chọn "Lưu"
Then: hệ thống báo lỗi trùng tên tại trường tên, không lưu

### AC-4: Ngừng hợp tác
Given: nhà cung cấp X đang hợp tác, có hoặc chưa có phiếu nhập
When: Nhân viên chuyển X sang "Ngừng hợp tác"
Then: trạng thái X được lưu là "Ngừng hợp tác"
And: X không xuất hiện trong danh sách chọn khi lập phiếu nhập mới
And: nếu X đã có phiếu nhập thì các phiếu nhập cũ vẫn hiển thị đúng tên X

### AC-5: Không xóa được nhà cung cấp đã có phiếu nhập
Given: nhà cung cấp X được ít nhất một phiếu nhập tham chiếu, bất kể trạng thái phiếu ("Nháp", "Đã xác nhận" hoặc "Đã hủy")
When: Nhân viên xóa X
Then: hệ thống từ chối xóa và gợi ý chuyển sang "Ngừng hợp tác"
And: nhà cung cấp X và các phiếu nhập tham chiếu X được giữ nguyên

### AC-6: Sửa nhà cung cấp hợp lệ
Given: nhà cung cấp X đã tồn tại, ở trạng thái "Đang hợp tác" hoặc "Ngừng hợp tác", và đã có phiếu nhập tham chiếu
When: Nhân viên sửa tên X thành tên chưa trùng với nhà cung cấp khác, cập nhật số điện thoại, email, địa chỉ bằng dữ liệu hợp lệ và chọn "Lưu"
Then: thông tin mới được lưu trên chính nhà cung cấp X và hiển thị trong danh sách, không tạo nhà cung cấp mới
And: trạng thái hợp tác của X không đổi
And: các phiếu nhập cũ vẫn tham chiếu đúng nhà cung cấp X

### AC-7: Sửa không báo trùng với chính nhà cung cấp
Given: nhà cung cấp X có tên "Công ty Biển Xanh" và không có nhà cung cấp khác trùng tên theo quy tắc ở bước 5
When: Nhân viên sửa số điện thoại, email hoặc địa chỉ bằng dữ liệu hợp lệ, giữ nguyên tên hoặc nhập tên chỉ khác hoa/thường, khoảng trắng đầu/cuối (ví dụ `  công ty biển xanh  `), rồi chọn "Lưu"
Then: hệ thống không báo lỗi trùng tên với chính X
And: thông tin thay đổi được lưu trên chính nhà cung cấp X

### AC-8: Xóa nhà cung cấp chưa có phiếu nhập
Given: nhà cung cấp X tồn tại ở trạng thái "Đang hợp tác" hoặc "Ngừng hợp tác" và không có bất kỳ phiếu nhập nào tham chiếu
When: Nhân viên chọn "Xóa" nhà cung cấp X
Then: hệ thống xóa hẳn nhà cung cấp X
And: X không còn xuất hiện trong danh sách quản lý nhà cung cấp hoặc danh sách chọn khi lập phiếu nhập mới

### AC-9: Phân biệt dấu tiếng Việt khi kiểm tra trùng tên
Given: nhà cung cấp "Công ty Biển Xanh" đã tồn tại và chưa có nhà cung cấp tên "Công ty Bien Xanh" theo quy tắc ở bước 5
When: Nhân viên thêm nhà cung cấp mới hoặc sửa một nhà cung cấp khác thành tên "Công ty Bien Xanh", nhập các thông tin khác hợp lệ và chọn "Lưu"
Then: hệ thống không coi hai tên trên là trùng nhau và lưu thông tin hợp lệ

### AC-10: Phân trang danh sách và kết quả tìm kiếm
Given: tập kết quả cần hiển thị (toàn bộ danh sách nhà cung cấp hoặc kết quả tìm theo tên) có nhiều nhà cung cấp hơn số lượng tối đa của một trang, và dữ liệu không thay đổi trong lúc chuyển trang
When: Nhân viên xem danh sách và chuyển qua các trang của tập kết quả đó
Then: hệ thống hiển thị đúng các nhà cung cấp thuộc từng trang, không vượt số lượng tối đa của một trang
And: tổng hợp các trang không bị thiếu hoặc lặp nhà cung cấp trong tập kết quả
And: khi đang tìm kiếm, từ khóa được giữ nguyên và mọi trang chỉ chứa các nhà cung cấp có tên phù hợp

### AC-11: Tìm tên chứa từ khóa theo quy tắc đã chốt
Given: có các nhà cung cấp "Công ty Biển Xanh", "Xưởng BIỂN ĐỎ" và "Công ty Bien Xanh"
When: Nhân viên tìm theo từ khóa `  BIỂN  `
Then: tập kết quả có "Công ty Biển Xanh" và "Xưởng BIỂN ĐỎ"
And: không có "Công ty Bien Xanh" vì tìm kiếm phân biệt dấu tiếng Việt
And: các tên không chứa từ khóa sau khi bỏ khoảng trắng đầu/cuối và không phân biệt hoa/thường không xuất hiện trong kết quả

### AC-12: Tìm kiếm không có kết quả
Given: không có tên nhà cung cấp nào chứa từ khóa Nhân viên nhập theo quy tắc ở bước 1
When: Nhân viên chọn "Tìm kiếm"
Then: hệ thống hiển thị danh sách kết quả trống
And: dữ liệu nhà cung cấp đã lưu không thay đổi

## Dependencies
- **Upstream UC:** UC-02
- **Downstream UC:** UC-33, UC-37
- **External Systems:** không có

## Notes
- Danh sách nhà cung cấp thuộc portal quản trị, không cache; trả `Cache-Control: no-store` theo BR-GIAIDOAN1, Constraints chung.
- Data model hiện đã có các cột tên, số điện thoại, email, địa chỉ và trạng thái (`supplier_status`) của nhà cung cấp.

**Quyết định đã chốt**
- Thông tin nhà cung cấp gồm: tên, số điện thoại, email, địa chỉ (đã chốt 15/11/2026; đã có trong data model).
- Nhà cung cấp có trạng thái "Đang hợp tác" / "Ngừng hợp tác"; chỉ nhà cung cấp "Đang hợp tác" được chọn khi lập phiếu nhập (đã chốt 15/11/2026; đã có cột `supplier_status` trong data model).
- Cho phép xóa hẳn nhà cung cấp chưa có phiếu nhập; nếu có bất kỳ phiếu nhập nào tham chiếu, kể cả "Nháp" hoặc "Đã hủy", thì từ chối xóa và gợi ý chuyển sang "Ngừng hợp tác" (đã chốt 22/11/2026).
- Tên nhà cung cấp bắt buộc và không trùng với nhà cung cấp khác, kể cả nhà cung cấp "Ngừng hợp tác"; so sánh tên bỏ khoảng trắng đầu/cuối, không phân biệt hoa/thường nhưng phân biệt dấu tiếng Việt; khi sửa loại trừ chính nhà cung cấp đang sửa (đã chốt 22/11/2026).
- Danh sách có phân trang và tìm theo tên chứa từ khóa; khi tìm kiếm, bỏ khoảng trắng đầu/cuối của tên và từ khóa, không phân biệt hoa/thường nhưng phân biệt dấu tiếng Việt (đã chốt 22/11/2026).

**Giả định [GD]**
- Không còn.

## History
- v1 (2026-11-15): initial
- v2 (2026-11-15): chốt thông tin nhà cung cấp gồm tên, SĐT, email, địa chỉ; ghi chú ERD cần bổ sung cột
- v3 (2026-11-15): chốt trạng thái nhà cung cấp Đang hợp tác / Ngừng hợp tác (ERD thêm cột `supplier_status`)
- v4 (2026-11-22): chốt cho phép xóa hẳn nhà cung cấp chưa có phiếu nhập; làm rõ từ chối xóa khi còn phiếu tham chiếu ở bất kỳ trạng thái nào; cập nhật flow, E3 và AC-5, không thêm AC
- v5 (2026-11-22): chốt quy tắc tên bắt buộc, không trùng và danh sách phân trang, tìm theo tên; cập nhật bước 1, bước 4, flow 2a, E2 và AC-3; không thêm AC
- v6 (2026-11-22): đồng bộ AC-2 với E1 về thiếu số điện thoại; cập nhật Notes theo data model và constraint không cache danh sách quản trị; không thêm AC
- v7 (2026-11-22): hoàn thiện các bước Main Flow, Alternative Flows và kết quả AC-1–AC-5; AC-2 và AC-3 áp dụng cả khi sửa; chỉ cập nhật tài liệu UC, không triển khai code hoặc thêm AC
- v8 (2026-11-22): developer cho phép thêm, sửa, xóa AC; hoàn thiện AC-1–AC-12 cho toàn bộ flow đã chốt, bổ sung flow tìm kiếm và chuyển trang; chỉ cập nhật tài liệu UC
