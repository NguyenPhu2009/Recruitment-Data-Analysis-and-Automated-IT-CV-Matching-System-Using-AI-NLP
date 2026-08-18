const COLORS = { teal: '#0B7A73', moss: '#25794C', amber: '#B5791F', coral: '#B84737', violet: '#5B5BC7' };

function showMatchState(name) {
    document.querySelectorAll('.match-state').forEach(el => el.classList.remove('is-visible'));
    document.getElementById('match-' + name).classList.add('is-visible');
}

var processingInterval = null;

// Bắt đầu chạy Animation hiển thị tiến trình giả lập trong lúc chờ AI phản hồi
function startProcessingUI() {
    var steps = [
        "Đang đọc nội dung CV...",
        "Đang trích xuất văn bản (PyMuPDF / pdfplumber)...",
        "Đang phân tích và so khớp kỹ năng với JD...",
        "Đang nạp mô hình FastText tính điểm ngữ nghĩa..."
    ];
    var i = 0;
    var label = document.getElementById('processingStatus');
    var bar = document.getElementById('progressFill');

    // Set thời gian chạy bar dài ra (15s) vì AI xử lý có thể mất 2-3 giây
    bar.style.animation = 'none'; void bar.offsetWidth; bar.style.animation = 'fillbar 15s ease forwards';
    label.textContent = steps[0];

    clearInterval(processingInterval);
    processingInterval = setInterval(function() {
        i++;
        if (i < steps.length) { label.textContent = steps[i]; }
    }, 1200);
}

// Dừng Animation khi có kết quả từ AI
function stopProcessingUI() {
    clearInterval(processingInterval);
    var bar = document.getElementById('progressFill');
    bar.style.animation = 'none';
    bar.style.width = '100%';
}

function buildDial(container, percent, colorHex, size, showTicks) {
    var strokeWidth = size * 0.075;
    var tickPad = showTicks ? size * 0.09 : 0;
    var radius = (size - strokeWidth) / 2 - tickPad;
    var cx = size / 2, cy = size / 2;
    var circumference = 2 * Math.PI * radius;
    var offset = circumference * (1 - percent / 100);
    var ticks = '';
    if (showTicks) {
        var tickCount = 40;
        var r1 = radius + strokeWidth / 2 + 4;
        var r2 = r1 + size * 0.035;
        for (var i = 0; i < tickCount; i++) {
            var angle = (i / tickCount) * Math.PI * 2 - Math.PI / 2;
            var major = (i % 5 === 0);
            var a1 = major ? r1 - 2 : r1, a2 = major ? r2 + 3 : r2;
            var x1 = cx + a1 * Math.cos(angle), y1 = cy + a1 * Math.sin(angle);
            var x2 = cx + a2 * Math.cos(angle), y2 = cy + a2 * Math.sin(angle);
            ticks += '<line x1="' + x1.toFixed(2) + '" y1="' + y1.toFixed(2) + '" x2="' + x2.toFixed(2) + '" y2="' + y2.toFixed(2) + '" stroke="' + (major ? '#B9C4C2' : '#DAE1DF') + '" stroke-width="' + (major ? 2 : 1) + '" stroke-linecap="round"/>';
        }
    }
    var svg = '<svg width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + ' ' + size + '">' + ticks +
        '<circle cx="' + cx + '" cy="' + cy + '" r="' + radius + '" fill="none" stroke="#E3E9E7" stroke-width="' + strokeWidth + '"/>' +
        '<circle class="dial-arc" cx="' + cx + '" cy="' + cy + '" r="' + radius + '" fill="none" stroke="' + colorHex + '" stroke-width="' + strokeWidth + '" stroke-linecap="round" stroke-dasharray="' + circumference + '" stroke-dashoffset="' + circumference + '" transform="rotate(-90 ' + cx + ' ' + cy + ')"/>' +
        '</svg>';
    container.innerHTML = svg;
    var arc = container.querySelector('.dial-arc');
    requestAnimationFrame(function() {
        requestAnimationFrame(function() {
            arc.style.transition = 'stroke-dashoffset 1.1s cubic-bezier(.3,.8,.3,1)';
            arc.style.strokeDashoffset = offset;
        });
    });
}

// Hàm render dữ liệu THẬT trả về từ API AI (ĐÃ THÊM THAM SỐ jdText)
function renderResult(data, jdText) {
    var pct = data.overall_score || 0;
    var label = 'Phù hợp tốt', badgeClass = 'badge-moss', color = COLORS.moss;

    if (pct < 50) { label = 'Chưa phù hợp'; badgeClass = 'badge-coral'; color = COLORS.coral; }
    else if (pct < 70) { label = 'Phù hợp trung bình'; badgeClass = 'badge-amber'; color = COLORS.amber; }

    // 1. Cập nhật Điểm tổng (Dial)
    document.getElementById('mainDialPercent').textContent = pct + '%';
    var lbl = document.getElementById('mainDialLabel');
    lbl.textContent = label;
    lbl.className = 'dial-status badge ' + badgeClass;
    buildDial(document.getElementById('mainDial'), pct, color, 220, true);

    // 2. Cập nhật Điểm thành phần (Đã map theo các ID chuẩn bên HTML)
    document.getElementById('score-skill-bar').style.width = (data.skill_score || 0) + '%';
    document.getElementById('score-skill-val').textContent = (data.skill_score || 0) + '%';

    document.getElementById('score-semantic-bar').style.width = (data.semantic_score || 0) + '%';
    document.getElementById('score-semantic-val').textContent = (data.semantic_score || 0) + '%';

    document.getElementById('score-exp-bar').style.width = (data.exp_score || 0) + '%';
    document.getElementById('score-exp-val').textContent = (data.exp_score || 0) + '%';

    // 3. Cập nhật Cột Kỹ năng Khớp / Thiếu (Dựa vào ID)
    const matchedList = data.matched_skills || [];
    const missingList = data.missing_skills || [];

    document.getElementById('matched-count').textContent = matchedList.length;
    document.getElementById('matched-skills-list').innerHTML = matchedList.map(s => `<span class="chip chip-match"><svg class="icon"><use href="#icon-check"/></svg>${s}</span>`).join('');

    document.getElementById('missing-count').textContent = missingList.length;
    document.getElementById('missing-skills-list').innerHTML = missingList.map(s => `<span class="chip chip-missing"><svg class="icon"><use href="#icon-x"/></svg>${s}</span>`).join('');

    // 4. Xử lý hiển thị JD và nút Xem thêm / Thu gọn
    const jdContainer = document.getElementById('match-jd-text');
    const toggleBtn = document.getElementById('toggleJdBtn');

    if (jdContainer && jdText) {
        // Biến \n thành <br> để giữ đúng format xuống dòng của JD
        jdContainer.innerHTML = jdText.replace(/\n/g, '<br>');

        // Hiện nút Xem thêm...
        toggleBtn.style.display = 'inline-block';
        toggleBtn.textContent = 'Xem thêm...';

        // Gắn sự kiện click
        toggleBtn.onclick = function() {
            if (jdContainer.style.webkitLineClamp === '3') {
                // Mở rộng: bỏ giới hạn dòng
                jdContainer.style.webkitLineClamp = 'unset';
                toggleBtn.textContent = 'Thu gọn';
            } else {
                // Thu gọn: giới hạn lại 3 dòng
                jdContainer.style.webkitLineClamp = '3';
                toggleBtn.textContent = 'Xem thêm...';
            }
        };
    }

    // 5. Xử lý Cảnh báo (Fallback TF-IDF)
    const warningBanner = document.getElementById('warningBanner');
    if(data.warning) {
        warningBanner.style.display = 'flex';
        warningBanner.querySelector('p').innerHTML = `${data.warning} <span class="tag">OOV: ${data.oov_rate || 0}% | Method: ${data.method_used || 'N/A'}</span>`;
    } else {
        warningBanner.style.display = 'none';
    }
}

function resetDropzone() {
    document.getElementById('fileChip').style.display = 'none';
    document.getElementById('dropzone').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = true;
    document.getElementById('cvFileInput').value = '';
}

function setSelectedFile(name) {
    document.getElementById('fileName').textContent = name;
    document.getElementById('fileChip').style.display = 'flex';
    document.getElementById('dropzone').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = false;
}

// Hàm gửi File CV xuống Backend
async function handleAnalyzeCV() {
    var fileInput = document.getElementById('cvFileInput');
    var jdTextInput = document.getElementById('jd_text');
    var jobTitleInput = document.getElementById('job_title'); // Lấy element ô input tiêu đề vị trí

    if (!fileInput.files.length) {
        alert("Vui lòng upload CV của bạn!");
        return;
    }

    // Lấy nội dung văn bản JD
    var jdText = jdTextInput ? jdTextInput.value.trim() : "";
    if (!jdText || jdText.length < 10) {
        alert("Vui lòng dán Mô tả công việc (JD) hợp lệ vào ô trống! (Tối thiểu 10 ký tự)");
        return;
    }

    var jobTitle = jobTitleInput ? jobTitleInput.value.trim() : "";
    if (!jobTitle) {
        jobTitle = "Vị trí tùy chỉnh";
    }

    var formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('jd_text', jdText);
    formData.append('job_title', jobTitle);

    showMatchState('processing');
    startProcessingUI();

    try {
        const response = await fetch('/api/match-cv', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        stopProcessingUI();

        if (response.ok) {
            showMatchState('result');
            renderResult(result, jdText); // <-- ĐÃ TRUYỀN THÊM jdText VÀO ĐÂY
        } else {
            alert("Lỗi hệ thống: " + (result.message || "Không thể phân tích CV"));
            showMatchState('upload');
        }
    } catch (error) {
        stopProcessingUI();
        console.error("Lỗi Fetch API:", error);
        alert("Lỗi kết nối đến máy chủ AI. Vui lòng kiểm tra lại server.");
        showMatchState('upload');
    }
}

function setupMatchEvents() {
    document.getElementById('analyzeBtn')?.addEventListener('click', handleAnalyzeCV);

    document.getElementById('retryBtn')?.addEventListener('click', function() {
        showMatchState('upload');
        resetDropzone();
    });

    document.getElementById('warningDismiss')?.addEventListener('click', function() {
        document.getElementById('warningBanner').style.display = 'none';
    });

    var dropzone = document.getElementById('dropzone');
    var fileInput = document.getElementById('cvFileInput');

    if(dropzone && fileInput) {
        dropzone.addEventListener('click', function() { fileInput.click(); });
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length) { setSelectedFile(fileInput.files[0].name); }
        });
        ['dragover', 'dragleave', 'drop'].forEach(function(evt) {
            dropzone.addEventListener(evt, function(e) {
                e.preventDefault();
                if (evt === 'dragover') dropzone.classList.add('is-dragover');
                if (evt === 'dragleave') dropzone.classList.remove('is-dragover');
                if (evt === 'drop') {
                    dropzone.classList.remove('is-dragover');
                    var name = (e.dataTransfer.files[0] && e.dataTransfer.files[0].name) || 'CV.pdf';
                    setSelectedFile(name);
                }
            });
        });
        document.getElementById('fileRemove').addEventListener('click', resetDropzone);
    }

    // Load mini dials trong bảng Lịch sử (nếu có)
    document.querySelectorAll('.mini-dial').forEach(function(el) {
        var pct = parseInt(el.dataset.percent, 10);
        var color = COLORS[el.dataset.color] || COLORS.teal;
        buildDial(el, pct, color, 36, false);
    });
}