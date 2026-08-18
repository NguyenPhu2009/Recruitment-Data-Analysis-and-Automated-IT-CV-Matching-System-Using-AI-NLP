// Hàm kiểm tra trạng thái đăng nhập
async function checkAuthStatus() {
    try {
        const res = await fetch('/api/auth/me'); // Cập nhật URL
        const data = await res.json();
        if (data.is_logged_in) {
            updateNavForLoggedInUser(data.user);
        }
    } catch (e) {
        console.warn('Chưa thể kiểm tra trạng thái đăng nhập:', e);
    }
}

// Cập nhật góc phải Thanh Navigation khi đã Đăng nhập
function updateNavForLoggedInUser(user) {
    const navAuth = document.querySelector('.nav-auth');
    if (navAuth) {
        navAuth.innerHTML = `
            <span style="font-size: 13.5px; font-weight: 600; color: var(--teal-deep);">👤 ${user.full_name}</span>
            <button class="btn btn-ghost" onclick="handleLogout()" style="padding: 6px 12px; font-size: 13px;">Đăng xuất</button>
        `;
    }
    const matchSavePrompt = document.getElementById('match-save-prompt');
    if (matchSavePrompt) {
        matchSavePrompt.style.display = 'none';
    }
}

// Hàm gửi request Đăng ký
async function handleRegister(e) {
    e.preventDefault();
    const fullName = document.getElementById('rg-name').value.trim();
    const email = document.getElementById('rg-email').value.trim();
    const password = document.getElementById('rg-pass').value;
    const confirmPassword = document.getElementById('rg-pass2').value;

    if (!fullName || !email || !password) { alert('Vui lòng điền đầy đủ các trường thông tin!'); return; }
    if (password !== confirmPassword) { alert('Mật khẩu nhập lại không khớp!'); return; }

    try {
        const response = await fetch('/api/auth/register', {  // Cập nhật URL
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ full_name: fullName, email: email, password: password, confirm_password: confirmPassword })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            setAuthTab('login');
            document.getElementById('li-email').value = email;
        } else {
            alert(result.message || 'Đăng ký thất bại!');
        }
    } catch (err) {
        console.error(err);
        alert('Có lỗi xảy ra khi kết nối tới Server!');
    }
}

// Hàm gửi request Đăng nhập
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('li-email').value.trim();
    const password = document.getElementById('li-pass').value;

    if (!email || !password) { alert('Vui lòng nhập đầy đủ Email và Mật khẩu!'); return; }

    try {
        const response = await fetch('/api/auth/login', {  // Cập nhật URL
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: password })
        });
        const result = await response.json();
        if (response.ok) {
            alert('Chào mừng ' + result.user.full_name + ' đã quay trở lại!');
            updateNavForLoggedInUser(result.user);
            showPage('dashboard');
        } else {
            alert(result.message || 'Đăng nhập thất bại!');
        }
    } catch (err) {
        console.error(err);
        alert('Có lỗi kết nối hệ thống!');
    }
}

// Hàm Đăng xuất
async function handleLogout() {
    if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
        await fetch('/api/auth/logout', { method: 'POST' }); // Cập nhật URL
        window.location.reload();
    }
}

// --- TÍNH NĂNG MỚI: Xử lý Đặt lại mật khẩu (Demo) ---
async function handleResetPassword(e) {
    e.preventDefault();
    const email = document.getElementById('rs-email').value.trim();
    const newPassword = document.getElementById('rs-pass').value;
    const confirmPassword = document.getElementById('rs-pass2').value;

    if (!email || !newPassword || !confirmPassword) {
        alert('Vui lòng điền đầy đủ thông tin!');
        return;
    }
    if (newPassword !== confirmPassword) {
        alert('Mật khẩu nhập lại không khớp!');
        return;
    }

    try {
        const response = await fetch('/api/auth/reset-password-demo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, new_password: newPassword })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Đổi mật khẩu thành công! Bạn có thể đăng nhập ngay bây giờ.');

            // Chuyển về màn hình đăng nhập
            document.getElementById('auth-reset-panel').style.display = 'none';
            document.getElementById('auth-login-panel').style.display = 'block';
            document.getElementById('li-email').value = email;
            document.getElementById('li-pass').value = '';

            // Xóa rỗng form reset
            document.getElementById('rs-email').value = '';
            document.getElementById('rs-pass').value = '';
            document.getElementById('rs-pass2').value = '';
        } else {
            alert(data.message || 'Có lỗi xảy ra!');
        }
    } catch (error) {
        console.error('Lỗi API:', error);
        alert('Không thể kết nối đến máy chủ.');
    }
}

function setupAuthEvents() {
    const registerBtn = document.querySelector('#auth-register-panel .btn-primary');
    if (registerBtn) registerBtn.addEventListener('click', handleRegister);

    const loginBtn = document.querySelector('#auth-login-panel .btn-primary');
    if (loginBtn) loginBtn.addEventListener('click', handleLogin);

    // --- TÍNH NĂNG MỚI: Bắt sự kiện form Đặt lại mật khẩu ---
    const showResetBtn = document.getElementById('btn-show-reset');
    if (showResetBtn) {
        showResetBtn.addEventListener('click', () => {
            document.getElementById('auth-login-panel').style.display = 'none';
            document.getElementById('auth-register-panel').style.display = 'none';
            document.getElementById('auth-reset-panel').style.display = 'block';
        });
    }

    const backToLoginBtn = document.getElementById('btn-back-to-login');
    if (backToLoginBtn) {
        backToLoginBtn.addEventListener('click', () => {
            document.getElementById('auth-reset-panel').style.display = 'none';
            document.getElementById('auth-login-panel').style.display = 'block';
        });
    }

    const submitResetBtn = document.getElementById('btn-submit-reset');
    if (submitResetBtn) submitResetBtn.addEventListener('click', handleResetPassword);
}