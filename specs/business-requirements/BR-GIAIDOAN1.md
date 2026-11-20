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

- Tài khoản và phân quyền: đăng ký bắt buộc nhập đủ email và số điện thoại; đăng nhập bằng email hoặc số điện thoại đều được. Có 3 vai trò cố định: Khách hàng, Nhân viên, Admin. Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; Nhân viên thực hiện mọi thao tác vận hành cửa hàng
- Hồ sơ khách hàng: sửa thông tin cá nhân, đổi mật khẩu
- Trang bán hàng: trang chủ, trang danh mục có phân trang, sắp xếp (mặc định sản phẩm mới nhất) và lọc theo giới tính, size, danh mục, bộ sưu tập, tìm kiếm theo tên hoặc từ khóa, chi tiết sản phẩm (chọn màu và size, ảnh, bảng size, tình trạng còn/hết hàng), các trang giới thiệu, chính sách, FAQ. Khách hàng thả tim để lưu sản phẩm vào danh sách yêu thích (wishlist)
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

### Out of Scope

- Mega menu, bộ lọc nâng cao, thêm nhanh vào giỏ từ thẻ sản phẩm
- Trang Outlet, sổ nhiều địa chỉ, quên mật khẩu qua email
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
- **Technical — Cache danh sách:** mọi danh sách lấy từ Database phải có chiến lược cache. Chiến lược cụ thể (nơi lưu cache, thời gian sống, cách làm mới khi dữ liệu thay đổi) chốt ở bước thiết kế — xem câu hỏi mở chung.
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
- [ ]  Constraint cache: "danh sách" gồm những danh sách nào — chỉ danh sách phía khách (danh mục, tìm kiếm) hay cả danh sách trong trang quản trị (đơn hàng, tài khoản, phiếu nhập…)? Dữ liệu được phép cũ tối đa bao lâu?

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
- Tài khoản đăng nhập (email, số điện thoại, mật khẩu, vai trò, trạng thái) tách khỏi hồ sơ cá nhân. Mỗi vai trò có hồ sơ riêng (Khách hàng / Nhân viên / Admin) gồm họ tên, ngày sinh, địa chỉ, có khóa ngoại tới tài khoản. Không có username riêng; email và số điện thoại là duy nhất (đã chốt 15/11/2026).
- Admin có toàn quyền tạo tài khoản với bất kỳ vai trò nào trong 3 vai trò cố định (Khách hàng, Nhân viên, Admin), không chỉ tài khoản nội bộ (đã chốt 20/11/2026).
- `[GD]` Tài khoản do Admin tạo tuân theo cùng ràng buộc như khi khách tự đăng ký: bắt buộc đủ email và số điện thoại, không trùng với tài khoản khác; Admin đặt mật khẩu ban đầu.
- Tài khoản do Admin tạo dùng được ngay, không bắt buộc đổi mật khẩu ở lần đăng nhập đầu (đã chốt 20/11/2026).
- Admin đổi được vai trò của tài khoản sang bất kỳ vai trò nào trong 3 vai trò cố định, kể cả giữa Khách hàng và Nhân viên/Admin. Vai trò mới có hiệu lực ngay, tài khoản đang đăng nhập bị đăng xuất; thông tin cá nhân và thông tin đăng nhập giữ nguyên (đã chốt 20/11/2026).
- `[GD]` Đổi vai trò giữ nguyên lịch sử đơn hàng, hóa đơn và lịch sử thao tác của tài khoản; Admin không tự đổi vai trò của mình; không cho đổi khiến hệ thống không còn Admin nào đang hoạt động.

### Open Questions

- [X]  Admin đổi vai trò được giữa những vai trò nào? → Mọi vai trò: Khách hàng, Nhân viên, Admin, kể cả giữa Khách hàng và vai trò nội bộ; không dựa vào data model hiện tại (đã chốt 20/11/2026).
- [X]  Tài khoản Khách hàng do Admin tạo có bắt buộc đổi mật khẩu ở lần đăng nhập đầu không? → Không, dùng được ngay như tài khoản khách tự đăng ký (đã chốt 20/11/2026).
- [X]  Admin được tạo tài khoản với vai trò nào? → Mọi vai trò: Khách hàng, Nhân viên, Admin (đã chốt 20/11/2026).
- [X]  Khi đăng ký, khách phải nhập cả email và số điện thoại, hay chỉ cần một trong hai? → Đăng ký bắt buộc nhập đủ cả hai; đăng nhập bằng một trong hai (đã chốt 15/11/2026).
- [X]  Nhân viên và Admin khác nhau về quyền thế nào? → Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; Nhân viên vận hành cửa hàng (đã chốt 15/11/2026).

---

## BR-002: Trang bán hàng và quản lý sản phẩm

### Metadata

- **ID:** BR-002
- **Status:** draft

### Background

Khách cần xem, tìm và chọn đúng sản phẩm (màu, size) trước khi mua; cửa hàng cần tự quản lý danh mục sản phẩm và giá bán.

### Goal

Khách tìm và xem được sản phẩm cùng tình trạng còn/hết hàng theo từng màu và size; Nhân viên quản lý được sản phẩm, biến thể, giá và phân loại.

### Success Metrics

- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng trang bán hàng và sản phẩm = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints

- Theo *Constraints chung*. Danh sách sản phẩm ở trang danh mục và kết quả tìm kiếm thuộc phạm vi constraint cache.
- Trang giới thiệu, chính sách, FAQ có nội dung cố định, không chỉnh sửa trên hệ thống; chỉ thông tin sản phẩm là sửa được (đã chốt 15/11/2026).
- Lọc sản phẩm theo giới tính, size, danh mục, bộ sưu tập (đã chốt 15/11/2026).
- Sắp xếp ưu tiên sản phẩm mới nhất (đã chốt 15/11/2026).
- Giá bán chỉ thay đổi theo size; cùng size khác màu thì cùng giá (đã chốt 15/11/2026). ERD hiện để giá ở biến thể (`variant_sell_price`), cần điều chỉnh hoặc đảm bảo đồng bộ.
- Ảnh sản phẩm (gallery) gắn theo sản phẩm, không theo màu (đã chốt 15/11/2026).
- Bảng size dùng chung cho cả cửa hàng, nội dung cố định (đã chốt 15/11/2026).
- Wishlist: Khách hàng thả tim để lưu sản phẩm vào danh sách yêu thích; mỗi sản phẩm chỉ có 1 lần trong danh sách của một tài khoản (đã chốt 15/11/2026, theo ERD).

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
- Khuyến mãi theo hóa đơn và voucher có giá trị đơn tối thiểu; voucher chỉ giới hạn tổng lượt dùng, không giới hạn số lần mỗi khách (theo ERD).
- Mỗi sản phẩm thuộc tối đa 1 khuyến mãi theo sản phẩm; mỗi đơn áp tối đa 1 khuyến mãi theo hóa đơn hoặc voucher (theo ERD).
- Khuyến mãi đã tạo không được sửa, chỉ có thể ngừng để các đơn sau không được áp. Khi tạo khuyến mãi, hệ thống hiển thị popup để Nhân viên xác nhận (đã chốt 15/11/2026).
- Khuyến mãi không có tên. Danh sách khuyến mãi (cả 3 loại) lọc được theo khoảng thời gian để Nhân viên tra cứu (đã chốt 15/11/2026).

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
