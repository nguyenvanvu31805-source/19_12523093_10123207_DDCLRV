param([string]$OutputPath = "docs/Loi_thoai_thuyet_trinh_Wine_Quality.docx")

$ErrorActionPreference = "Stop"
$workspace = [System.IO.Path]::GetFullPath((Get-Location).Path)
$output = [System.IO.Path]::GetFullPath((Join-Path $workspace $OutputPath))
if (-not $output.StartsWith($workspace, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Output path must stay inside the workspace."
}
if (Test-Path -LiteralPath $output) { Remove-Item -LiteralPath $output -Force }
New-Item -ItemType Directory -Path (Split-Path -Parent $output) -Force | Out-Null

$wdAlignParagraphLeft = 0
$wdAlignParagraphCenter = 1
$wdAlignParagraphJustify = 3
$wdPageBreak = 7
$wdFieldPage = 33
$wdHeaderFooterPrimary = 1
$wdFormatDocumentDefault = 16
$accent = 0x473B8C
$ink = 0x2A2522
$muted = 0x666B71

$slides = @(
    [pscustomobject]@{
        Number=1; Title="Trang bìa"; Time="30–40 giây";
        Objective="Chào hội đồng, giới thiệu đề tài và định hướng chung của bài trình bày.";
        Speech=@(
            "Kính thưa giảng viên và các bạn, nhóm em xin trình bày đề tài Xây dựng hệ thống dự đoán chất lượng rượu vang. Đây là một bài toán ứng dụng học máy vào lĩnh vực kiểm soát chất lượng thực phẩm, cụ thể là ước lượng điểm chất lượng của rượu vang đỏ dựa trên dữ liệu đo lường hóa lý.",
            "Trong đồ án này, nhóm không chỉ dừng ở việc huấn luyện một mô hình dự đoán. Quy trình được thực hiện theo hướng tương đối đầy đủ, bao gồm phân tích dữ liệu, tiền xử lý, so sánh nhiều thuật toán hồi quy, tinh chỉnh siêu tham số, lựa chọn mô hình và tích hợp mô hình vào một hệ thống có giao diện, backend và thành phần dự đoán độc lập.",
            "Phần trình bày gồm năm nội dung chính: bối cảnh bài toán, dữ liệu và phân tích khám phá; quy trình tiền xử lý; nguyên lý các mô hình; kết quả thực nghiệm và mô hình được lựa chọn; cuối cùng là kiến trúc hệ thống, kết luận và hướng phát triển."
        );
        Transition="Trước hết, nhóm xin trình bày lý do vì sao bài toán dự đoán chất lượng rượu vang có ý nghĩa trong thực tế."
    },
    [pscustomobject]@{
        Number=2; Title="Vì sao cần dự đoán chất lượng rượu vang?"; Time="Khoảng 1 phút";
        Objective="Nêu bối cảnh, mục tiêu, cách tiếp cận và phạm vi nghiên cứu.";
        Speech=@(
            "Trong sản xuất rượu vang, chất lượng thường được xác định thông qua đánh giá cảm quan của các chuyên gia. Phương pháp này có giá trị chuyên môn cao, nhưng cần nhiều thời gian, chi phí tổ chức và có thể chịu ảnh hưởng bởi kinh nghiệm, trạng thái cảm quan hoặc sự khác biệt giữa những người chấm. Vì vậy, một công cụ dự đoán dựa trên dữ liệu có thể hỗ trợ sàng lọc ban đầu và giúp quá trình đánh giá nhất quán hơn.",
            "Mục tiêu của đề tài là khảo sát khả năng khai thác các phép đo hóa lý để ước lượng điểm quality. Nhóm tiếp cận bài toán theo hướng hồi quy: trước tiên phân tích dữ liệu để nhận diện phân bố và các mối liên hệ đáng chú ý; sau đó huấn luyện bốn thuật toán, thực hiện Cross Validation và tinh chỉnh; cuối cùng triển khai mô hình được lựa chọn thành một dịch vụ dự đoán.",
            "Phạm vi của nghiên cứu chỉ bao gồm rượu vang đỏ Vinho Verde. Kết quả của mô hình nên được hiểu là thông tin hỗ trợ ra quyết định, không phải công cụ thay thế hoàn toàn hội đồng cảm quan. Cách xác định phạm vi như vậy giúp tránh diễn giải quá mức khả năng của mô hình."
        );
        Transition="Sau khi xác định bối cảnh và phạm vi, phần tiếp theo trình bày nguồn gốc cũng như đặc điểm của bộ dữ liệu được sử dụng."
    },
    [pscustomobject]@{
        Number=3; Title="Dataset: nguồn gốc và ý nghĩa"; Time="Khoảng 1 phút 10 giây";
        Objective="Giới thiệu nguồn UCI, cấu trúc, target và những đặc điểm quan trọng của dữ liệu.";
        Speech=@(
            "Bộ dữ liệu được sử dụng là Red Wine Quality, thuộc Wine Quality Dataset trên UCI Machine Learning Repository. Dữ liệu được công bố trong nghiên cứu của Cortez và cộng sự năm 2009, với DOI 10.24432/C56S3T. Các mẫu rượu thuộc dòng Vinho Verde của Bồ Đào Nha. Đây là nguồn dữ liệu công khai và được sử dụng khá phổ biến trong các nghiên cứu học máy về chất lượng rượu.",
            "Dữ liệu ban đầu có 1.599 mẫu và 12 cột. Trong đó, 11 cột là các chỉ tiêu hóa lý được đo trong phòng thí nghiệm, chẳng hạn độ axit, đường dư, chlorides, sulfur dioxide, density, pH, sulphates và alcohol. Cột còn lại là quality, thể hiện điểm đánh giá cảm quan từ 3 đến 8.",
            "Dữ liệu gốc không có giá trị thiếu. Tuy nhiên, nhóm phát hiện 240 dòng trùng lặp; sau khi loại bỏ, tập dữ liệu còn 1.359 mẫu. Một điểm cần lưu ý là quality được hình thành từ đánh giá cảm quan, nên target có thể chứa yếu tố chủ quan hoặc nhiễu nhãn. Hai mẫu có thông số hóa lý gần nhau vẫn có khả năng nhận điểm khác nhau. Đặc điểm này đặt ra giới hạn tự nhiên cho mức độ chính xác có thể đạt được."
        );
        Transition="Từ dữ liệu này, nhóm tiến hành phân tích khám phá. Biểu đồ đầu tiên xem xét phân bố của biến mục tiêu quality."
    },
    [pscustomobject]@{
        Number=4; Title="EDA 1 — Phân bố điểm chất lượng"; Time="50–60 giây";
        Objective="Giải thích tình trạng mất cân bằng của target và hệ quả đối với đánh giá mô hình.";
        Speech=@(
            "Biểu đồ này là biểu đồ đếm số lượng mẫu tại từng mức quality trên dữ liệu ban đầu. Trục ngang là điểm chất lượng từ 3 đến 8, còn trục dọc là số lượng mẫu. Có thể thấy dữ liệu tập trung rất mạnh ở hai mức 5 và 6. Cụ thể, điểm 5 có 681 mẫu và điểm 6 có 638 mẫu. Trong khi đó, điểm 3 chỉ có 10 mẫu và điểm 8 có 18 mẫu; các mức 4 và 7 cũng ít hơn đáng kể.",
            "Như vậy, phân bố target không cân bằng và nghiêng về nhóm chất lượng trung bình. Điều này có hai hệ quả. Thứ nhất, mô hình sẽ học tốt hơn ở vùng điểm 5–6 vì được quan sát nhiều mẫu hơn. Thứ hai, các metric tổng hợp có thể trông khá tốt dù mô hình dự đoán chưa tốt ở các mức hiếm như 3 hoặc 8.",
            "Do đây là bài toán hồi quy, nhóm không biến quality thành các lớp để cân bằng cưỡng bức. Thay vào đó, nhóm giữ nguyên bản chất số của target, sử dụng nhiều metric đồng thời và thận trọng khi diễn giải kết quả đối với những vùng có ít dữ liệu."
        );
        Transition="Sau target, nhóm xem xét alcohol, một đặc trưng hóa lý thể hiện tín hiệu khá rõ trong quá trình EDA."
    },
    [pscustomobject]@{
        Number=5; Title="EDA 2 — Phân bố nồng độ cồn"; Time="50–60 giây";
        Objective="Mô tả hình dạng phân bố alcohol và lý do cần chuẩn hóa đối với mô hình tuyến tính.";
        Speech=@(
            "Biểu đồ histogram thể hiện tần suất của nồng độ alcohol; đường cong phía trên giúp quan sát xu hướng phân bố tổng thể. Trong bộ dữ liệu, alcohol nằm trong khoảng từ 8,4 đến 14,9 phần trăm. Phần lớn mẫu tập trung ở vùng khoảng 9 đến 11 phần trăm, sau đó tần suất giảm dần và tạo thành một đuôi kéo dài về phía các giá trị cao.",
            "Phân bố này không hoàn toàn đối xứng. Đồng thời, alcohol có thang đo khác đáng kể so với các biến như density, chlorides hoặc volatile acidity. Sự khác biệt về thang đo có thể làm các thuật toán dựa trên hệ số, đặc biệt là Linear Regression và Ridge Regression, hoạt động kém ổn định nếu dữ liệu không được chuẩn hóa.",
            "Vì vậy, nhóm sử dụng StandardScaler trong pipeline. Việc chuẩn hóa không làm thay đổi thứ tự hay bản chất của các mẫu, mà đưa các đặc trưng về thang đo thống nhất để mô hình tuyến tính học hệ số hợp lý hơn. Với các mô hình cây, bước này ít quan trọng hơn, nhưng sử dụng chung pipeline giúp quy trình nhất quán."
        );
        Transition="Phân bố riêng của alcohol mới chỉ cho biết hình dạng dữ liệu. Tiếp theo, nhóm đối chiếu alcohol với từng mức quality."
    },
    [pscustomobject]@{
        Number=6; Title="EDA 3 — Alcohol và quality"; Time="Khoảng 1 phút";
        Objective="Giải thích boxplot và xu hướng tương quan dương giữa alcohol và quality.";
        Speech=@(
            "Đây là boxplot của alcohol theo từng mức quality. Đường nằm giữa mỗi hộp là trung vị; phần hộp thể hiện 50 phần trăm dữ liệu trung tâm; các râu và các điểm rời cho biết độ phân tán và ngoại lai. Cách biểu diễn này giúp so sánh đồng thời vị trí trung tâm và mức biến động giữa các nhóm chất lượng.",
            "Quan sát từ trái sang phải, trung vị alcohol có xu hướng tăng ở các nhóm quality cao. Sự khác biệt rõ hơn tại quality 7 và 8, nơi alcohol trung tâm cao hơn so với nhóm 5 và 6. Kết quả này phù hợp với hệ số tương quan dương 0,48 giữa alcohol và quality trong ma trận tương quan.",
            "Tuy nhiên, các hộp vẫn chồng lấn đáng kể và có nhiều điểm ngoại lai. Nghĩa là không phải mọi mẫu có alcohol cao đều đạt quality cao, và ngược lại. Do đó, alcohol là một biến quan trọng nhưng không đủ để dự đoán độc lập. Mô hình cần kết hợp đồng thời nhiều thuộc tính hóa lý và học các tương tác giữa chúng."
        );
        Transition="Một đặc trưng khác có xu hướng theo chiều ngược lại là volatile acidity, tức độ axit bay hơi."
    },
    [pscustomobject]@{
        Number=7; Title="EDA 4 — Volatile acidity và quality"; Time="Khoảng 1 phút";
        Objective="Trình bày quan hệ nghịch giữa độ axit bay hơi và chất lượng.";
        Speech=@(
            "Biểu đồ này cũng là boxplot, nhưng biến được quan sát là volatile acidity. Xu hướng chính khá rõ: khi quality tăng từ 3 lên 8, trung vị volatile acidity nhìn chung giảm. Nhóm chất lượng thấp có mức axit bay hơi trung tâm cao hơn, trong khi các nhóm quality 7 và 8 tập trung ở vùng thấp hơn.",
            "Về mặt dữ liệu, kết quả này thể hiện một quan hệ nghịch. Ma trận tương quan cho hệ số khoảng âm 0,39 giữa volatile acidity và quality. Đây là một trong những mối liên hệ tuyến tính đáng chú ý nhất đối với target, chỉ đứng sau alcohol về độ lớn tuyệt đối.",
            "Dù vậy, các nhóm vẫn có vùng chồng lấn và xuất hiện ngoại lai, đặc biệt ở quality 5 và 6. Vì vậy, không nên diễn giải rằng volatile acidity trực tiếp quyết định quality. Biểu đồ chỉ cho thấy xu hướng thống kê trong tập dữ liệu; dự đoán cuối cùng vẫn phải dựa trên tổ hợp nhiều biến."
        );
        Transition="Để quan sát đồng thời mối liên hệ giữa toàn bộ các biến, nhóm sử dụng ma trận tương quan."
    },
    [pscustomobject]@{
        Number=8; Title="EDA 5 — Ma trận tương quan"; Time="Khoảng 1 phút 10 giây";
        Objective="Giải thích heatmap, tín hiệu với target và tương quan giữa các features.";
        Speech=@(
            "Ma trận tương quan thể hiện hệ số tương quan tuyến tính giữa từng cặp biến. Hệ số nằm trong khoảng từ âm 1 đến dương 1. Giá trị dương cho biết hai biến có xu hướng tăng cùng nhau; giá trị âm cho biết một biến tăng khi biến còn lại giảm. Đường chéo chính bằng 1 vì mỗi biến tương quan hoàn toàn với chính nó.",
            "Đối với quality, alcohol có tương quan dương 0,48 và volatile acidity có tương quan âm 0,39. Ngoài ra, sulphates có tương quan dương khoảng 0,25 và citric acid khoảng 0,23. Đây là các tín hiệu hữu ích, nhưng mức tương quan chưa đủ lớn để một biến đơn lẻ giải thích toàn bộ target.",
            "Giữa các đặc trưng cũng tồn tại tương quan đáng kể. Ví dụ, fixed acidity tương quan dương với density và tương quan âm với pH; free sulfur dioxide tương quan với total sulfur dioxide. Hiện tượng này có thể gây đa cộng tuyến cho mô hình tuyến tính, qua đó tạo động cơ sử dụng Ridge Regression. Mặt khác, các mô hình cây có thể học quan hệ phi tuyến và tương tác tốt hơn. Cuối cùng, cần nhấn mạnh rằng tương quan không đồng nghĩa quan hệ nhân quả."
        );
        Transition="Sau EDA, nhóm xây dựng quy trình tiền xử lý theo thứ tự chặt chẽ để dữ liệu sạch và không xảy ra data leakage."
    },
    [pscustomobject]@{
        Number=9; Title="Tiền xử lý và ngăn ngừa data leakage"; Time="Khoảng 1 phút 20 giây";
        Objective="Trình bày đầy đủ quy trình làm sạch, chia dữ liệu, pipeline và nguyên tắc chống rò rỉ.";
        Speech=@(
            "Quy trình tiền xử lý được thực hiện theo sáu bước. Đầu tiên, nhóm kiểm tra schema, kiểu dữ liệu và giá trị thiếu. Dữ liệu gốc không có missing value, nhưng pipeline vẫn sử dụng median imputer để hệ thống có khả năng xử lý an toàn nếu dữ liệu thực tế phát sinh giá trị thiếu. Tiếp theo, nhóm loại 240 dòng trùng, đưa số mẫu từ 1.599 xuống 1.359. Các ngoại lai hợp lệ không bị xóa vì có thể đại diện cho những mẫu rượu đặc biệt.",
            "Sau làm sạch, dữ liệu được tách thành X gồm 11 đặc trưng và y là quality. Tập dữ liệu sau đó được chia theo tỷ lệ 80 phần trăm train và 20 phần trăm test, với random state bằng 42. Kết quả là 1.087 mẫu train và 272 mẫu test.",
            "Điểm quan trọng nhất để ngăn data leakage là phải chia train và test trước khi học bất kỳ tham số tiền xử lý nào. Median imputer và StandardScaler chỉ được fit trên train; test chỉ sử dụng các tham số đã học từ train để biến đổi. Cross Validation và tinh chỉnh siêu tham số cũng chỉ diễn ra trong tập train. Test set được giữ độc lập và chỉ dùng một lần ở bước đánh giá cuối.",
            "Toàn bộ imputer, scaler và mô hình được đóng gói trong một pipeline. Cách này bảo đảm quy trình biến đổi tại thời điểm dự đoán thực tế giống hệt quy trình huấn luyện, giảm nguy cơ sai lệch giữa môi trường nghiên cứu và môi trường triển khai."
        );
        Transition="Trên dữ liệu đã xử lý, nhóm thử nghiệm bốn mô hình. Trước hết là hai mô hình tuyến tính."
    },
    [pscustomobject]@{
        Number=10; Title="Mô hình 1 — Linear Regression và Ridge Regression"; Time="Khoảng 1 phút 15 giây";
        Objective="Giải thích nguyên lý bình phương tối thiểu và điều chuẩn L2.";
        Speech=@(
            "Linear Regression mô hình hóa quality như một tổ hợp tuyến tính của các đặc trưng. Mỗi đặc trưng được gán một hệ số, thể hiện mức thay đổi dự kiến của quality khi đặc trưng đó thay đổi và các biến khác được giữ cố định. Quá trình huấn luyện tìm bộ hệ số sao cho tổng sai số bình phương giữa dự đoán và giá trị thực là nhỏ nhất.",
            "Ưu điểm của Linear Regression là tốc độ nhanh và khả năng diễn giải tương đối rõ. Tuy nhiên, mô hình giả định quan hệ gần tuyến tính, trong khi chất lượng rượu có thể phụ thuộc vào các tương tác phức tạp. Ngoài ra, khi các đặc trưng tương quan với nhau, hệ số có thể trở nên kém ổn định.",
            "Ridge Regression mở rộng Linear Regression bằng cách bổ sung điều chuẩn L2. Thành phần phạt này co nhỏ các hệ số có độ lớn cao, từ đó hạn chế việc mô hình phụ thuộc quá mạnh vào một biến và cải thiện độ ổn định khi có đa cộng tuyến. Tham số alpha kiểm soát mức phạt: alpha càng lớn, hệ số càng bị co mạnh. Vì L2 phụ thuộc vào độ lớn hệ số, chuẩn hóa đặc trưng là bước cần thiết trước khi huấn luyện Ridge."
        );
        Transition="Hai mô hình tiếp theo sử dụng tổ hợp cây quyết định, phù hợp hơn với quan hệ phi tuyến."
    },
    [pscustomobject]@{
        Number=11; Title="Mô hình 2 — Random Forest và Gradient Boosting"; Time="Khoảng 1 phút 25 giây";
        Objective="Phân biệt cơ chế học song song của Random Forest và học tuần tự của Gradient Boosting.";
        Speech=@(
            "Random Forest là mô hình tổ hợp nhiều cây quyết định. Mỗi cây được huấn luyện trên một mẫu bootstrap và chỉ xem xét một tập con ngẫu nhiên của các đặc trưng tại mỗi lần chia nhánh. Các cây học tương đối độc lập, sau đó dự đoán cuối cùng được lấy trung bình. Cơ chế ngẫu nhiên hóa và trung bình hóa giúp giảm phương sai so với một cây đơn lẻ, đồng thời mô hình có thể học quan hệ phi tuyến và tương tác giữa các biến.",
            "Gradient Boosting cũng kết hợp nhiều cây, nhưng các cây được xây dựng tuần tự. Cây sau tập trung học phần sai số, hay residual, mà tổ hợp trước chưa giải thích được. Dự đoán cuối cùng là tổng có trọng số của các cây. Nhờ liên tục sửa sai, Gradient Boosting thường đạt độ chính xác cao, đặc biệt với dữ liệu dạng bảng.",
            "Sự khác biệt cốt lõi là Random Forest giảm phương sai thông qua nhiều cây học song song, còn Gradient Boosting giảm sai lệch bằng chuỗi cây học nối tiếp. Gradient Boosting nhạy hơn với learning rate, số cây và độ sâu; nếu tinh chỉnh không phù hợp, mô hình có thể overfit. Random Forest thường ổn định hơn nhưng có kích thước mô hình lớn và khó diễn giải trực tiếp."
        );
        Transition="Để so sánh và tinh chỉnh các mô hình một cách đáng tin cậy, nhóm sử dụng 5-fold Cross Validation trên tập train."
    },
    [pscustomobject]@{
        Number=12; Title="Tinh chỉnh siêu tham số và Cross Validation"; Time="Khoảng 1 phút 20 giây";
        Objective="Mô tả 5-fold CV, tiêu chí chọn cấu hình và các kết quả tuning thực tế.";
        Speech=@(
            "Trong 5-fold Cross Validation, tập train được chia thành năm phần. Ở mỗi lượt, bốn phần được dùng để huấn luyện và một phần được dùng để validation. Vị trí của phần validation được luân phiên qua năm lượt, vì vậy mỗi mẫu trong tập train được dùng làm validation đúng một lần. Kết quả của cấu hình là RMSE trung bình trên năm fold.",
            "Nhóm thử nghiệm nhiều cấu hình siêu tham số và chọn cấu hình có CV RMSE thấp. Với Ridge Regression, alpha bằng 10 cho CV RMSE khoảng 0,6648. Với Random Forest, cấu hình 200 cây, max depth bằng 10 và min samples split bằng 2 đạt khoảng 0,6583. Với Gradient Boosting, learning rate 0,05, max depth bằng 3 và 100 cây đạt khoảng 0,6571.",
            "Gradient Boosting có CV RMSE thấp hơn một lượng nhỏ trong vòng đánh giá này. Tuy nhiên, lựa chọn cuối cùng không dựa duy nhất vào một con số CV. Nhóm còn xem xét đồng thời kết quả trên test sau tuning, MAE, RMSE, R bình phương, độ ổn định và khả năng đóng gói triển khai. Toàn bộ quá trình tuning chỉ sử dụng train; test set vẫn được khóa đến đánh giá cuối, nhờ đó tránh tối ưu gián tiếp theo test."
        );
        Transition="Các cấu hình được đánh giá bằng bốn metric. Slide tiếp theo giải thích ý nghĩa và cách đọc từng metric."
    },
    [pscustomobject]@{
        Number=13; Title="Metric đánh giá"; Time="Khoảng 1 phút";
        Objective="Giải thích MAE, MSE, RMSE, R² và lý do phải xem nhiều metric.";
        Speech=@(
            "MAE là trung bình trị tuyệt đối của sai số. Metric này có cùng đơn vị với quality và dễ diễn giải: nếu MAE xấp xỉ 0,47 thì dự đoán lệch trung bình khoảng 0,47 điểm. MAE tương đối ít bị chi phối bởi một số sai số rất lớn.",
            "MSE lấy bình phương sai số trước khi tính trung bình. Vì vậy, các dự đoán lệch nhiều bị phạt mạnh hơn, nhưng đơn vị của MSE là bình phương của đơn vị target. RMSE là căn bậc hai của MSE, vừa giữ đặc tính phạt sai số lớn vừa quay về cùng đơn vị điểm quality.",
            "R bình phương đo tỷ lệ biến thiên của target được mô hình giải thích so với dự đoán bằng giá trị trung bình. R bình phương càng cao thường càng tốt, nhưng đây không phải accuracy và không nên diễn giải thành tỷ lệ dự đoán đúng. Với bài toán này, nhóm ưu tiên MAE và RMSE thấp, đồng thời xem xét R bình phương cao. Việc dùng nhiều metric giúp tránh lựa chọn mô hình chỉ vì một chỉ số thuận lợi."
        );
        Transition="Dựa trên các metric vừa trình bày, đây là kết quả so sánh bốn mô hình trước vòng tinh chỉnh cuối."
    },
    [pscustomobject]@{
        Number=14; Title="Kết quả và bảng so sánh 4 mô hình"; Time="Khoảng 1 phút 20 giây";
        Objective="So sánh khách quan bốn mô hình trên cùng test set và rút ra nhận xét.";
        Speech=@(
            "Bảng này trình bày kết quả của bốn mô hình trên cùng tập test gồm 272 mẫu, trước vòng tinh chỉnh cuối của mô hình được chọn. Linear Regression và Ridge Regression cho kết quả gần như tương đương: RMSE khoảng 0,656 và R bình phương khoảng 0,392. Điều này cho thấy điều chuẩn L2 giúp ổn định hệ số nhưng chưa tạo ra cải thiện lớn về khả năng dự đoán, vì giới hạn chính có thể nằm ở giả định tuyến tính.",
            "Hai mô hình tổ hợp cây đạt kết quả tốt hơn rõ rệt. Random Forest có MAE thấp nhất, bằng khoảng 0,4682. Gradient Boosting có RMSE thấp hơn một lượng rất nhỏ, bằng 0,6193 so với 0,6196 của Random Forest, đồng thời R bình phương nhỉnh hơn ở mức 0,4586.",
            "Chênh lệch giữa hai mô hình cây khá nhỏ, nhưng cả hai đều giảm RMSE khoảng 0,037 điểm và tăng R bình phương khoảng 0,067 so với nhóm tuyến tính. Kết quả này củng cố nhận định rằng quan hệ giữa các đặc trưng hóa lý và quality không hoàn toàn tuyến tính. Tuy nhiên, nhóm chưa kết luận chỉ từ bảng này mà tiếp tục tinh chỉnh và cân nhắc khả năng triển khai."
        );
        Transition="Sau vòng tinh chỉnh và đánh giá cuối, mô hình được lựa chọn để triển khai là Random Forest Regressor."
    },
    [pscustomobject]@{
        Number=15; Title="Mô hình được lựa chọn"; Time="Khoảng 1 phút 20 giây";
        Objective="Nêu cấu hình, metric chính thức và lý do chọn Random Forest tuned.";
        Speech=@(
            "Mô hình cuối cùng là Random Forest Regressor đã tinh chỉnh, phiên bản 1.0.0. Cấu hình gồm 200 cây, max depth bằng 10, min samples split bằng 2 và random state bằng 42. Đây là cấu hình được đóng gói trong pipeline cùng các bước tiền xử lý.",
            "Trên tập test cuối, mô hình đạt MAE 0,468880; MSE 0,379509; RMSE 0,616043 và R bình phương 0,464240. So với Random Forest ban đầu, RMSE giảm từ khoảng 0,6196 xuống 0,6160 và R bình phương tăng từ khoảng 0,4580 lên 0,4642. MAE gần như giữ nguyên, cho thấy cải thiện chủ yếu nằm ở việc giảm các sai số lớn hơn.",
            "Nhóm lựa chọn Random Forest vì ba lý do. Thứ nhất, mô hình cân bằng tốt giữa MAE, RMSE và R bình phương sau tuning. Thứ hai, Random Forest phù hợp với quan hệ phi tuyến và tương tác giữa các đặc trưng, đồng thời tương đối ổn định trên dữ liệu dạng bảng. Thứ ba, pipeline đã được kiểm thử, đóng gói và tích hợp thuận lợi vào AI Service. Việc lựa chọn dựa trên hiệu quả tổng thể và khả năng vận hành, không phải vì tên mô hình phức tạp hơn.",
            "R bình phương 0,4642 cũng cho thấy mô hình mới giải thích được một phần biến thiên của quality. Đây là kết quả có ý nghĩa nhưng chưa đủ để khẳng định dự đoán tuyệt đối chính xác; yếu tố cảm quan và các biến chưa quan sát vẫn đóng vai trò đáng kể."
        );
        Transition="Mô hình sau khi lựa chọn được tích hợp vào kiến trúc hệ thống như sau."
    },
    [pscustomobject]@{
        Number=16; Title="Kiến trúc hệ thống dự đoán"; Time="Khoảng 1 phút 10 giây";
        Objective="Giải thích luồng dữ liệu từ người dùng đến mô hình và thành phần lưu lịch sử.";
        Speech=@(
            "Luồng xử lý bắt đầu khi người dùng nhập 11 thông số hóa lý trên giao diện. Giao diện thực hiện kiểm tra cơ bản về dữ liệu đầu vào, sau đó gửi yêu cầu đến Backend API. Backend chịu trách nhiệm điều phối, kiểm tra schema và chuyển dữ liệu sang AI Service.",
            "AI Service tải pipeline Random Forest đã đóng gói. Pipeline tự động áp dụng đúng thứ tự tiền xử lý đã học từ train, sau đó tạo ra điểm quality dự đoán. Kết quả được gửi ngược về Backend và trả cho giao diện để người dùng quan sát.",
            "Song song với việc trả kết quả, Backend có thể lưu thông tin đầu vào, kết quả dự đoán và thời gian thực hiện vào MongoDB để hình thành lịch sử dự đoán. Việc tách Frontend, Backend, AI Service và cơ sở dữ liệu thành các thành phần riêng giúp hệ thống dễ bảo trì, kiểm thử và thay thế phiên bản mô hình mà không cần thay đổi toàn bộ ứng dụng.",
            "Kiến trúc này cũng giảm nguy cơ sai lệch giữa huấn luyện và phục vụ, vì mọi yêu cầu dự đoán đều đi qua cùng một pipeline đã đóng gói, thay vì thực hiện tiền xử lý rời rạc ở nhiều nơi."
        );
        Transition="Cuối cùng, nhóm xin tổng kết các kết quả chính, hạn chế và hướng phát triển của đề tài."
    },
    [pscustomobject]@{
        Number=17; Title="Kết luận và hướng phát triển"; Time="Khoảng 1 phút 15 giây";
        Objective="Tổng kết đóng góp, nhìn nhận giới hạn và đề xuất hướng phát triển.";
        Speech=@(
            "Tóm lại, đề tài đã hoàn thành một quy trình tương đối đầy đủ từ dữ liệu đến hệ thống. Qua EDA, nhóm nhận thấy alcohol có liên hệ dương và volatile acidity có liên hệ âm đáng chú ý với quality. Kết quả thực nghiệm cho thấy hai mô hình tổ hợp cây vượt các mô hình tuyến tính; Random Forest sau tinh chỉnh được lựa chọn và tích hợp vào hệ thống dự đoán.",
            "Đề tài vẫn có một số hạn chế. Dữ liệu chỉ đại diện cho rượu vang đỏ Vinho Verde nên khả năng khái quát sang các loại rượu khác chưa được kiểm chứng. Target quality chịu ảnh hưởng cảm quan và các mức điểm hiếm có ít mẫu. R bình phương ở mức khoảng 0,464 cho thấy còn nhiều biến thiên chưa được giải thích, có thể đến từ nguyên liệu, quy trình sản xuất, thời gian ủ hoặc điều kiện bảo quản mà dataset không cung cấp.",
            "Trong tương lai, nhóm có thể mở rộng dữ liệu cho nhiều vùng và nhiều loại rượu; bổ sung các đặc trưng liên quan đến quy trình sản xuất; sử dụng phương pháp giải thích mô hình như feature importance hoặc SHAP; thực hiện kiểm định trên dữ liệu bên ngoài; đồng thời theo dõi data drift và xây dựng cơ chế tái huấn luyện định kỳ.",
            "Thông điệp cuối cùng là mô hình học máy có thể hỗ trợ đánh giá chất lượng nhanh và nhất quán hơn, nhưng độ tin cậy chỉ tăng khi dữ liệu đủ đại diện, quy trình đánh giá nghiêm ngặt và kết quả được giải thích trong đúng phạm vi. Nhóm em xin cảm ơn giảng viên và các bạn đã lắng nghe, và nhóm sẵn sàng trả lời câu hỏi."
        );
        Transition="Kết thúc phần trình bày — chuyển sang phần câu hỏi và thảo luận."
    }
)

function Set-SelectionFormat {
    param($Selection,[double]$Size=13,[bool]$Bold=$false,[bool]$Italic=$false,[int]$Color=$ink,[int]$Align=$wdAlignParagraphJustify,[double]$SpaceBefore=0,[double]$SpaceAfter=7,[double]$LeftIndent=0)
    $Selection.Font.Name = "Times New Roman"
    $Selection.Font.Size = $Size
    $Selection.Font.Bold = $(if($Bold){-1}else{0})
    $Selection.Font.Italic = $(if($Italic){-1}else{0})
    $Selection.Font.Color = $Color
    $Selection.ParagraphFormat.Alignment = $Align
    $Selection.ParagraphFormat.SpaceBefore = $SpaceBefore
    $Selection.ParagraphFormat.SpaceAfter = $SpaceAfter
    $Selection.ParagraphFormat.LineSpacing = 18
    $Selection.ParagraphFormat.LeftIndent = $LeftIndent
    $Selection.ParagraphFormat.FirstLineIndent = 0
}

function Add-Paragraph {
    param($Selection,[string]$Text,[double]$Size=13,[bool]$Bold=$false,[bool]$Italic=$false,[int]$Color=$ink,[int]$Align=$wdAlignParagraphJustify,[double]$SpaceBefore=0,[double]$SpaceAfter=7,[double]$LeftIndent=0)
    Set-SelectionFormat $Selection $Size $Bold $Italic $Color $Align $SpaceBefore $SpaceAfter $LeftIndent
    $Selection.TypeText($Text)
    $Selection.TypeParagraph()
}

function Add-PageBreak { param($Selection) $Selection.InsertBreak($wdPageBreak) }

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.Options.Pagination = $true
    $doc = $word.Documents.Add()
    $doc.PageSetup.TopMargin = $word.CentimetersToPoints(2.0)
    $doc.PageSetup.BottomMargin = $word.CentimetersToPoints(1.8)
    $doc.PageSetup.LeftMargin = $word.CentimetersToPoints(2.3)
    $doc.PageSetup.RightMargin = $word.CentimetersToPoints(2.0)
    $sel = $word.Selection

    # Cover
    Add-Paragraph $sel "KỊCH BẢN THUYẾT TRÌNH" 15 $true $false $accent $wdAlignParagraphCenter 70 18
    Add-Paragraph $sel "XÂY DỰNG HỆ THỐNG DỰ ĐOÁN`nCHẤT LƯỢNG RƯỢU VANG" 26 $true $false $ink $wdAlignParagraphCenter 10 22
    Add-Paragraph $sel "Lời thoại học thuật theo từng slide" 16 $false $true $muted $wdAlignParagraphCenter 4 45
    Add-Paragraph $sel "Môn học: Học máy cơ bản (Machine Learning)" 13 $false $false $ink $wdAlignParagraphCenter 0 8
    Add-Paragraph $sel "Nguyễn Văn Vũ — 12523093`nNguyễn Văn Linh — 10123207" 13 $false $false $ink $wdAlignParagraphCenter 0 8
    Add-Paragraph $sel "Thời lượng mục tiêu: 18–19 phút" 13 $true $false $accent $wdAlignParagraphCenter 25 8
    Add-Paragraph $sel "Tài liệu sử dụng cùng Wine_Quality_Presentation.pptx" 11 $false $false $muted $wdAlignParagraphCenter 85 0
    Add-PageBreak $sel

    # Guide and contents
    Add-Paragraph $sel "HƯỚNG DẪN SỬ DỤNG" 20 $true $false $ink $wdAlignParagraphLeft 0 10
    Add-Paragraph $sel "Tài liệu này là kịch bản gợi ý, không nên đọc hoàn toàn theo kiểu học thuộc. Khi trình bày, cần nhìn khán giả, sử dụng con trỏ để chỉ đúng vùng biểu đồ đang phân tích và ngắt nhịp sau các số liệu quan trọng. Có thể rút gọn mỗi đoạn nếu thời gian thực tế bị giới hạn." 13 $false $false $ink $wdAlignParagraphJustify 0 10
    Add-Paragraph $sel "Nguyên tắc diễn đạt học thuật" 14 $true $false $accent $wdAlignParagraphLeft 8 5
    Add-Paragraph $sel "• Phân biệt rõ quan sát thống kê với kết luận nhân quả.`n• Khi đọc metric, nêu cả giá trị và ý nghĩa; không gọi R² là accuracy.`n• Không khẳng định mô hình thay thế chuyên gia cảm quan.`n• Nhấn mạnh test set chỉ được dùng cho đánh giá cuối." 12.5 $false $false $ink $wdAlignParagraphLeft 0 10 12
    Add-Paragraph $sel "PHÂN BỔ THỜI GIAN" 14 $true $false $accent $wdAlignParagraphLeft 10 6
    foreach($slide in $slides){
        Add-Paragraph $sel ("Slide {0:D2} — {1}: {2}" -f $slide.Number,$slide.Title,$slide.Time) 11.2 $false $false $ink $wdAlignParagraphLeft 0 1
    }

    # One slide script per page
    foreach($slide in $slides){
        Add-PageBreak $sel
        Add-Paragraph $sel ("SLIDE {0:D2}" -f $slide.Number) 11 $true $false $accent $wdAlignParagraphLeft 0 2
        Add-Paragraph $sel $slide.Title 20 $true $false $ink $wdAlignParagraphLeft 0 8
        Add-Paragraph $sel ("Thời lượng gợi ý: " + $slide.Time) 11.5 $true $false $accent $wdAlignParagraphLeft 0 3
        Add-Paragraph $sel ("Mục tiêu trình bày: " + $slide.Objective) 11.5 $false $true $muted $wdAlignParagraphLeft 0 12
        Add-Paragraph $sel "LỜI THOẠI GỢI Ý" 12 $true $false $accent $wdAlignParagraphLeft 0 7
        foreach($paragraph in $slide.Speech){
            Add-Paragraph $sel $paragraph 13 $false $false $ink $wdAlignParagraphJustify 0 8 10
        }
        Add-Paragraph $sel "CÂU CHUYỂN Ý" 11 $true $false $accent $wdAlignParagraphLeft 7 3
        Add-Paragraph $sel $slide.Transition 12.5 $false $true $muted $wdAlignParagraphJustify 0 0 10
    }

    # Header and footer
    foreach($section in $doc.Sections){
        $header = $section.Headers.Item($wdHeaderFooterPrimary).Range
        $header.Text = "Kịch bản thuyết trình — Xây dựng hệ thống dự đoán chất lượng rượu vang"
        $header.Font.Name = "Times New Roman"; $header.Font.Size = 9; $header.Font.Color = $muted
        $header.ParagraphFormat.Alignment = $wdAlignParagraphRight
        $footer = $section.Footers.Item($wdHeaderFooterPrimary).Range
        $footer.ParagraphFormat.Alignment = $wdAlignParagraphCenter
        $footer.Font.Name = "Times New Roman"; $footer.Font.Size = 10; $footer.Font.Color = $muted
        $footer.Fields.Add($footer,$wdFieldPage) | Out-Null
    }

    try {
        $doc.BuiltInDocumentProperties.Item("Title").Value = "Kịch bản thuyết trình — Dự đoán chất lượng rượu vang"
        $doc.BuiltInDocumentProperties.Item("Subject").Value = "Lời thoại học thuật cho 17 slide"
        $doc.BuiltInDocumentProperties.Item("Author").Value = "Nguyễn Văn Vũ; Nguyễn Văn Linh"
    } catch {
        # Some Word 2019 installations do not expose BuiltInDocumentProperties
        # through late-bound COM; the document content is unaffected.
    }
    $doc.Repaginate()
    $doc.SaveAs2($output,$wdFormatDocumentDefault)
    $doc.Repaginate()
    $doc.Close()
    $word.Quit()
    $doc = $null; $word = $null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    Write-Output "Created: $output"
    Write-Output "Slides scripted: $($slides.Count)"
    Write-Output "Explicit page breaks: 18"
}
finally {
    if($null -ne $doc){try{$doc.Close(0)}catch{}}
    if($null -ne $word){try{$word.Quit()}catch{}}
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
