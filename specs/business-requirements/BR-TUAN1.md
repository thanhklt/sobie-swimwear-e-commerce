# BR-TUAN1: Website bán đồ bơi — Đồ án Công nghệ phần mềm

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
- Giỏ hàng và đặt hàng: khách chưa đăng nhập vẫn dùng được giỏ hàng, nhưng phải đăng nhập mới đặt hàng được. Thanh toán bằng COD hoặc chuyển khoản qua mã QR
- Khuyến mãi 3 loại: theo sản phẩm, theo giá trị hóa đơn, voucher. Khuyến mãi theo sản phẩm giảm trực tiếp trên giá sản phẩm (hiển thị trên trang chi tiết sản phẩm). Hệ thống tự chọn mức giảm có lợi hơn cho khách giữa khuyến mãi theo hóa đơn và voucher. Khuyến mãi theo sản phẩm được tính cùng với mức giảm được chọn đó. Mọi loại khuyến mãi giảm theo phần trăm, không có mức giảm tối đa
- Đơn hàng: khách theo dõi và hủy đơn khi đơn chưa xử lý. Nhân viên xác nhận hoặc từ chối đơn, rồi bàn giao đơn đã xác nhận cho vận chuyển. Đơn chuyển khoản quá 24 giờ kể từ lúc đặt mà chưa thanh toán thì hệ thống tự hủy
- Vận chuyển và thanh toán mô phỏng: một trang giả lập đơn vị vận chuyển và một trang giả lập xác nhận chuyển khoản, đều không cần đăng nhập và là 1 trang duy nhất. Trang vận chuyển hiển thị danh sách đơn đang giao với nút "Đã giao" / "Giao không thành công"; trang chuyển khoản hiển thị danh sách đơn QR chưa thanh toán với nút "Xác nhận đã chuyển khoản". Hai trang này tự động cập nhật trạng thái đơn về website
- Hóa đơn tự xuất khi giao thành công; khách và nhân viên chỉ xem (cần chốt)
- Kho: quản lý nhà cung cấp, lập và xác nhận phiếu nhập. Đơn giao không thành công thì hệ thống tự cộng lại hàng vào tồn kho (không có thao tác nhận hàng hoàn). Nhân viên xem được tồn kho. Tồn kho không bao giờ âm
- Cấu hình cửa hàng (hard-code, không chỉnh sửa trên hệ thống): phí vận chuyển cố định, hotline, link Zalo, thông tin người gửi, tài khoản nhận chuyển khoản, ngưỡng tồn kho thấp
- Dashboard: doanh thu, lợi nhuận gộp, số đơn theo trạng thái, sản phẩm bán chạy, tồn kho thấp, tiền nhập hàng theo nhà cung cấp
- Admin quản lý tài khoản: tạo tài khoản nội bộ, sửa, khóa và mở khóa

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
- Hóa đơn điện tử VAT, kết nối ngân hàng và đơn vị vận chuyển thật
- Đa ngôn ngữ
- Chức năng chỉnh sửa cấu hình cửa hàng
- Thao tác nhận hàng hoàn thủ công, tính giá trị hàng hoàn
- Chỉ số hiệu quả khuyến mãi trên dashboard

### Constraints chung
Áp dụng cho mọi BR bên dưới.
- **Technical — Kiến trúc Backend:** thiết kế theo kiến trúc 3 tầng (3-layer architecture): `Route` → `Service` → `Repository` → `Database`. Không gọi tắt tầng (Route không gọi trực tiếp Repository hoặc Database).
- **Technical — Cache danh sách:** mọi danh sách lấy từ Database phải có chiến lược cache. Chiến lược cụ thể (nơi lưu cache, thời gian sống, cách làm mới khi dữ liệu thay đổi) chốt ở bước thiết kế — xem câu hỏi mở chung.
- **Technical — Cấu hình cửa hàng:** hard-code, không có chức năng chỉnh sửa và không có BR riêng. Gồm: phí vận chuyển cố định, hotline, link Zalo, thông tin người gửi, tài khoản nhận chuyển khoản, ngưỡng tồn kho thấp.
- **Timeline:** demo hằng tuần thứ Hai 16/11, 23/11, 30/11/2026; hoàn thành và nghiệm thu hết ngày 06/12/2026; 07/12/2026 báo cáo kết quả.

### Danh mục BR

| ID | Tên | Status |
|---|---|---|
| [BR-001](#br-001-tài-khoản-và-phân-quyền) | Tài khoản và phân quyền | draft |
| [BR-002](#br-002-trang-bán-hàng-và-quản-lý-sản-phẩm) | Trang bán hàng và quản lý sản phẩm | draft |
| [BR-003](#br-003-giỏ-hàng-đặt-hàng-và-hóa-đơn) | Giỏ hàng, đặt hàng và hóa đơn | draft |
| [BR-004](#br-004-khuyến-mãi) | Khuyến mãi | draft |
| [BR-005](#br-005-kho-và-nhập-hàng) | Kho và nhập hàng | draft |
| [BR-006](#br-006-vận-chuyển-và-thanh-toán-mô-phỏng) | Vận chuyển và thanh toán mô phỏng | draft |
| [BR-007](#br-007-dashboard-báo-cáo) | Dashboard báo cáo | draft |

### Open Questions chung
- [ ] `[GD]` Cách gom các mục In Scope thành 7 BR như bảng trên có đúng ý không?
- [ ] `[GD]` Success Metric của từng BR đang suy ra từ metric tổng (100% acceptance test của nhóm tính năng đó). Có cần metric riêng cho từng BR không?
- [ ] Constraint cache: "danh sách" gồm những danh sách nào — chỉ danh sách phía khách (danh mục, tìm kiếm) hay cả danh sách trong trang quản trị (đơn hàng, tài khoản, phiếu nhập…)? Dữ liệu được phép cũ tối đa bao lâu?

---

## BR-001: Tài khoản và phân quyền

### Metadata
- **ID:** BR-001
- **Status:** draft

### Background
Khách phải có tài khoản mới đặt hàng được, và cửa hàng cần tách người mua với người vận hành. Hệ thống dùng 3 vai trò cố định, không cấu hình quyền.

### Goal
Khách hàng tự đăng ký, đăng nhập và quản lý hồ sơ của mình; Admin quản lý được tài khoản nội bộ với 3 vai trò cố định.

### Success Metrics
- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng tài khoản = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints
- Theo *Constraints chung*.
- Tài khoản đăng nhập (email, số điện thoại, mật khẩu, vai trò, trạng thái) tách khỏi hồ sơ cá nhân. Mỗi vai trò có hồ sơ riêng (Khách hàng / Nhân viên / Admin) gồm họ tên, ngày sinh, địa chỉ, có khóa ngoại tới tài khoản. Không có username riêng; email và số điện thoại là duy nhất (đã chốt 15/11/2026).

### Open Questions
- [x] Khi đăng ký, khách phải nhập cả email và số điện thoại, hay chỉ cần một trong hai? → Đăng ký bắt buộc nhập đủ cả hai; đăng nhập bằng một trong hai (đã chốt 15/11/2026).
- [x] Nhân viên và Admin khác nhau về quyền thế nào? → Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản; Nhân viên vận hành cửa hàng (đã chốt 15/11/2026).

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
- Wishlist: Khách hàng thả tim để lưu sản phẩm vào danh sách yêu thích; mỗi sản phẩm chỉ có 1 lần trong danh sách của một tài khoản (đã chốt 15/11/2026, theo ERD).

### Open Questions
- [x] Nội dung trang giới thiệu, chính sách, FAQ có chỉnh sửa được trên hệ thống không? → Không, nội dung cố định (đã chốt 15/11/2026).
- [x] Trang danh mục sắp xếp theo những tiêu chí nào? → Ưu tiên sản phẩm mới nhất; lọc theo giới tính, size, danh mục, bộ sưu tập (đã chốt 15/11/2026).
- [x] "Các thuộc tính" của sản phẩm gồm những gì? → Giới tính, màu, size; cùng với danh mục và bộ sưu tập (theo ERD).

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
- Theo *Constraints chung*. Phí vận chuyển cố định và tài khoản nhận chuyển khoản lấy từ cấu hình hard-code.
- Đơn chuyển khoản quá 24 giờ kể từ lúc đặt mà chưa thanh toán thì hệ thống tự hủy.
- Trạng thái đơn: Chưa xử lý → Đã xác nhận → Đang giao → Giao thành công | Giao không thành công; nhánh kết thúc: Đã hủy (khách hủy hoặc hệ thống tự hủy), Bị từ chối (Nhân viên từ chối) (đã chốt 15/11/2026).
- Đơn bị hủy hoặc bị từ chối thì cộng lại tồn kho và hoàn lượt voucher (đã chốt 15/11/2026).
- Nhân viên bàn giao đơn "Đã xác nhận" cho vận chuyển thì đơn chuyển sang "Đang giao" và hiện trên trang giả lập vận chuyển (đã chốt 15/11/2026).
- Mỗi lần đơn đổi trạng thái, hệ thống lưu lịch sử thay đổi (theo ERD).

### Open Questions
- [x] "Đơn chưa xử lý" là trạng thái nào — trước khi Nhân viên xác nhận đơn? → Đúng, xem bộ trạng thái đơn ở Constraints (đã chốt 15/11/2026).

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

### Open Questions
- [x] Mức giảm tính theo phần trăm, theo số tiền, hay cả hai? Có mức giảm tối đa không? → Theo phần trăm, không có mức tối đa (đã chốt 15/11/2026).
- [x] Voucher giới hạn lượt dùng thế nào (tổng lượt, lượt mỗi khách)? → Chỉ tổng lượt dùng (đã chốt 15/11/2026).

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

### Open Questions
- [x] Có xem được danh sách tồn kho theo biến thể ngoài dashboard không? → Có, Nhân viên quản lý hàng hóa nên xem được tồn kho (đã chốt 15/11/2026).

---

## BR-006: Vận chuyển và thanh toán mô phỏng

### Metadata
- **ID:** BR-006
- **Status:** draft

### Background
Đồ án không kết nối ngân hàng và đơn vị vận chuyển thật, nhưng vẫn cần trạng thái giao hàng và thanh toán thay đổi để demo trọn vòng đời đơn.

### Goal
Hai trang giả lập (đơn vị vận chuyển, xác nhận chuyển khoản) tự động cập nhật được trạng thái đơn về website.

### Success Metrics
- `[GD]` Must_acceptance_test_pass_rate của nhóm tính năng mô phỏng = 100% tại buổi demo cuối 06/12/2026 (đo qua bảng kết quả kiểm thử nghiệm thu)

### Constraints
- Theo *Constraints chung*. Thông tin người gửi và tài khoản nhận chuyển khoản lấy từ cấu hình hard-code.
- Hai trang giả lập không cần đăng nhập, mỗi trang là 1 trang duy nhất (đã chốt 15/11/2026).

### Open Questions
- [x] Hai trang giả lập là ứng dụng tách riêng hay nằm trong cùng website? → Mỗi trang là 1 trang duy nhất, không cần đăng nhập (đã chốt 15/11/2026).
- [x] Trang giả lập vận chuyển cập nhật được những trạng thái nào? → Chỉ hiển thị đơn đang giao, với nút "Đã giao" (Giao thành công) và "Giao không thành công". Việc chuyển sang "Đang giao" do Nhân viên bàn giao vận chuyển (đã chốt 15/11/2026).

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
- [x] "Hiệu quả khuyến mãi" đo bằng chỉ số nào? → Không làm chỉ số này; chuyển sang Out of Scope (đã chốt 15/11/2026).
- [x] Vai trò nào được xem dashboard? → Chỉ Nhân viên, vì Admin chỉ quản lý tài khoản và gán vai trò cho tài khoản (đã chốt 15/11/2026).

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
