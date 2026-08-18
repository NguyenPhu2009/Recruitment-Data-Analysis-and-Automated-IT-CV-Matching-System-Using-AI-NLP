// Biến lưu trữ toàn cục để giữ data lịch sử
let globalHistoryData = [];

window.initHistoryChartOnce = function() {
    fetchHistoryData();
};

async function fetchHistoryData() {
    const tbody = document.getElementById('history-table-body');
    const authStatus = document.getElementById('history-auth-status');

    if (!tbody) return;

    // Reset giao diện loading mỗi lần vào lại trang
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--ink-faint);">Đang tải dữ liệu lịch sử...</td></tr>`;

    try {
        const response = await fetch('/api/history');
        const data = await response.json();

        // ❌ NẾU CHƯA ĐĂNG NHẬP (API trả về lỗi 401)
        if (response.status === 401) {
            if (authStatus) {
                authStatus.textContent = 'Cần đăng nhập';
                authStatus.style.color = 'var(--coral)';
            }
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--coral);">Vui lòng <a href="#" data-goto="auth" data-authtab="login" style="color:var(--teal);text-decoration:underline;">đăng nhập</a> để xem lịch sử phân tích CV của bạn.</td></tr>`;
            return;
        }

        // ✅ NẾU THÀNH CÔNG VÀ CÓ DỮ LIỆU
        if (data.status === 'success') {
            if (authStatus) {
                authStatus.textContent = 'Lịch sử cá nhân';
                authStatus.style.color = 'var(--ink-faint)';
            }

            // Lưu vào biến toàn cục để dùng cho nút "Xem lại"
            globalHistoryData = data.history || [];
            renderHistoryTable(globalHistoryData);
        }
    } catch (error) {
        console.error("Lỗi tải lịch sử:", error);
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--coral);">Lỗi kết nối máy chủ. Không thể tải lịch sử.</td></tr>`;
    }
}

// Hàm phân loại màu sắc và badge dựa trên điểm số
function getScoreConfig(score) {
    if (score < 50) return { color: 'coral', label: 'Chưa phù hợp', badge: 'badge-coral' };
    if (score < 70) return { color: 'amber', label: 'Phù hợp trung bình', badge: 'badge-amber' };
    return { color: 'moss', label: 'Phù hợp tốt', badge: 'badge-moss' };
}

// Hàm render dữ liệu ra bảng HTML
function renderHistoryTable(historyArray) {
    const tbody = document.getElementById('history-table-body');

    // Nếu đã đăng nhập nhưng chưa test CV lần nào
    if (historyArray.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--ink-faint);">Bạn chưa có lượt phân tích CV nào được lưu lại.</td></tr>`;
        return;
    }

    // ĐÃ SỬA: Loại bỏ company_name vì người dùng tự dán JD
    const rowsHtml = historyArray.map((item, index) => {
        const conf = getScoreConfig(item.overall_score);
        const dateStr = item.analyzed_at ? item.analyzed_at.split(' ')[0] : 'Gần đây';

        return `
        <tr>
            <td class="mono">${dateStr}</td>
            <td>
                <div class="hist-job" style="font-weight: 500;">${item.job_title}</div>
            </td>
            <td>
                <div class="hist-score">
                    <div class="mini-dial" data-percent="${item.overall_score}" data-color="${conf.color}"></div>
                    <span class="num">${item.overall_score}%</span>
                </div>
            </td>
            <td><span class="badge ${conf.badge}">${conf.label}</span></td>
            <td>
                <button class="btn btn-outline btn-sm view-history-btn" onclick="viewHistoryDetail(${index})">Xem lại</button>
            </td>
        </tr>
        `;
    }).join('');

    tbody.innerHTML = rowsHtml;

    // Kích hoạt lại hiệu ứng vòng tròn cho các thẻ .mini-dial vừa được chèn vào DOM
    if (typeof buildDial === 'function') {
        const COLORS = { teal: '#0B7A73', moss: '#25794C', amber: '#B5791F', coral: '#B84737', violet: '#5B5BC7' };

        document.querySelectorAll('#history-table-body .mini-dial').forEach(function(el) {
            const pct = parseInt(el.dataset.percent, 10);
            const colorHex = COLORS[el.dataset.color] || COLORS.teal;
            buildDial(el, pct, colorHex, 36, false);
        });
    } else {
        console.warn("Không tìm thấy hàm buildDial (từ match.js) để vẽ vòng tròn điểm số.");
    }
}

// Bắt sự kiện Xem lại chi tiết lịch sử
window.viewHistoryDetail = function(index) {
    const item = globalHistoryData[index];
    if(!item) return;

    // 1. Đổi active trên thanh Navbar
    document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
    const matchNavLink = document.querySelector('[data-goto="match"]');
    if (matchNavLink) matchNavLink.classList.add('active');

    // 2. Chuyển màn hình chính sang trang Match
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const matchPage = document.getElementById('page-match');
    if (matchPage) matchPage.classList.add('active');

    // 3. Tính toán lại điểm ngữ nghĩa (Semantic)
    let semScore = Math.round((item.overall_score - (0.6 * item.skill_score) - (0.1 * item.exp_score)) / 0.3);
    if (semScore < 0) semScore = 0;
    if (semScore > 100) semScore = 100;

    // 4. Định dạng lại nội dung gợi ý, chèn thêm đoạn JD đã lưu
    const jdPreview = item.job_jd && item.job_jd.length > 200 ? item.job_jd.substring(0, 200) + '...' : (item.job_jd || 'Không có dữ liệu JD');
    const customSuggestion = `<b>Mô tả công việc đã nộp:</b><br><span style="color: var(--ink-light); font-size: 13px;">${jdPreview}</span><br><br><i>Dữ liệu được trích xuất từ Lịch sử hệ thống. Bạn có thể dán JD mới và thử lại với file CV của mình nhé!</i>`;

    // 5. Tạo Object giống hệt JSON trả về từ API AI
    const historyResultData = {
        overall_score: item.overall_score,
        skill_score: item.skill_score,
        semantic_score: semScore,
        exp_score: item.exp_score,
        matched_skills: item.matched_skills,
        missing_skills: item.missing_skills,
        suggestion: customSuggestion
    };

    // 6. Kích hoạt giao diện Kết quả và Render dữ liệu (Sử dụng lại 100% code bên match.js)
    if(typeof showMatchState === 'function') showMatchState('result');
    if(typeof renderResult === 'function') renderResult(historyResultData);
};