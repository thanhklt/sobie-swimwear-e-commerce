# BR-GIAIDOAN1: Website bán đồ bơi — Đồ án Công nghệ phần mềm

> Format mỗi BR theo *Template BR-XXX-Name.md* (Phụ lục B, SDD Ebook). Đã bỏ các trường Owner, Stakeholders, Target Quarter và mục Related Use Cases theo yêu cầu. In Scope và Out of Scope để chung ở phần Tổng quan, không chia theo BR.
> `[GD]`: giả định của agent, chờ developer quyết định.

## Tổng quan

### Background

Đồ án môn Công nghệ phần mềm: xây dựng website bán đồ bơi online cho một cửa hàng giả định (1 kho, 1 kênh bán online). Phạm vi MVP được tách thành các BR theo nhóm nghiệp vụ ở bên dưới.

### Goal

Xây dựng website bán đồ bơi online cho một cửa hàng giả định (1 kho, 1 kênh bán online), hoàn thành toàn bộ nhóm tính năng bắt buộc và nghiệm thu đạt 100%, hạn chót hết ngày 06/12/2026.

### Success Metrics

- New_must_features_per_weekly_demo ≥ 1 tại mỗi buổi demo thứ Hai 16/11, 23/11, 30/11/2026 (đo qua checklist tính năng chạy được trong buổi demo)
- Must_acceptance_test_pass_rate = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu), ngày 07/12/2026 dùng kết quả test để báo cho cô.

### In Scope (MVP – hạn chót 06/12/2026)

- Tài khoản và phân quyền: Khách hàng tự đăng ký ở trang bán hàng (storefront) bằng email OTP rồi tạo mật khẩu Sobie, hoặc đăng ký với Google mà không cần mật khẩu Sobie. Thông tin hồ sơ được bổ sung sau khi đăng ký. Khách hàng đăng nhập ở storefront bằng mật khẩu Sobie hoặc dùng luồng Google chung cho cả đăng ký và đăng nhập. Nhân viên và Admin đăng nhập ở portal quản trị riêng. Có 3 vai trò cố định. Admin quản lý tài khoản và gán vai trò, còn Nhân viên vận hành cửa hàng.
- Hồ sơ khách hàng: Khách hàng tự bổ sung hoặc sửa thông tin cá nhân. Admin cũng có thể cập nhật hồ sơ Khách hàng từ portal quản trị.
- Đổi mật khẩu Sobie: Khách hàng, Nhân viên và Admin có thể tự đổi mật khẩu của mình.
- Trang bán hàng: trang chủ (gồm khối 5 sản phẩm bán chạy nhất 7 ngày gần nhất, bổ sung 21/11/2026), trang danh mục có phân trang, sắp xếp (mặc định sản phẩm mới nhất) và lọc theo giới tính, size, danh mục, bộ sưu tập, tìm kiếm theo tên hoặc từ khóa, chi tiết sản phẩm (chọn màu và size, ảnh, bảng size, tình trạng còn/hết hàng), các trang giới thiệu, chính sách, FAQ. Khách hàng thả tim để lưu sản phẩm vào danh sách yêu thích (wishlist)
- Sản phẩm: quản lý sản phẩm, biến thể theo màu × size, giá bán theo size, danh mục, bộ sưu tập và các thuộc tính
- Giỏ hàng và đặt hàng: khách chưa đăng nhập vẫn dùng được giỏ hàng, nhưng phải đăng nhập mới đặt hàng được. Thanh toán bằng COD hoặc chuyển khoản qua mã QR. Mọi đơn chuyển khoản dùng chung 1 tài khoản ngân hàng của cửa hàng; hệ thống tự đối soát qua webhook của dịch vụ bên thứ 3 theo dõi biến động số dư, không cần ai bấm xác nhận đã thanh toán
- Khuyến mãi 3 loại: theo sản phẩm, theo giá trị hóa đơn, voucher. Khuyến mãi theo sản phẩm giảm trực tiếp trên giá sản phẩm (hiển thị trên trang chi tiết sản phẩm). Hệ thống tự chọn mức giảm có lợi hơn cho khách giữa khuyến mãi theo hóa đơn và voucher. Khuyến mãi theo sản phẩm được tính cùng với mức giảm được chọn đó. Mọi loại khuyến mãi giảm theo phần trăm, không có mức giảm tối đa
- Đơn hàng: khách theo dõi và hủy đơn khi đơn chưa xử lý; đơn đã xác nhận thì khách không hủy được. Nhân viên xác nhận đơn, rồi bàn giao đơn đã xác nhận cho vận chuyển. Nhân viên được hủy đơn bất cứ lúc nào trước khi đơn vị vận chuyển nhận hàng, qua popup nhập lý do và xác nhận; đơn bị hủy thì hệ thống tự cộng lại hàng vào tồn kho. Đơn chuyển khoản quá 24 giờ kể từ lúc đặt mà chưa thanh toán thì hệ thống tự hủy
- Vận chuyển mô phỏng: một trang giả lập đơn vị vận chuyển, không cần đăng nhập và là 1 trang duy nhất. Trang hiển thị đơn "Chờ lấy hàng" với nút "Đã nhận hàng" (đơn vị vận chuyển đã lấy được hàng từ cửa hàng) và đơn "Đang giao" với nút "Đã giao" / "Giao không thành công"; trang tự động cập nhật trạng thái đơn về website
- Thanh toán chuyển khoản tự động: website hiển thị mã VietQR của tài khoản cửa hàng, điền sẵn số tiền và nội dung chuyển khoản chứa mã đơn. Dịch vụ SePay gửi webhook khi tài khoản nhận tiền; website tự khớp giao dịch với đơn và chuyển đơn sang "Đã thanh toán". Demo bằng 1 sản phẩm demo giá 2.000đ (xem BR-006)
- Hóa đơn tự xuất khi giao thành công; khách và nhân viên chỉ xem (đã chốt 20/11/2026)
- Kho: quản lý nhà cung cấp, lập và xác nhận phiếu nhập. Đơn giao không thành công thì hệ thống tự cộng lại hàng vào tồn kho (không có thao tác nhận hàng hoàn). Nhân viên xem được tồn kho. Tồn kho không bao giờ âm
- Cấu hình cửa hàng (hard-code hoặc biến môi trường, không chỉnh sửa trên hệ thống): phí vận chuyển cố định cho mọi đơn (biến môi trường, mặc định 12.000đ), hotline, link Zalo, thông tin người gửi, tài khoản nhận chuyển khoản, ngưỡng tồn kho thấp
- Dashboard: doanh thu, lợi nhuận gộp, số đơn theo trạng thái, sản phẩm bán chạy, tồn kho thấp, tiền nhập hàng theo nhà cung cấp
- Admin quản lý tài khoản: toàn quyền tạo tài khoản với mọi vai trò (Khách hàng, Nhân viên, Admin), sửa, khóa và mở khóa
- Nhân viên có chức năng Quản lý khách hàng để xem thông tin và khóa tài khoản Khách hàng.

### Out of Scope

- Mega menu, bộ lọc nâng cao, thêm nhanh vào giỏ từ thẻ sản phẩm
- Trang Outlet, sổ nhiều địa chỉ
- Quên mật khẩu — làm ở giai đoạn 2. Giai đoạn 1 trang đăng nhập storefront vẫn có nút "Quên mật khẩu" cho Khách hàng, nhưng bấm vào không có hành động nào (đã chốt 21/11/2026)
- Đánh giá sản phẩm (review) — làm ở giai đoạn 2
- Blog, trang cộng đồng, góp ý, thanh thông báo chạy, banner tùy chỉnh
- Tạo vai trò mới hoặc cấu hình quyền
- Đổi/trả hàng theo yêu cầu khách, hoàn tiền trong hệ thống. Khách đã chuyển khoản rồi mới hủy đơn thì tự liên hệ cửa hàng; hệ thống không xử lý
- Freeship theo ngưỡng, quà tặng theo bậc đơn, tích điểm thành viên
- Email marketing (nhắc giỏ hàng, báo giảm giá), AI chatbox tư vấn
- Nhiều kho hoặc chi nhánh, bán trên sàn TMĐT, POS tại cửa hàng
- Hóa đơn điện tử VAT, kết nối đơn vị vận chuyển thật
- Kết nối trực tiếp API ngân hàng, cổng thanh toán thẻ hoặc ví điện tử. Website chỉ nhận thông báo giao dịch đến từ dịch vụ theo dõi biến động số dư bên thứ 3
- Trang giả lập xác nhận chuyển khoản (thay bằng đối soát tự động qua dịch vụ bên thứ 3, chốt 20/11/2026)
- Đa ngôn ngữ
- Chức năng chỉnh sửa cấu hình cửa hàng
- Thao tác nhận hàng hoàn thủ công, tính giá trị hàng hoàn
- Chỉ số hiệu quả khuyến mãi trên dashboard

### Constraints chung

Áp dụng cho mọi BR bên dưới.

- **Technical — Kiến trúc Backend:** thiết kế theo kiến trúc 3 tầng (3-layer architecture): `Route` → `Service` → `Repository` → `Database`. Không gọi tắt tầng (Route không gọi trực tiếp Repository hoặc Database).
- **Technical — Cache (đã chốt 21/11/2026, cập nhật cho SSR):** website render HTML phía server (FastAPI + Jinja + HTMX). **Không phải danh sách nào cũng cache:** chỉ dữ liệu công khai, giống nhau với mọi người xem, mới được cache; trang và danh sách gắn với một người dùng (cần đăng nhập) không cache, để luôn đúng dữ liệu mới nhất và không lộ dữ liệu trên máy dùng chung.
  - **Được cache — cache dữ liệu ở Redis, không cache HTML** (HTML vẫn render lại mỗi request vì có phần riêng của từng người):
    - Danh mục, thuộc tính sản phẩm (giới tính, size, màu, bộ sưu tập), danh sách sản phẩm theo danh mục và các khối trang chủ: key có chứa *số phiên bản catalog*; mỗi khi sản phẩm, khuyến mãi hoặc tồn kho thay đổi thì tăng số phiên bản, key cũ tự hết hiệu lực; TTL dự phòng 5 phút.
    - Khuyến mãi đang hiệu lực: cache ở Redis; TTL hết hạn đúng mốc bắt đầu / kết thúc gần nhất của khuyến mãi theo hóa đơn và voucher, xóa key khi Nhân viên tạo hoặc kết thúc khuyến mãi `[GD]`.
    - Khối bán chạy trang chủ: xem Constraints của BR-002.
  - **Lỗi Redis sau khi DB đã commit — UC-14, UC-15, UC-16, UC-17 (đã chốt 22/11/2026, mở rộng UC-14/15 ngày 23/11/2026):** Khi tạo/sửa/đổi trạng thái/xóa sản phẩm hoặc gallery, tạo/xóa/đổi trạng thái biến thể, lưu giá theo size hoặc thêm/sửa/xóa danh mục, bộ sưu tập, thuộc tính, hệ thống commit PostgreSQL trước rồi mới tăng số phiên bản catalog tại Redis; nếu DB rollback thì không tăng phiên bản. Nếu cập nhật Redis bị lỗi hoặc timeout sau commit, hệ thống ghi log cảnh báo, vẫn thông báo thao tác thành công và không rollback dữ liệu DB đã commit. Chỉ dữ liệu thực sự đọc từ cache công khai có thể cũ cho đến khi hết TTL dự phòng còn lại (tối đa 5 phút) hoặc có lần tăng phiên bản thành công tiếp theo; không coi DB và Redis là một transaction nguyên tử. Lượt truy cập tiếp theo làm mới cache sẽ nhận dữ liệu mới; TTL không tự cập nhật DOM của trang đã mở. Các luồng không cache (tìm kiếm, wishlist, giỏ/đặt hàng, portal quản trị) và bước lọc trạng thái hiện hành từ DB khi render khối Bán chạy không chờ TTL hay phụ thuộc tăng phiên bản Redis thành công (UC-14-Q10, UC-15-Q7, UC-17-Q6; developer duyệt đồng bộ tại Codex 23/11/2026).
  - **Chặn mua từ giao diện cũ:** UC-18 kiểm tra đồng thời `product_status = ACTIVE` của sản phẩm cha, `variant_status = ACTIVE` của biến thể và tồn kho hiện hành từ DB qua Service công khai trước khi thêm giỏ; UC-19/20 kiểm tra lại sau khi giữ khóa sản phẩm cha trong transaction tạo đơn và từ chối nếu sản phẩm hoặc biến thể không còn ACTIVE. TTL không thay thế kiểm tra nghiệp vụ này (UC-15-Q7; bổ sung điều kiện sản phẩm cha theo yêu cầu xử lý rà soát vòng 3 tại Codex ngày 23/11/2026).
  - **Không cache:**
    - Kết quả tìm kiếm.
    - Mọi trang và danh sách cần đăng nhập: hồ sơ, giỏ hàng, wishlist, đơn hàng, hóa đơn của Khách hàng; mọi danh sách trong portal quản trị (tài khoản, đơn hàng, nhà cung cấp, phiếu nhập, khuyến mãi, voucher, tồn kho, hóa đơn…).
    - Dashboard (BR-007): truy vấn trực tiếp Database.
    - Giỏ của Khách vãng lai lưu ở `localStorage` của trình duyệt, không đưa vào Redis; tồn kho và voucher lúc đặt hàng luôn đọc từ Database trong transaction.
  - **HTTP header:** HTML có phần riêng của từng người (tên tài khoản trên header, số lượng trong giỏ, nút thả tim) nên không trang HTML nào được đánh dấu `public`.
    - Trang công khai (trang chủ, danh mục, tìm kiếm, chi tiết sản phẩm, trang giới thiệu / chính sách / FAQ) và mảnh HTMX của chúng: `Cache-Control: private, no-cache`. Không dùng `ETag` (đã chốt 21/11/2026): server vẫn phải render xong HTML mới băm được nên `ETag` chỉ tiết kiệm băng thông, không đáng thêm một middleware.
    - Trang cần đăng nhập (storefront và portal quản trị), trang đăng nhập / đăng ký, trang giả lập vận chuyển: `Cache-Control: no-store` để ngăn lưu trong HTTP cache. Header này không kiểm soát bản chụp DOM trong lịch sử HTMX.
    - **Lịch sử HTMX (review PR #7, 23/11/2026):** layout chứa nội dung gắn với phiên, kể cả header cá nhân hóa trên trang công khai, phải có `hx-history="false"` trước khi rời trang để không lưu DOM vào `localStorage`. Đặt `historyRestoreAsHxRequest = false`; khi Back/Forward cần khôi phục, request đến server lấy trang đầy đủ và kiểm tra lại phiên hiện hành. Sau đăng xuất không khôi phục dữ liệu riêng của phiên cũ (UC-13 AC-9; [tài liệu HTMX](https://htmx.org/attributes/hx-history/)).
    - Route trả cả trang đầy đủ lẫn mảnh HTMX: thêm `Vary: HX-Request`, để trình duyệt không lẫn mảnh HTML với trang đầy đủ khi bấm Back.
    - File tĩnh `/static` (CSS, JS, ảnh giao diện): `Cache-Control: public, max-age=31536000, immutable`; tên file kèm mã phiên bản để đổi nội dung là đổi URL.
    - Webhook SePay (JSON, BR-006): `Cache-Control: no-store`.
- **Technical — Xác thực (đã chốt 21/11/2026, thay cơ chế access / refresh token của v20):** website render phía server (FastAPI + Jinja + HTMX) và duy trì trạng thái đăng nhập Sobie bằng **phiên phía server** (session).
  - Đăng nhập thành công thì tạo 1 dòng trong bảng `identity.session`: hệ thống sinh mã phiên ngẫu nhiên, chỉ lưu bản băm SHA-256 trong DB, gửi mã gốc trong cookie `HttpOnly`, `Secure`, `SameSite=Lax`. Một tài khoản có thể có nhiều phiên (nhiều thiết bị).
  - Storefront và portal quản trị dùng 2 cookie phiên khác tên, nên một trình duyệt có thể đăng nhập cùng lúc vào cả hai cổng (đã chốt 23/11/2026).
  - Hạn phiên: **Khách hàng 30 phút**, **Nhân viên / Admin 1 giờ**, tính từ lần thao tác cuối; mỗi request hợp lệ gia hạn phiên (đã chốt 21/11/2026). Hết hạn thì coi như chưa đăng nhập.
  - Mỗi request: tìm phiên theo bản băm của mã trong cookie, còn hạn thì đọc vai trò và trạng thái từ `identity.account`. Phiên không lưu vai trò.
  - **Quay lại sau đăng nhập:** Khách hàng đăng nhập storefront từ checkout hoặc nút tim trên trang chi tiết UC-12 được quay lại theo `return_url` nội bộ hợp lệ thuộc đúng hai luồng này. Server kiểm tra đích sau chuẩn hóa, không chấp nhận scheme/host, dạng `//`, gạch chéo ngược, ký tự điều khiển hoặc biến thể mã hóa dẫn tới đích bị cấm; đích khác phạm vi bị bỏ qua và dùng nhánh mặc định của UC-02. Không dùng `return_url` để bỏ qua kiểm tra vai trò/cổng hoặc tự thích/bỏ thích; portal quản trị không dùng đích quay lại storefront (UC-12-Q8, developer yêu cầu đồng bộ UC-02/38 tại Codex 23/11/2026).
  - Kết thúc phiên: đăng xuất (UC-03) xóa phiên hiện tại, có hiệu lực ngay. Đổi vai trò (UC-07), khóa tài khoản (UC-08), đổi mật khẩu (UC-05) xóa mọi phiên của tài khoản trong cùng transaction với thao tác đó.
  - Chống giả mạo request (CSRF): cookie `SameSite=Lax` cộng kiểm tra header `Origin` ở mọi request ghi (POST, PUT, PATCH, DELETE, kể cả request HTMX); `Origin` khác domain của website thì từ chối. Không dùng CSRF token. Frontend và backend chạy cùng domain.
  - Giới hạn tần suất (rate limit) theo IP, đếm ở Redis, áp dụng cho đăng nhập bằng mật khẩu. Yêu cầu vượt 5 lần/phút nhận HTTP 429. Đăng nhập Google không tính vào và không chịu giới hạn của bộ đếm này (đã chốt 23/11/2026).
- **Technical — Cấu hình cửa hàng:** không có chức năng chỉnh sửa trên hệ thống và không có BR riêng. Gồm: hotline, link Zalo, thông tin người gửi, tài khoản nhận chuyển khoản, ngưỡng tồn kho thấp (hard-code); phí vận chuyển cố định cho mọi đơn nạp từ biến môi trường, mặc định 12.000đ (chốt 20/11/2026).
- **Technical — Webhook thanh toán:** website phải có địa chỉ công khai để dịch vụ bên thứ 3 gửi webhook tới. Giai đoạn demo dùng ngrok forward cổng local ra internet (đã chốt 20/11/2026); mỗi khi địa chỉ ngrok thay đổi phải cập nhật lại URL webhook trên trang quản trị của dịch vụ. Khóa xác thực webhook (API key) nạp qua biến môi trường, không hard-code trong mã nguồn.
- **Timeline:** demo hằng tuần thứ Hai 16/11, 23/11, 30/11/2026; hoàn thành và nghiệm thu hết ngày 06/12/2026; 07/12/2026 báo cáo kết quả.

### Danh mục BR


| ID                                                          | Tên                                      | Status |
| ----------------------------------------------------------- | ----------------------------------------- | ------ |
| [BR-001](#br-001-tài-khoản-và-phân-quyền)              | Tài khoản và phân quyền              | draft  |
| [BR-002](#br-002-trang-bán-hàng-và-quản-lý-sản-phẩm) | Trang bán hàng và quản lý sản phẩm | draft  |
| [BR-003](#br-003-giỏ-hàng-đặt-hàng-và-hóa-đơn)     | Giỏ hàng, đặt hàng và hóa đơn    | draft  |
| [BR-004](#br-004-khuyến-mãi)                              | Khuyến mãi                              | draft  |
| [BR-005](#br-005-kho-và-nhập-hàng)                       | Kho và nhập hàng                       | draft  |
| [BR-006](#br-006-vận-chuyển-mô-phỏng-và-thanh-toán-chuyển-khoản-tự-động) | Vận chuyển mô phỏng và thanh toán chuyển khoản tự động | draft  |
| [BR-007](#br-007-dashboard-báo-cáo)                       | Dashboard báo cáo                       | draft  |

### Open Questions chung

- [ ]  `[GD]` Cách gom các mục In Scope thành 7 BR như bảng trên có đúng ý không?
- [ ]  `[GD]` Success Metric của từng BR đang suy ra từ metric tổng (100% acceptance test của nhóm tính năng đó). Có cần metric riêng cho từng BR không?
- [X]  Constraint cache: "danh sách" gồm những danh sách nào — chỉ danh sách phía khách (danh mục, tìm kiếm) hay cả danh sách trong trang quản trị (đơn hàng, tài khoản, phiếu nhập…)? Dữ liệu được phép cũ tối đa bao lâu? → Không phải danh sách nào cũng cache: chỉ dữ liệu công khai (danh mục, thuộc tính, danh sách sản phẩm theo danh mục, các khối trang chủ, khuyến mãi đang hiệu lực, khối bán chạy) được cache ở Redis; kết quả tìm kiếm, mọi trang và danh sách cần đăng nhập (kể cả portal quản trị) và dashboard không cache (đã chốt 21/11/2026, cập nhật cho SSR; xem Constraints chung — Cache).
- [X]  Danh sách trong khu vực quản trị có cần chiến lược cache không? → Không cache: luôn đọc Database, trả `Cache-Control: no-store` (đã chốt 21/11/2026).

---

## BR-001: Tài khoản và phân quyền

### Metadata

- **ID:** BR-001
- **Status:** draft

### Background

Khách phải có tài khoản mới đặt hàng được, và cửa hàng cần tách người mua với người vận hành. Hệ thống dùng 3 vai trò cố định, không cấu hình quyền.

### Goal

Khách hàng tự đăng ký, đăng nhập và quản lý hồ sơ của mình; Admin quản lý được mọi tài khoản với 3 vai trò cố định.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng tài khoản = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints

- Theo *Constraints chung*.
- Email, vai trò, trạng thái và thông tin hồ sơ của cả 3 vai trò dùng chung bản ghi tài khoản (đã chốt 21/11/2026, thay quyết định ngày 15/11/2026 tách hồ sơ riêng theo vai trò). Không có username riêng. Email là duy nhất. Nếu tài khoản có số điện thoại, số đó cũng phải duy nhất.
- Khách tự đăng ký bằng email phải dùng email chưa có tài khoản Sobie, xác minh qua OTP rồi tạo mật khẩu Sobie. OTP có hiệu lực 5 phút và chỉ có thể yêu cầu gửi lại khi đủ 5 phút từ lần gửi gần nhất. Sau khi tạo tài khoản thành công, Sobie chuyển khách đến màn hình đăng nhập theo [UC-01](../use-cases/identity/UC-01-register-account.md).
- Trang đăng ký và đăng nhập dùng chung nút “Đăng nhập với Google”. Sau khi xác thực thành công và nhận email đã được Google xác minh, Sobie ưu tiên tìm tài khoản theo định danh Google (`sub`). Nếu chưa tìm thấy theo `sub`, Sobie dùng email đã xác minh để liên kết tài khoản Khách hàng đang Hoạt động chưa có liên kết Google, không gửi OTP. Nếu chưa có tài khoản theo email, Sobie tạo tài khoản Khách hàng kèm giỏ hàng và danh sách yêu thích trống theo [UC-01](../use-cases/identity/UC-01-register-account.md). Việc tạo hoặc liên kết tài khoản và cấp phiên storefront diễn ra trong cùng một transaction. Khách được đưa tới trang chủ hoặc quay lại checkout theo [UC-02](../use-cases/identity/UC-02-login.md).
- Đăng ký qua Google lưu email đã xác minh và định danh Google (`sub`); đăng ký trực tiếp lưu email đã xác minh và mật khẩu đã băm. Họ tên, ngày sinh, số điện thoại và địa chỉ nhận hàng được khách bổ sung qua UC-04.
- Tài khoản có mật khẩu Sobie đăng nhập bằng email hoặc số điện thoại đã lưu kèm mật khẩu. Khách hàng có liên kết Google có thể đăng nhập ở storefront bằng Google mà không cần nhập hoặc tạo mật khẩu Sobie. Khi tài khoản chỉ dùng Google, đăng nhập qua biểu mẫu mật khẩu trả thông báo "Thông tin đăng nhập không đúng".
- Mỗi tài khoản có mã do hệ thống cấp: Khách hàng `KH-<ngày đăng ký>-<4 số>`, Nhân viên `NV-<họ tên>-<ngày sinh>-<4 số>`, Admin `AD-<họ tên>-<ngày sinh>-<4 số>`; bộ đếm 4 số riêng cho từng loại; ngày sinh bắt buộc với Nhân viên và Admin. Mã không sửa được, trừ khi đổi vai trò Nhân viên ↔ Admin thì cấp mã mới (đã chốt 21/11/2026).
- Admin có toàn quyền tạo tài khoản với bất kỳ vai trò nào trong 3 vai trò cố định (Khách hàng, Nhân viên, Admin), không chỉ tài khoản nội bộ (đã chốt 20/11/2026).
- Khi tạo tài khoản qua [UC-06](../use-cases/identity/UC-06-create-account.md), Admin nhập email và số điện thoại chưa được tài khoản khác sử dụng, đặt mật khẩu ban đầu có ít nhất 6 ký tự và chọn vai trò từ danh sách 3 vai trò cố định. Hệ thống cấp mã và tạo tài khoản trong cùng một transaction. Hệ thống có sẵn một tài khoản Admin ở trạng thái Hoạt động khi khởi tạo lần đầu (đã chốt 23/11/2026).
- Tài khoản do Admin tạo dùng được ngay, không bắt buộc đổi mật khẩu ở lần đăng nhập đầu (đã chốt 20/11/2026).
- Admin chỉ đổi được vai trò qua lại giữa Nhân viên và Admin. Không đổi Khách hàng sang Nhân viên / Admin và không đổi Nhân viên / Admin sang Khách hàng. Vai trò mới có hiệu lực ngay, tài khoản đang đăng nhập bị đăng xuất; thông tin cá nhân và thông tin đăng nhập giữ nguyên (đã chốt 20/11/2026, thay quyết định cho đổi sang mọi vai trò cùng ngày).
- `[GD]` Đổi vai trò giữ nguyên lịch sử thao tác của tài khoản.
- Từ khi khởi tạo, hệ thống luôn phải có ít nhất một tài khoản vai trò Admin ở trạng thái Hoạt động. Admin được tự đổi vai trò hoặc tự khóa nếu sau thao tác vẫn còn một Admin Hoạt động. UC-07 và UC-08 phải kiểm tra ràng buộc trong cùng transaction với cập nhật tài khoản và bảo đảm ràng buộc khi hai thao tác diễn ra đồng thời (xác nhận lại 23/11/2026).
- Admin được khóa và mở khóa tài khoản của cả ba vai trò, tuân theo ràng buộc trên. Hồ sơ, đơn hàng và dữ liệu nghiệp vụ gắn với tài khoản giữ nguyên khi khóa hoặc mở khóa (đã chốt 23/11/2026).
- Storefront chỉ cho tài khoản Khách hàng đăng nhập. Nhân viên và Admin đăng nhập ở portal quản trị riêng. Tài khoản đăng nhập sai cổng chỉ nhận thông báo "Thông tin đăng nhập không đúng", giống trường hợp tài khoản không tồn tại hoặc sai mật khẩu (thông báo hai cổng đã chốt 23/11/2026).
- Quên mật khẩu làm ở giai đoạn 2. Giai đoạn 1 storefront hiển thị nút "Quên mật khẩu" và giữ khách ở trang đăng nhập khi bấm nút (đã chốt 21/11/2026). Portal quản trị không hiển thị nút trong giai đoạn 1 (đã chốt 23/11/2026).
- Cơ chế phiên đăng nhập theo *Constraints chung — Xác thực* (phiên phía server lưu ở `identity.session`). Đổi vai trò, khóa tài khoản và đổi mật khẩu đều kết thúc ngay mọi phiên của tài khoản, kể cả phiên đang dùng để đổi mật khẩu (đã chốt 21/11/2026).
- Khách hàng tự sửa họ tên, ngày sinh, địa chỉ và số điện thoại qua UC-04. Email trên hồ sơ storefront chỉ xem. Admin có thể cập nhật hồ sơ Khách hàng, gồm email, qua UC-07 (đã chốt 26/11/2026).
- Trong portal quản trị, Nhân viên được xem thông tin tài khoản Khách hàng qua UC-07 và khóa tài khoản Khách hàng qua UC-08. Quyền sửa và mở khóa tài khoản trong portal thuộc Admin (đã chốt 23/11/2026).
- Cả ba vai trò được tự đổi mật khẩu Sobie qua UC-05 nếu tài khoản đã có mật khẩu Sobie. Mật khẩu mới có ít nhất 6 ký tự và phải khác mật khẩu hiện tại (đã chốt 23/11/2026).

### Open Questions

- [X]  Admin đổi vai trò được giữa những vai trò nào? → Chỉ giữa Nhân viên và Admin; Khách hàng không đổi sang vai trò nội bộ và ngược lại (đã chốt lại 20/11/2026, thay câu trả lời "mọi vai trò" trước đó).
- [X]  Admin có được tự khóa chính mình không? → Được, khi hệ thống còn Admin khác đang hoạt động (đã chốt 20/11/2026).
- [X]  Tài khoản Khách hàng do Admin tạo có bắt buộc đổi mật khẩu ở lần đăng nhập đầu không? → Không, dùng được ngay như tài khoản khách tự đăng ký (đã chốt 20/11/2026).
- [X]  Admin được tạo tài khoản với vai trò nào? → Mọi vai trò: Khách hàng, Nhân viên, Admin (đã chốt 20/11/2026).
- [X]  Khi tự đăng ký, khách cần cung cấp những thông tin nào? → Xác minh email bằng OTP rồi tạo mật khẩu Sobie, hoặc xác thực qua Google. Khách bổ sung thông tin hồ sơ, gồm số điện thoại, ở UC-04 (đã chốt 23/11/2026, thay yêu cầu nhập cả email và số điện thoại khi đăng ký ngày 15/11/2026).
- [X]  Nhân viên và Admin khác nhau về quyền thế nào? → Admin quản trị tài khoản và gán vai trò. Nhân viên vận hành cửa hàng, được xem thông tin và khóa tài khoản Khách hàng (cập nhật 23/11/2026).

---

## BR-002: Trang bán hàng và quản lý sản phẩm

### Metadata

- **ID:** BR-002
- **Status:** draft

### Background

Khách cần xem, tìm và chọn đúng sản phẩm (màu, size) trước khi mua; cửa hàng cần tự quản lý danh mục sản phẩm và giá bán.

### Goal

Khách tìm và xem được sản phẩm cùng tình trạng còn/hết hàng theo từng màu và size; Nhân viên quản lý được sản phẩm, biến thể, giá và phân loại. Khi đã nhập kho xác nhận, sản phẩm chỉ được sửa Mô tả theo quy tắc khóa bên dưới.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng trang bán hàng và sản phẩm = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints

- Theo *Constraints chung*. Danh sách sản phẩm ở trang danh mục và các khối trang chủ được cache ở Redis; kết quả tìm kiếm không cache (Constraints chung — Cache).
- Trang giới thiệu, chính sách, FAQ có nội dung cố định, không chỉnh sửa trên hệ thống; chỉ thông tin sản phẩm là sửa được (đã chốt 15/11/2026).
- Lỗi trang thông tin UC-13 qua HTMX vẫn trả HTTP 404; sự kiện `htmx:beforeSwap` chỉ cho swap response 404 vào target `#main-content` để thông báo lỗi thực sự hiện trong DOM. Không bật swap mọi 4xx/5xx và không thay xử lý session 401/403 (UC-13-Q5, developer chốt 23/11/2026).
- Lọc sản phẩm theo giới tính, size, danh mục, bộ sưu tập (đã chốt 15/11/2026).
- Sắp xếp ưu tiên sản phẩm mới nhất (đã chốt 15/11/2026).
- Danh sách danh mục và tìm kiếm: Mới nhất sắp theo `product_created_at DESC, product_id ASC`; Giá tăng/giảm theo giá thực tế thấp nhất sau khuyến mãi (`effective_min_price ASC` hoặc `DESC`), luôn dùng `product_id ASC` làm khóa phụ cuối cùng. Tập dữ liệu cố định cho thứ tự nhất quán khi phân trang hoặc tải lại; không cam kết giữ nguyên các trang khi dữ liệu thay đổi (23/11/2026, UC-10-Q11; đồng bộ UC-11 theo duyệt tại Codex).
- Giá bán chỉ thay đổi theo size; cùng size khác màu thì cùng giá (đã chốt 15/11/2026). ERD hiện để giá ở biến thể (`variant_sell_price`), cần điều chỉnh hoặc đảm bảo đồng bộ.
- **Khóa sản phẩm sau nhập kho (review PR #7, developer chốt tại Codex 23/11/2026; UC-14-Q11/UC-17-Q7):** Có ít nhất một biến thể thuộc phiếu nhập `CONFIRMED` thì Nhân viên chỉ được sửa Mô tả của toàn sản phẩm. Khóa tên, danh mục, giới tính, bộ sưu tập, gallery, giá bán, trạng thái sản phẩm, thêm/xóa/đổi trạng thái mọi biến thể; không được đổi tên taxonomy dùng chung nếu tác động sản phẩm đã nhập. Không mở khóa khi tồn kho về 0; DRAFT/CANCELLED chưa kích hoạt khóa sửa này, nhưng điều kiện chặn xóa do từng liên kết phiếu nhập vẫn giữ nguyên. Quy tắc này ưu tiên hơn quyền đổi giá/ngừng bán/thêm biến thể đã chốt trước đó; phải cấu hình trước xác nhận nhập kho, không tự mở ngoại lệ cho sản phẩm đã nhập khi chưa định giá hoặc đang INACTIVE. Khóa áp dụng thao tác chỉnh sửa Catalog, không thay thế giao dịch tồn kho của module inventory. Server kiểm tra lại qua Service inventory trong cùng transaction sau khóa sản phẩm cha; xác nhận nhập phải dùng cùng hợp đồng tuần tự hóa tại Notes UC-14.
- **Thứ tự khóa liên UC (đồng bộ theo yêu cầu xử lý rà soát tại Codex 23/11/2026):** UC-14/15 tạo/đặt tham chiếu phải lấy đủ khóa taxonomy `FOR KEY SHARE` theo tên bảng rồi UUID trước khóa sản phẩm; UC-17 sửa/xóa mục lấy `FOR UPDATE` trên taxonomy trước sản phẩm. Sản phẩm khóa theo product_key ASC trước biến thể theo variant_key ASC; không giữ khóa sản phẩm rồi chờ taxonomy. UC-34 khóa dòng phiếu nhập, gọi Service Catalog dùng cùng session khóa sản phẩm rồi biến thể trước xác nhận/cộng tồn. Catalog kiểm tra CONFIRMED bằng Service inventory chỉ đọc dữ liệu đã commit, không lấy khóa phiếu nhập sau khóa sản phẩm. Giao thức dùng READ COMMITTED; truy vấn kiểm tra CONFIRMED mới chạy sau khi được cấp khóa sản phẩm. Các Service giữ khóa đến commit/rollback và đọc lại sau khi chờ; DB và Redis vẫn tách biệt như chính sách cache.
- Tập biến thể tính giá thẻ (UC-09/10/11) và khoảng giá chi tiết khi có tập hợp lệ (UC-12): chỉ gồm biến thể `variant_status = ACTIVE` có `variant_sell_price > 0`, không phụ thuộc tồn kho. Biến thể INACTIVE hoặc chưa có giá không tham gia min/max; biến thể ACTIVE có giá nhưng hết hàng vẫn tham gia. Giá sau khuyến mãi làm tròn theo `ROUND_HALF_UP`. Nhãn "Hết hàng" trên thẻ hiển thị khi không còn biến thể trong tập này có tồn kho khả dụng > 0 (23/11/2026, UC-10-Q9; developer duyệt đồng bộ tại Codex).
- Điều kiện xuất hiện trong danh sách trang chủ/danh mục/tìm kiếm: sản phẩm cha ACTIVE và có ít nhất một biến thể ACTIVE có giá > 0. Loại từng sản phẩm không đủ điều kiện trước khi tính tổng số, tổng trang hoặc lấy giới hạn hiển thị; không đổi trạng thái DB và không ẩn sản phẩm chỉ vì hết tồn kho. Danh sách rỗng dùng thông báo/ẩn khối tương ứng, không sinh trang 0 (23/11/2026, UC-10-Q10; developer duyệt đồng bộ tại Codex).
- URL chi tiết trực tiếp khi sản phẩm cha ACTIVE nhưng không còn biến thể ACTIVE có giá hợp lệ: vẫn trả HTTP 200, hiển thị tên/mô tả/ảnh và thông báo "Sản phẩm tạm ngừng kinh doanh", không hiển thị khoảng giá, vô hiệu hóa màu/size/số lượng/thêm giỏ. Sản phẩm cha INACTIVE hoặc không tồn tại vẫn trả 404 theo UC-12 E1 (UC-12-Q9b, developer chốt và yêu cầu đồng bộ tại Codex 23/11/2026).
- Ảnh sản phẩm (gallery) gắn theo sản phẩm, không theo màu (đã chốt 15/11/2026).
- Bảng size dùng chung cho cả cửa hàng, nội dung cố định (đã chốt 15/11/2026).
- Wishlist: Khách hàng thả tim để lưu sản phẩm vào danh sách yêu thích; mỗi sản phẩm chỉ có 1 lần trong danh sách của một tài khoản (đã chốt 15/11/2026, theo ERD).
- Khách vãng lai bấm tim trên trang chi tiết đăng nhập xong quay lại trang đó qua UC-02; việc đăng nhập không tạo/xóa wishlist_item. Chưa lưu thì tim chưa chọn và khách chủ động bấm lại; đã lưu từ trước thì tim đã chọn, bảo toàn dữ liệu hiện có (UC-12-Q4/Q8, đồng bộ UC-38 theo yêu cầu tại Codex 23/11/2026).
- Các khối sản phẩm trên trang chủ (đã chốt 22/11/2026, UC-09-Q1; cập nhật 23/11/2026 theo UC-10-Q10): khối Hàng mới hiển thị tối đa 8 sản phẩm hợp lệ mới nhất theo `product_created_at` giảm dần; mỗi bộ sưu tập có sản phẩm hợp lệ hiển thị tên bộ sưu tập và tối đa 4 sản phẩm hợp lệ mới nhất. Áp dụng điều kiện xuất hiện ở trên trước giới hạn 8/4, bù suất bằng sản phẩm hợp lệ tiếp theo; khối không còn sản phẩm hợp lệ thì ẩn.
- Khối bán chạy trên trang chủ (đã chốt 21/11/2026, cập nhật 22/11/2026 theo UC-09-Q2, UC-09-Q4):
  - Hiển thị 5 sản phẩm (tính theo sản phẩm, cộng mọi biến thể) có tổng số lượng bán lớn nhất trong 7 ngày gần nhất. Tính các đơn kể từ lúc đặt, không chờ giao thành công. Xếp theo tổng số lượng bán, không theo số đơn.
  - "7 ngày gần nhất" là 168 giờ tính lùi từ thời điểm tác vụ tính, theo UTC. Tính đơn ở trạng thái "Chưa xử lý", "Đã xác nhận", "Chờ lấy hàng", "Đang giao", "Giao thành công"; loại đơn "Đã hủy" và "Giao không thành công".
  - Nếu bằng tổng số lượng bán, ưu tiên sản phẩm có đơn đặt gần nhất; nếu vẫn bằng nhau thì sắp xếp theo `product_id` tăng dần.
  - Một tác vụ chạy mỗi 10 phút tính top 15 sản phẩm và ghi vào Redis (chỉ lưu mã sản phẩm và số lượng, TTL 30 phút). Khi hiển thị, hệ thống đọc trạng thái sản phẩm và tập biến thể hợp lệ hiện hành từ DB, bỏ sản phẩm Ngừng bán hoặc không có biến thể ACTIVE có giá > 0 rồi lấy tối đa 5 sản phẩm đầu còn lại trong top 15; không lấy ngoài top 15. Nhờ đó ngừng bán được phản ánh ở request mới mà không chờ tác vụ 10 phút hoặc tăng catalog_version thành công. Tên, ảnh, giá lấy tại lúc hiển thị. Key trống (Redis mất dữ liệu hoặc tác vụ lỗi) thì tính lại từ Database. Việc lọc lúc hiển thị không thay đổi phép tổng hợp, xếp hạng và lịch chạy của reporting.
  - Module `reporting` phụ trách tác vụ tổng hợp top 15, lấy số lượng bán qua service công khai của `ordering` và ghi vào Redis. Khi render trang chủ, `catalog` đọc danh sách này, lọc theo dữ liệu hiện hành của module catalog như trên rồi mới lấy tối đa 5 sản phẩm; khuyến mãi và tồn kho lấy qua service công khai của `promotion` và `inventory`. Nếu Redis trống hoặc mất kết nối, gọi service công khai của `reporting` để tính lại từ Database qua service của `ordering`; không truy cập trực tiếp bảng hoặc repository của module khác.
  - Còn từ 1 đến 4 sản phẩm sau khi lọc thì hiển thị số còn lại; không có sản phẩm nào thì ẩn khối.

### Open Questions

- [X]  Nội dung trang giới thiệu, chính sách, FAQ có chỉnh sửa được trên hệ thống không? → Không, nội dung cố định (đã chốt 15/11/2026).
- [X]  Trang danh mục sắp xếp theo những tiêu chí nào? → Ưu tiên sản phẩm mới nhất; lọc theo giới tính, size, danh mục, bộ sưu tập (đã chốt 15/11/2026).
- [X]  "Các thuộc tính" của sản phẩm gồm những gì? → Giới tính, màu, size; cùng với danh mục và bộ sưu tập (theo ERD).

---

## BR-003: Giỏ hàng, đặt hàng và hóa đơn

### Metadata

- **ID:** BR-003
- **Status:** draft

### Background

Đây là luồng tạo ra doanh thu: khách chọn hàng, đặt và thanh toán; cửa hàng xử lý đơn và ghi nhận hóa đơn khi giao thành công.

### Goal

Khách đặt được đơn với COD hoặc chuyển khoản QR và theo dõi được đơn; Nhân viên xử lý được đơn; đơn giao thành công có hóa đơn.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng giỏ hàng, đặt hàng và hóa đơn = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints

- Theo *Constraints chung*. Tài khoản nhận chuyển khoản lấy từ cấu hình hard-code.
- Khi đặt hàng COD hoặc QR, khách có thể nhập tay tên người nhận, số điện thoại nhận hàng và địa chỉ nhận hàng. Khi khách bấm "Sử dụng thông tin hồ sơ", hệ thống tự điền ba thông tin nhận hàng nếu hồ sơ đã có đủ họ tên, ngày sinh, số điện thoại và địa chỉ hợp lệ. Nếu hồ sơ còn thiếu hoặc có dữ liệu không hợp lệ, hệ thống mở biểu mẫu cập nhật hồ sơ ngay trong checkout theo UC-04. Sau khi lưu hồ sơ hợp lệ, hệ thống tự điền thông tin nhận hàng và đưa khách về biểu mẫu đặt hàng. Khách có thể sửa các giá trị trước khi xác nhận. Đơn lưu thông tin nhận hàng cuối cùng tại thời điểm đặt. (đã chốt 27/11/2026).
- Phí vận chuyển: 1 mức cố định áp cho mọi đơn, không phụ thuộc sản phẩm; nạp từ biến môi trường, mặc định 12.000đ (đã chốt 20/11/2026).
- Đơn chuyển khoản quá 24 giờ kể từ lúc đặt mà chưa thanh toán thì hệ thống tự hủy.
- Đơn chuyển khoản tự chuyển sang "Đã thanh toán" khi hệ thống nhận được giao dịch khớp từ dịch vụ theo dõi biến động số dư (xem BR-006) (đã chốt 20/11/2026).
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Chờ lấy hàng → Đang giao → Giao thành công | Giao không thành công; nhánh kết thúc: Đã hủy (khách hủy, Nhân viên hủy hoặc hệ thống tự hủy) (đã chốt 15/11/2026; bổ sung "Chờ lấy hàng" và Nhân viên hủy, bỏ trạng thái "Bị từ chối" ngày 20/11/2026).
- Không có thao tác "Từ chối đơn" riêng: từ chối và hủy cùng một logic, Nhân viên chỉ có nút "Hủy đơn" (đã chốt 20/11/2026).
- Quyền hủy đơn (đã chốt 20/11/2026):
  - Khách hàng chỉ hủy được đơn "Chưa xử lý". Từ "Đã xác nhận" trở đi khách không hủy được.
  - Hệ thống tự hủy đơn chuyển khoản "Chưa xử lý" quá 24 giờ chưa thanh toán.
  - Nhân viên được hủy đơn ở các trạng thái "Chưa xử lý", "Đã xác nhận", "Chờ lấy hàng". Khi đơn vị vận chuyển đã nhận hàng (từ "Đang giao" trở đi) và ở các trạng thái kết thúc (Giao thành công, Giao không thành công, Đã hủy), Nhân viên không hủy được.
  - Khi Nhân viên bấm "Hủy đơn", hệ thống hiển thị popup bắt buộc nhập lý do hủy; bấm xác nhận mới hủy.
  - Lý do hủy được lưu cùng lịch sử trạng thái đơn `[GD]`, chỉ Nhân viên xem được; khách chỉ thấy đơn ở trạng thái "Đã hủy", không thấy lý do.
- Đơn bị hủy thì hệ thống tự cộng lại số lượng đã trừ vào tồn kho và hoàn lượt voucher (đã chốt 15/11/2026; áp dụng cả khi Nhân viên hủy, chốt 20/11/2026).
- Đơn chuyển khoản đã thanh toán mà bị hủy thì hoàn tiền xử lý ngoài hệ thống (theo Out of Scope).
- Nhân viên bàn giao đơn "Đã xác nhận" cho vận chuyển thì đơn chuyển sang "Chờ lấy hàng" và hiện trên trang giả lập vận chuyển. Khi đơn vị vận chuyển bấm "Đã nhận hàng" trên trang giả lập, đơn chuyển sang "Đang giao" (bổ sung 20/11/2026).
- Hóa đơn tự xuất khi đơn chuyển sang "Giao thành công"; khách và Nhân viên chỉ xem, không sửa hay xuất lại hóa đơn (đã chốt 20/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử thay đổi (theo ERD).

### Open Questions

- [X]  Ở trạng thái "Chưa xử lý", giữ cả "Từ chối" và "Hủy đơn"? → Không; cùng một logic, chỉ giữ nút "Hủy đơn", bỏ trạng thái "Bị từ chối" (đã chốt 20/11/2026).
- [X]  Nhân viên có được hủy đơn không? → Được, qua popup nhập lý do và xác nhận; đơn bị hủy tự cộng lại tồn kho (đã chốt 20/11/2026).
- [X]  Nhân viên hủy "bất cứ lúc nào" gồm những trạng thái nào? → Chỉ các trạng thái chưa kết thúc và trước khi đơn vị vận chuyển nhận hàng: Chưa xử lý, Đã xác nhận, Chờ lấy hàng (đã chốt 20/11/2026).
- [X]  Khách có thấy lý do hủy do Nhân viên nhập không? → Không (đã chốt 20/11/2026).
- [X]  "Đơn chưa xử lý" là trạng thái nào — trước khi Nhân viên xác nhận đơn? → Đúng, xem bộ trạng thái đơn ở Constraints (đã chốt 15/11/2026).

---

## BR-004: Khuyến mãi

### Metadata

- **ID:** BR-004
- **Status:** draft

### Background

Cửa hàng cần công cụ giảm giá để kích cầu. Khách luôn được hưởng mức giảm có lợi nhất mà không phải tự so sánh.

### Goal

Nhân viên tạo được 3 loại khuyến mãi; khi đặt hàng, hệ thống áp khuyến mãi theo sản phẩm cùng với mức giảm có lợi hơn cho khách giữa khuyến mãi theo hóa đơn và voucher.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng khuyến mãi = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints

- Theo *Constraints chung*.
- Mức giảm theo hóa đơn và mức giảm theo voucher bằng nhau thì ưu tiên voucher (đã chốt 15/11/2026).
- Mọi loại khuyến mãi giảm theo phần trăm; không có mức giảm tối đa (đã chốt 15/11/2026, theo ERD).
- Mỗi khuyến mãi có số lượng được áp dụng và số lượng thực tế đã dùng. Khuyến mãi theo sản phẩm không áp dụng giới hạn số lượng; có hiệu lực cho đến khi Nhân viên bấm kết thúc chương trình (đã chốt 15/11/2026).
- Khuyến mãi theo sản phẩm chỉ có tạo rồi kết thúc: không có ngày bắt đầu, ngày kết thúc; có hiệu lực ngay khi tạo và hết hiệu lực khi Nhân viên bấm kết thúc chương trình. Mỗi khuyến mãi theo sản phẩm gắn đúng 1 sản phẩm (đã chốt 20/11/2026).
- Khuyến mãi theo hóa đơn và voucher có thời điểm bắt đầu và thời điểm kết thúc do Nhân viên chọn khi tạo theo lịch `Asia/Ho_Chi_Minh`. Ngày bắt đầu có hiệu lực từ 00:00:00 ngày đó; ngày kết thúc áp dụng đến hết ngày đã chọn — hết hiệu lực tại 00:00:00 của ngày kế tiếp (`Asia/Ho_Chi_Minh`, lưu UTC). Hết hiệu lực khi tới mốc đó, hoặc khi Nhân viên bấm kết thúc trước hạn; kết thúc trước hạn vẫn giữ nguyên thời điểm kết thúc đã chọn (đã chốt 20/11/2026; làm rõ mốc hết ngày 24/11/2026).
- Trạng thái hiển thị của khuyến mãi: Sắp diễn ra (chỉ hóa đơn và voucher, chưa tới thời điểm bắt đầu), Đang hiệu lực, Đã kết thúc (đã chốt 20/11/2026).
- Khuyến mãi đã kết thúc không bật lại được; muốn áp lại thì tạo khuyến mãi mới (đã chốt 20/11/2026).
- Khuyến mãi theo hóa đơn và voucher có giá trị đơn tối thiểu; voucher chỉ giới hạn tổng lượt dùng, không giới hạn số lần mỗi khách (theo ERD).
- Mỗi sản phẩm thuộc tối đa 1 khuyến mãi theo sản phẩm; mỗi đơn áp tối đa 1 khuyến mãi theo hóa đơn hoặc voucher (theo ERD).
- Khuyến mãi đã tạo không được sửa, chỉ có thể ngừng để các đơn sau không được áp. Khi tạo khuyến mãi, hệ thống hiển thị popup để Nhân viên xác nhận (đã chốt 15/11/2026).
- Khuyến mãi không có tên. Danh sách khuyến mãi theo hóa đơn và voucher lọc được theo khoảng thời gian để Nhân viên tra cứu (đã chốt 15/11/2026); khuyến mãi theo sản phẩm không lọc theo khoảng thời gian vì không có ngày bắt đầu / kết thúc (đã chốt 20/11/2026).

### Open Questions

- [X]  Mức giảm tính theo phần trăm, theo số tiền, hay cả hai? Có mức giảm tối đa không? → Theo phần trăm, không có mức tối đa (đã chốt 15/11/2026).
- [X]  Voucher giới hạn lượt dùng thế nào (tổng lượt, lượt mỗi khách)? → Chỉ tổng lượt dùng (đã chốt 15/11/2026).

---

## BR-005: Kho và nhập hàng

### Metadata

- **ID:** BR-005
- **Status:** draft

### Background

Cửa hàng có 1 kho. Tồn kho phải đúng để khách không đặt được hàng đã hết.

### Goal

Nhân viên nhập hàng từ nhà cung cấp; hàng của đơn giao không thành công tự quay lại tồn kho; tồn kho luôn đúng và không bao giờ âm.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng kho = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints

- Theo *Constraints chung*.
- Tồn kho không bao giờ âm.
- Ngưỡng tồn kho thấp lấy từ cấu hình hard-code.
- Khi xác nhận phiếu nhập, giá vốn được tính lại theo phương án bình quân gia quyền (xem Constraints của BR-007).
- Đơn giao không thành công: hệ thống tự cộng lại số lượng vào tồn kho, không cần Nhân viên thao tác; giá vốn không đổi.
- Nhà cung cấp có trạng thái Đang hợp tác / Ngừng hợp tác (đã chốt 15/11/2026).

### Open Questions

- [X]  Có xem được danh sách tồn kho theo biến thể ngoài dashboard không? → Có, Nhân viên quản lý hàng hóa nên xem được tồn kho (đã chốt 15/11/2026).

---

## BR-006: Vận chuyển mô phỏng và thanh toán chuyển khoản tự động

### Metadata

- **ID:** BR-006
- **Status:** draft

### Background

Đồ án không kết nối đơn vị vận chuyển thật, nên dùng trang giả lập để thay đổi trạng thái giao hàng. Với thanh toán chuyển khoản, cửa hàng muốn mọi đơn dùng chung 1 tài khoản ngân hàng và trạng thái thanh toán tự cập nhật, không cần ai bấm xác nhận. Ngân hàng không tự báo cho website, nên cần một dịch vụ bên thứ 3 theo dõi biến động số dư và gửi webhook về website.

### Goal

Trang giả lập vận chuyển tự động cập nhật được trạng thái đơn về website; đơn chuyển khoản tự chuyển sang "Đã thanh toán" khi tài khoản cửa hàng nhận đúng tiền của đơn, không cần thao tác thủ công; demo được luồng này bằng số tiền nhỏ.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng vận chuyển và thanh toán = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)
- `[GD]` Tại buổi demo, đơn chuyển khoản chuyển sang "Đã thanh toán" mà không có ai bấm xác nhận, sau khi chuyển tiền thật (đo bằng thao tác trực tiếp trong buổi demo)

### Constraints

- Theo *Constraints chung*. Thông tin người gửi và tài khoản nhận chuyển khoản lấy từ cấu hình hard-code.

**Vận chuyển mô phỏng**

- Trang giả lập vận chuyển không cần đăng nhập, là 1 trang duy nhất (đã chốt 15/11/2026).
- Trang có 3 nút theo trạng thái đơn (đã chốt 20/11/2026):
  - Đơn "Chờ lấy hàng": nút "Đã nhận hàng" — đơn vị vận chuyển đã lấy được hàng từ cửa hàng → đơn chuyển "Đang giao".
  - Đơn "Đang giao": nút "Đã giao" → "Giao thành công"; nút "Giao không thành công" → "Giao không thành công".

**Thanh toán chuyển khoản tự động** (đã chốt 20/11/2026)

- Mọi đơn chuyển khoản dùng chung 1 tài khoản ngân hàng của cửa hàng. Mỗi đơn hiển thị mã VietQR của tài khoản đó, điền sẵn số tiền (tổng thanh toán) và nội dung chuyển khoản gồm tiền tố `SOBIE` + mã đơn hàng, ví dụ `SOBIE7K3M9Q2X` (đã chốt tiền tố 20/11/2026). Tiền tố phải khai báo trùng với cấu hình nhận diện mã thanh toán trên SePay. Mã đơn hàng gồm 8 ký tự ngẫu nhiên theo bảng chữ Crockford Base32 (0–9 và A–Z bỏ I, L, O, U, tổng 32 ký tự: `0123456789ABCDEFGHJKMNPQRSTVWXYZ`), sinh bằng bộ sinh ngẫu nhiên an toàn (`secrets`); cột mã đơn có ràng buộc UNIQUE, trùng thì sinh lại; tách khỏi khóa chính `order_id` (đã chốt 20/11/2026). Khách vẫn có thể chuyển tay bằng số tài khoản nếu nhập đúng nội dung.
- Dùng dịch vụ SePay theo dõi biến động số dư của tài khoản cửa hàng (đã chốt 20/11/2026); SePay gửi webhook về website mỗi khi tài khoản nhận tiền.
- Webhook phải được xác thực bằng khóa bí mật (API key) nạp từ biến môi trường; sai khóa thì từ chối, không ghi nhận.
- Quy tắc khớp giao dịch với đơn (đã chốt 20/11/2026):
  - Khớp khi nội dung chuyển khoản chứa mã của một đơn chuyển khoản đang "Chưa xử lý", "Chưa thanh toán", còn trong hạn 24 giờ, và số tiền nhận ≥ tổng thanh toán của đơn → đơn chuyển "Đã thanh toán". Chuyển thừa vẫn tính là đã thanh toán; phần thừa xử lý ngoài hệ thống.
  - Không khớp (không có mã đơn, mã đơn không tồn tại, chuyển thiếu, đơn đã hủy hoặc quá hạn): hệ thống không cập nhật trạng thái thanh toán của đơn. Khách chủ động liên hệ cửa hàng để giải quyết khoản tiền đó (ngoài hệ thống).
  - Nếu sau đó khách chuyển khoản lại với thông tin đúng (đúng mã đơn, đủ tiền) khi đơn vẫn còn "Chưa xử lý", "Chưa thanh toán" và trong hạn thì đơn tự chuyển "Đã thanh toán".
  - Mỗi giao dịch được xét độc lập, không cộng dồn các lần chuyển thiếu của cùng một đơn (đã chốt 20/11/2026).
  - Mỗi giao dịch chỉ được xử lý 1 lần, chống trùng theo mã giao dịch của dịch vụ (dịch vụ có thể gửi lại cùng một webhook).
  - `[GD]` Mọi giao dịch nhận được (khớp hoặc không) đều được lưu lại để đối chiếu khi khách liên hệ; không có màn hình riêng cho Nhân viên.
- Ghi nhận giao dịch và cập nhật trạng thái thanh toán chạy trong cùng một database transaction.
- Không còn trang giả lập xác nhận chuyển khoản và không có nút "Xác nhận đã chuyển khoản".

**Kế hoạch demo thanh toán QR** (đã chốt 20/11/2026)

Mục tiêu: demo luồng thật (quét QR → chuyển tiền thật → webhook → đơn tự "Đã thanh toán") mà mỗi lần chỉ chuyển vài nghìn đồng.

- Dữ liệu demo giá thấp, logic không đổi:
  - Seed 1 sản phẩm demo có giá bán 2.000đ cho mọi size.
  - Phí vận chuyển giữ mặc định 12.000đ (biến môi trường).
  - Tổng mỗi đơn demo = 2.000đ + 12.000đ = 14.000đ (chưa tính khuyến mãi); hệ thống chạy đúng logic thật, không có nhánh code riêng cho demo.
- Website chạy local, dùng ngrok để SePay gửi webhook tới.
- Tài khoản chuyển tiền phải khác tài khoản nhận (có thể là tài khoản cá nhân thứ hai). Nếu tài khoản nhận là của chính cửa hàng/nhóm, tiền demo vẫn nằm trong tay nhóm.
- Kịch bản demo: kiểm tra trước buổi demo ít nhất 1 ngày (webhook tới được website, API key đúng); trong buổi demo: đặt đơn chuyển khoản → quét QR bằng app ngân hàng → chờ webhook → mở lại chi tiết đơn thấy "Đã thanh toán" → Nhân viên xác nhận đơn.
- Dự phòng khi dịch vụ bên thứ 3 hoặc mạng lỗi trong buổi demo: một công cụ gửi webhook mẫu đúng định dạng của SePay, có API key, chỉ bật ở môi trường dev/demo `[GD]`.

### Open Questions

- [X]  Mã đơn hàng sinh thế nào? → 8 ký tự ngẫu nhiên theo bảng chữ Crockford Base32 (0–9 và A–Z bỏ I, L, O, U), sinh bằng module `secrets`; cột mã đơn UNIQUE, trùng thì sinh lại (đã chốt 20/11/2026).
- [X]  Tiền tố nội dung chuyển khoản? → `SOBIE` + mã đơn hàng (đã chốt 20/11/2026).
- [X]  Chọn nhà cung cấp dịch vụ theo dõi biến động số dư? → SePay (đã chốt 20/11/2026).
- [X]  Phí vận chuyển? → 1 biến môi trường áp cho mọi đơn, mặc định 12.000đ (đã chốt 20/11/2026).
- [X]  Khách chuyển thiếu nhiều lần? → Không cộng dồn, mỗi giao dịch xét riêng (đã chốt 20/11/2026).
- [X]  Kế hoạch demo? → Tạo 1 sản phẩm demo giá 2.000đ; website local + ngrok (đã chốt 20/11/2026).
- [X]  Giao dịch không khớp xử lý thế nào? → Không cập nhật trạng thái thanh toán; khách chủ động liên hệ cửa hàng; khách chuyển lại đúng thông tin thì đơn tự chuyển "Đã thanh toán" (đã chốt 20/11/2026).
- [X]  Chuyển thừa / thiếu? → Thừa vẫn tính là đã thanh toán; thiếu là không khớp (đã chốt 20/11/2026).
- [X]  Thanh toán chuyển khoản dùng chung 1 mã QR tài khoản ngân hàng và tự đối soát? → Dùng dịch vụ bên thứ 3 theo dõi biến động số dư và gửi webhook về website; bỏ trang giả lập xác nhận chuyển khoản (đã chốt 20/11/2026).
- [X]  Nút "Đã nhận hàng" ứng với trạng thái nào? → Thêm trạng thái "Chờ lấy hàng" giữa "Đã xác nhận" và "Đang giao" (đã chốt 20/11/2026).
- [X]  Đơn "Chờ lấy hàng" có hủy được không? → Khách không hủy được; Nhân viên hủy được (đã chốt 20/11/2026, xem quyền hủy đơn ở BR-003).
- [X]  Hai trang giả lập là ứng dụng tách riêng hay nằm trong cùng website? → Mỗi trang là 1 trang duy nhất, không cần đăng nhập (đã chốt 15/11/2026). → Cập nhật 20/11/2026: chỉ còn trang giả lập vận chuyển.
- [X]  Trang giả lập vận chuyển cập nhật được những trạng thái nào? → Chỉ hiển thị đơn đang giao, với nút "Đã giao" (Giao thành công) và "Giao không thành công". Việc chuyển sang "Đang giao" do Nhân viên bàn giao vận chuyển (đã chốt 15/11/2026). → Cập nhật 20/11/2026: thêm nút "Đã nhận hàng"; Nhân viên bàn giao đưa đơn sang "Chờ lấy hàng", đơn vị vận chuyển bấm "Đã nhận hàng" mới chuyển sang "Đang giao" (xem Constraints).

---

## BR-007: Dashboard báo cáo

### Metadata

- **ID:** BR-007
- **Status:** draft

### Background

Cửa hàng cần theo dõi kết quả kinh doanh và tồn kho để ra quyết định.

### Goal

Xem được các chỉ số kinh doanh chính của cửa hàng trên một dashboard.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng dashboard = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints

- Theo *Constraints chung*.
- Ngưỡng tồn kho thấp lấy từ cấu hình hard-code.
- Giá vốn tính theo phương án bình quân gia quyền (đã chốt 15/11/2026). Mỗi lần xác nhận phiếu nhập:
  `Giá vốn mới = (Giá trị tồn hiện tại + Tiền nhập lô này) / Tồn sau khi nhập`
  Khi tồn hiện tại bằng 0, giá vốn mới bằng giá nhập của lô mới.
- Giá vốn tính riêng cho từng biến thể (màu × size).
- Hàng của đơn giao không thành công quay lại tồn kho không làm thay đổi giá vốn; không tính giá trị hàng hoàn.
- Lợi nhuận gộp = Doanh thu − Giá vốn hàng bán (SL bán × giá vốn).
- Tiền tính bằng số nguyên VND, làm tròn `ROUND_HALF_UP`.
- Dashboard truy vấn trực tiếp Database theo khoảng thời gian Nhân viên chọn, không cache phía server (đã chốt 21/11/2026). Sản phẩm bán chạy trên dashboard khác khối bán chạy ở trang chủ (BR-002): tính theo kỳ báo cáo và chỉ đơn "Giao thành công".

### Open Questions

- [X]  "Hiệu quả khuyến mãi" đo bằng chỉ số nào? → Không làm chỉ số này; chuyển sang Out of Scope (đã chốt 15/11/2026).
- [X]  Vai trò nào được xem dashboard? → Chỉ Nhân viên, vì Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản (đã chốt 15/11/2026).

---

## History

- v1: BRQ-001 — Goal, Success Metrics, In Scope, Out of Scope cho toàn bộ MVP
- v2 (2026-11-15): đổi tên file thành BR-TUAN1.md; tách thành BR-001 → BR-007 theo template ebook; thêm constraint kiến trúc 3 tầng, cache danh sách, cấu hình cửa hàng hard-code
- v3 (2026-11-15): In/Out of Scope để chung ở Tổng quan; hạn chót hết ngày 06/12/2026; đổi "Quản lý" thành "Nhân viên"; đơn chuyển khoản tự hủy sau 24 giờ; khách đã chuyển khoản rồi hủy đơn tự liên hệ cửa hàng; khuyến mãi theo sản phẩm tính cùng mức giảm tốt hơn giữa khuyến mãi hóa đơn và voucher
- v4 (2026-11-15): chốt giá vốn bình quân gia quyền — Giá vốn mới = (Giá trị tồn hiện tại + Tiền nhập lô này) / Tồn sau khi nhập
- v5 (2026-11-15): giá vốn tính theo biến thể; đơn giao không thành công tự cộng lại tồn kho, bỏ thao tác nhận hàng hoàn, không tính giá trị hàng hoàn
- v6 (2026-11-15): chốt đăng ký đủ email và SĐT; Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; bộ trạng thái đơn; hủy/từ chối đơn cộng lại tồn kho và hoàn lượt voucher; hai mức giảm bằng nhau thì ưu tiên voucher; chỉ Nhân viên xem dashboard
- v7 (2026-11-15): làm rõ Admin chỉ gán vai trò (Nhân viên ↔ Admin) cho tài khoản, không tạo vai trò mới
- v8 (2026-11-15): đối chiếu ERD — khuyến mãi giảm theo %, số lượng áp dụng; giá theo size; gallery theo sản phẩm; wishlist vào phạm vi, review để giai đoạn 2; lọc và sắp xếp trang danh mục; trang thông tin cố định; Nhân viên xem tồn kho; bàn giao vận chuyển; trang giả lập không cần đăng nhập; bỏ chỉ số hiệu quả khuyến mãi
- v9 (2026-11-15): theo data model v1 — bảng size chung; khuyến mãi không sửa, chỉ ngừng, tạo có popup xác nhận; nhà cung cấp có trạng thái hợp tác; khuyến mãi không có tên, lọc được theo khoảng thời gian
- v10 (2026-11-20): đổi tên file thành BR-GIAIDOAN1.md; chốt hóa đơn tự xuất khi giao thành công, khách và Nhân viên chỉ xem; trang giả lập vận chuyển thêm nút "Đã nhận hàng" và trạng thái "Chờ lấy hàng" `[GD]`; Admin toàn quyền tạo tài khoản với mọi vai trò; ghi nhận câu hỏi mở về QR dùng chung và tự đối soát
- v11 (2026-11-20): chốt thanh toán chuyển khoản dùng chung 1 tài khoản, tự đối soát qua webhook dịch vụ bên thứ 3; bỏ trang giả lập xác nhận chuyển khoản; đổi tên BR-006; thêm constraint webhook và kế hoạch demo bằng số tiền nhỏ `[GD]`; chốt trạng thái "Chờ lấy hàng"; đơn đã xác nhận không hủy được; tài khoản do Admin tạo không bắt buộc đổi mật khẩu
- v12 (2026-11-20): chốt kế hoạch demo bằng sản phẩm demo 2.000đ, dùng ngrok cho webhook; chốt quy tắc giao dịch không khớp (không cập nhật, khách liên hệ cửa hàng, chuyển lại đúng thì tự cập nhật), chuyển thừa tính đã thanh toán, chuyển thiếu là không khớp; Nhân viên được hủy đơn bất cứ lúc nào qua popup nhập lý do, đơn hủy tự cộng lại tồn kho; khách chỉ hủy được đơn "Chưa xử lý"
- v13 (2026-11-20): chốt SePay; phí vận chuyển là 1 biến môi trường cho mọi đơn, mặc định 12.000đ (đơn demo 14.000đ); Nhân viên chỉ hủy được đơn trước khi đơn vị vận chuyển nhận hàng (Chưa xử lý, Đã xác nhận, Chờ lấy hàng); khách không thấy lý do hủy; chuyển thiếu không cộng dồn
- v14 (2026-11-20): bỏ thao tác "Từ chối đơn" và trạng thái "Bị từ chối", Nhân viên chỉ có nút "Hủy đơn"; tiền tố nội dung chuyển khoản là `SOBIE`; mã đơn hàng sinh ngẫu nhiên không trùng (chờ chốt cách sinh)
- v15 (2026-11-20): chốt mã đơn hàng 8 ký tự ngẫu nhiên Crockford Base32, UNIQUE, sinh lại khi trùng
- v16 (2026-11-20): Admin đổi được vai trò sang mọi vai trò (gồm Khách hàng ↔ Nhân viên/Admin)
- v17 (2026-11-20): theo data model v2 — khuyến mãi theo sản phẩm chỉ có tạo rồi kết thúc, gắn đúng 1 sản phẩm; khuyến mãi theo hóa đơn và voucher có thời điểm bắt đầu / kết thúc, kết thúc sớm giữ nguyên thời điểm kết thúc; trạng thái hiển thị Sắp diễn ra / Đang hiệu lực / Đã kết thúc; khuyến mãi đã kết thúc không bật lại; BR-001: Admin được tự đổi vai trò, luôn còn ít nhất 1 Admin đang hoạt động; khuyến mãi theo sản phẩm không lọc theo khoảng thời gian
- v18 (2026-11-20): BR-001 — chỉ đổi vai trò giữa Nhân viên và Admin (thay v16: không còn đổi Khách hàng ↔ Nhân viên/Admin); Admin được tự khóa chính mình khi còn Admin khác đang hoạt động
- v19 (2026-11-21): BR-001 — gộp thông tin cá nhân vào tài khoản, bỏ hồ sơ riêng theo vai trò; mã tài khoản KH- / NV- / AD- với bộ đếm riêng từng loại, đổi vai trò Nhân viên ↔ Admin thì cấp mã mới
- v20 (2026-11-21): chốt chiến lược cache (HTTP `ETag` cho mọi GET, `max-age=60` cho dữ liệu công khai, `private, no-cache` cho đơn hàng; Redis cho danh mục, trang chủ, khuyến mãi đang hiệu lực, khối bán chạy; dashboard không cache); chốt xác thực bằng access token 15 phút + refresh token 14 ngày lưu ở Redis, `account_token_version`, rate limit đăng nhập và làm mới token; quên mật khẩu chuyển sang giai đoạn 2 (giai đoạn 1 có nút nhưng không có hành động); storefront và portal quản trị đăng nhập riêng; BR-002 thêm khối bán chạy trên trang chủ
- v21 (2026-11-21): website là SSR nên đổi xác thực sang phiên phía server: bảng `identity.session`, cookie `HttpOnly` + `Secure` + `SameSite=Lax`, kiểm tra `Origin` ở mọi request ghi; hạn phiên Khách hàng 30 phút, Nhân viên / Admin 1 giờ; bỏ access token JWT, refresh token Redis, `account_token_version` và rate limit làm mới token
- v22 (2026-11-21): constraint cache cập nhật cho SSR — không phải danh sách nào cũng cache: chỉ dữ liệu công khai cache ở Redis (cache dữ liệu, không cache HTML); kết quả tìm kiếm, mọi trang cần đăng nhập (kể cả portal quản trị) và dashboard không cache; không trang HTML nào `public`: trang công khai `private, no-cache` + `ETag` `[GD]`, trang cần đăng nhập `no-store`, `Vary: HX-Request`, file tĩnh cache 1 năm; hạn phiên tính từ lần thao tác cuối (đã chốt)
- v23 (2026-11-21): bỏ `ETag` cho trang HTML công khai; không còn response nào dùng `ETag`
- v24 (2026-11-22): đồng bộ các quyết định UC-09 đã được developer duyệt: khối Hàng mới tối đa 8 sản phẩm, mỗi bộ sưu tập tối đa 4 sản phẩm; bán chạy tính 168 giờ UTC, loại đơn hủy/giao không thành công, tiêu chí phụ khi bằng số lượng; hiển thị số còn lại hoặc ẩn khối rỗng; ranh giới reporting tổng hợp/catalog hiển thị và fallback khi Redis trống/lỗi.
- v25 (2026-11-22): theo phê duyệt của developer tại Codex, áp dụng quyết định UC-17-Q6 cho UC-16 và ghi ngoại lệ cache chung trong phạm vi hai UC: DB commit thành công nhưng Redis lỗi thì ghi log, vẫn báo thành công, không rollback DB; cache cũ hết TTL dự phòng 5 phút hoặc được làm mới ở lần cập nhật catalog thành công tiếp theo.
- v26 (2026-11-23): developer duyệt đồng bộ UC-15-Q7 tại Codex: mở rộng ngoại lệ Redis sau commit cho tạo/xóa/đổi trạng thái biến thể; kiểm tra trạng thái/tồn kho từ DB qua Service khi thêm giỏ và trong transaction tạo đơn COD/QR để chặn thao tác mua từ cache cũ; giữ nguyên các giả định khác.
- v27 (2026-11-23): theo yêu cầu xử lý rà soát vòng 3 tại Codex, bổ sung kiểm tra sản phẩm cha ACTIVE cùng biến thể ACTIVE cho UC-18/19/20 để chặn mua từ trang cũ khi sản phẩm đã Ngừng bán; không thay chính sách Redis hay các giả định khác.
- v28 (2026-11-23): theo phê duyệt đồng bộ 5 file tại Codex, ghi UC-10-Q9/Q10/Q11 về tập biến thể tính giá/tồn kho, ẩn sản phẩm không hợp lệ trước giới hạn/phân trang và khóa phụ product_id ASC; giữ nguyên thống kê reporting. Mở rộng chính sách Redis sau commit cho UC-14-Q10, giới hạn độ trễ ở dữ liệu thực sự cache; giữ câu hỏi URL chi tiết tại UC-12-Q9b.
- v29 (2026-11-23): theo yêu cầu tại Codex, đồng bộ UC-02/38 về return_url nội bộ an toàn từ checkout/trang chi tiết và không tự thay đổi wishlist; ghi quyết định UC-12-Q9b giữ trang HTTP 200 nhưng khóa mua khi không còn biến thể hợp lệ, cùng contract 404 HTMX UC-13-Q5. Không thay các giả định ngoài phạm vi.
- v30 (2026-11-23): theo quyết định developer tại Codex cho review PR #7, ghi quy tắc sản phẩm chỉ sửa Mô tả sau phiếu CONFIRMED; đồng bộ khóa giá/trạng thái/biến thể/taxonomy và ưu tiên hơn quyền sửa cũ, giữ nguyên nghiệp vụ tồn kho ngoài Catalog.
- v31 (2026-11-23): xử lý hai phát hiện rà soát Catalog: đồng bộ thứ tự taxonomy trước sản phẩm giữa UC-14/15/17 và khóa phiếu/sản phẩm/biến thể tại UC-34, tránh khóa phiếu ngược khi Catalog kiểm tra CONFIRMED; giữ nguyên quy tắc chỉ sửa Mô tả sau nhập.
- v32 (2026-11-23): đồng bộ BR-001 với luồng tự đăng ký bằng email OTP hoặc Google, bổ sung hồ sơ qua UC-04 và đăng nhập Google theo UC-02.
- v33 (2026-11-23): đồng bộ BR-001 với quyết định của UC-02 về thông báo đăng nhập sai, nút quên mật khẩu, cookie hai cổng và giới hạn đăng nhập bằng mật khẩu.
- v34 (2026-11-23): chốt xác minh OTP qua email Sobie khi liên kết Google lần đầu với tài khoản hiện có.
- v35 (2026-11-23): chốt nút "Sử dụng thông tin hồ sơ" và quy tắc điền thông tin nhận hàng ở BR-003.
- v36 (2026-11-23): đồng bộ BR-001 với quyền cập nhật hồ sơ Khách hàng và quy tắc tự đổi mật khẩu của UC-05.
- v37 (2026-11-23): đồng bộ BR-001 với các quyết định về tạo tài khoản qua UC-06.
- v38 (2026-11-23): bổ sung quyền Nhân viên xem thông tin và khóa tài khoản Khách hàng qua UC-07 và UC-08.
- v39 (2026-11-23): chốt các giả định của UC-08 và xác nhận hệ thống luôn có ít nhất một Admin Hoạt động, kể cả khi khóa và đổi vai trò đồng thời.
- v40 (2026-11-26): hợp nhất đăng ký và đăng nhập Google, cấp phiên ngay khi tạo tài khoản, liên kết theo email đã xác minh không qua OTP, và chuyển email hồ sơ storefront sang chỉ xem.
- v41 (2026-11-27): đồng bộ dữ liệu xác thực khi tạo tài khoản và luồng bổ sung hồ sơ để tự điền tại checkout COD/QR.
