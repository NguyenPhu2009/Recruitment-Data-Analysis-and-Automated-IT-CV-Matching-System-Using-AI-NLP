// Xử lý chuyển trang (SPA)
function showPage(name, param) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));

    const targetPage = document.getElementById('page-' + name);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    var navKey = (name === 'job-detail') ? 'jobs' : name;
    document.querySelectorAll('.nav-link').forEach(function(b) {
        b.classList.toggle('active', b.dataset.goto === navKey && name !== 'auth');
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
    document.getElementById('navLinks').classList.remove('is-open');

    // ĐÃ THÊM: Nếu chuyển sang trang chi tiết công việc và có jobId (param), tiến hành gọi API lấy data thật
    if (name === 'job-detail' && param) {
        if (typeof window.fetchJobDetail === 'function') {
            window.fetchJobDetail(param);
        }
    }

    if (name === 'history' && typeof initHistoryChartOnce === 'function') {
        initHistoryChartOnce();
    }
}

// Xử lý chuyển Tab Đăng nhập / Đăng ký
function setAuthTab(tab) {
    document.querySelectorAll('.authtab').forEach(function(b) {
        b.classList.toggle('active', b.dataset.authtab === tab);
    });
    document.getElementById('auth-login-panel').style.display = (tab === 'login') ? 'block' : 'none';
    document.getElementById('auth-register-panel').style.display = (tab === 'register') ? 'block' : 'none';
}

// Đăng ký các sự kiện UI cơ bản
function setupUIEvents() {
    // ĐÃ ÁP DỤNG PHƯƠNG ÁN 1: Event Delegation toàn cục cho data-goto
    document.addEventListener('click', function(e) {
        const el = e.target.closest('[data-goto]');
        if (el) {
            // Ngăn chặn hành vi mặc định (ví dụ nếu nút là thẻ <a> sẽ không bị reload trang)
            e.preventDefault();

            // ĐÃ THÊM: Lấy thuộc tính data-id (nếu có) trên phần tử được click để truyền vào showPage
            const param = el.getAttribute('data-id') || null;

            showPage(el.dataset.goto, param);

            if (el.dataset.authtab) setAuthTab(el.dataset.authtab);
        }
    });

    document.getElementById('burger').addEventListener('click', function() {
        document.getElementById('navLinks').classList.toggle('is-open');
    });

    document.querySelectorAll('.authtab').forEach(function(b) {
        b.addEventListener('click', function() { setAuthTab(b.dataset.authtab); });
    });
}