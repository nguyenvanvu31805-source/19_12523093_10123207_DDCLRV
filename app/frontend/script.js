/**
 * Frontend JavaScript cho ứng dụng Dự đoán chất lượng rượu vang
 * Giao tiếp trực tiếp với Backend API qua HTTP POST http://127.0.0.1:5000/predict
 */

const BACKEND_URL = "http://127.0.0.1:5000";

// Bộ 11 giá trị mẫu chuẩn theo yêu cầu đồ án
const SAMPLE_DATA = {
  fixed_acidity: 7.4,
  volatile_acidity: 0.7,
  citric_acid: 0.0,
  residual_sugar: 1.9,
  chlorides: 0.076,
  free_sulfur_dioxide: 11,
  total_sulfur_dioxide: 34,
  density: 0.9978,
  pH: 3.51,
  sulphates: 0.56,
  alcohol: 9.4
};

// Danh sách định danh 11 trường tương ứng với key JSON gửi lên Backend
const FEATURE_MAP = [
  { id: "fixed_acidity", key: "fixed acidity" },
  { id: "volatile_acidity", key: "volatile acidity" },
  { id: "citric_acid", key: "citric acid" },
  { id: "residual_sugar", key: "residual sugar" },
  { id: "chlorides", key: "chlorides" },
  { id: "free_sulfur_dioxide", key: "free sulfur dioxide" },
  { id: "total_sulfur_dioxide", key: "total sulfur dioxide" },
  { id: "density", key: "density" },
  { id: "pH", key: "pH" },
  { id: "sulphates", key: "sulphates" },
  { id: "alcohol", key: "alcohol" }
];

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("prediction-form");
  const btnSample = document.getElementById("btn-sample");
  const btnSubmit = document.getElementById("btn-submit");
  const btnText = document.getElementById("btn-text");
  const btnSpinner = document.getElementById("btn-spinner");
  const errorBox = document.getElementById("error-box");
  const errorMessage = document.getElementById("error-message");
  const resultBox = document.getElementById("result-box");
  const scoreDisplay = document.getElementById("score-display");
  const scoreText = document.getElementById("score-text");
  const rawScore = document.getElementById("raw-score");

  // Nạp lại dữ liệu mẫu khi click nút "Điền giá trị mẫu"
  btnSample.addEventListener("click", () => {
    Object.keys(SAMPLE_DATA).forEach((fieldId) => {
      const input = document.getElementById(fieldId);
      if (input) {
        input.value = SAMPLE_DATA[fieldId];
      }
    });
    hideError();
    hideResult();
  });

  // Xử lý gửi Form dự đoán
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    hideResult();

    // 1. Kiểm tra và chuyển đổi dữ liệu của 11 trường
    const payload = {};
    for (const item of FEATURE_MAP) {
      const input = document.getElementById(item.id);
      if (!input || input.value.trim() === "") {
        showError("Vui lòng điền đầy đủ 11 thông số trước khi dự đoán.");
        input?.focus();
        return;
      }

      const numVal = parseFloat(input.value);
      if (isNaN(numVal)) {
        showError(`Giá trị của trường "${item.key}" không hợp lệ. Vui lòng nhập số.`);
        input.focus();
        return;
      }

      // Giữ nguyên tên key tiếng Anh chính xác (có khoảng trắng)
      payload[item.key] = numVal;
    }

    // 2. Chuyển trạng thái đang dự đoán (loading)
    setLoading(true);

    try {
      // 3. Gửi HTTP POST request sang Backend
      const response = await fetch(`${BACKEND_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      // 4. Xử lý các mã trạng thái phản hồi
      if (response.ok) {
        const data = await response.json();
        const score = data.prediction;
        showResult(score);
      } else if (response.status === 422) {
        showError("Dữ liệu nhập không hợp lệ. Vui lòng kiểm tra lại.");
      } else if (response.status === 503) {
        showError("AI Service hiện không khả dụng.");
      } else {
        let detail = "";
        try {
          const errData = await response.json();
          detail = errData.detail ? `: ${errData.detail}` : "";
        } catch (_) {
          // Bỏ qua nếu không parse được json
        }
        showError(`Lỗi máy chủ (${response.status})${detail}`);
      }
    } catch (networkError) {
      // Khi không thể kết nối tới Backend (Backend tắt hoặc lỗi mạng)
      console.error("Network Error:", networkError);
      showError("Không thể kết nối tới Backend.");
    } finally {
      // 5. Kết thúc trạng thái loading
      setLoading(false);
    }
  });

  // Helper hiển thị trạng thái nút khi loading
  function setLoading(isLoading) {
    btnSubmit.disabled = isLoading;
    if (isLoading) {
      btnText.textContent = "Đang dự đoán...";
      btnSpinner.style.display = "inline-block";
    } else {
      btnText.textContent = "Dự đoán chất lượng";
      btnSpinner.style.display = "none";
    }
  }

  // Helper hiển thị thông báo lỗi
  function showError(msg) {
    errorMessage.textContent = msg;
    errorBox.style.display = "flex";
    hideResult();
  }

  // Helper ẩn thông báo lỗi
  function hideError() {
    errorBox.style.display = "none";
    errorMessage.textContent = "";
  }

  // Helper hiển thị kết quả
  function showResult(score) {
    const roundedScore = Number(score).toFixed(2);
    scoreDisplay.textContent = roundedScore;
    scoreText.textContent = `Điểm chất lượng dự đoán: ${roundedScore}`;
    rawScore.textContent = Number(score).toFixed(4);
    resultBox.style.display = "block";
    resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Helper ẩn kết quả
  function hideResult() {
    resultBox.style.display = "none";
  }
});
