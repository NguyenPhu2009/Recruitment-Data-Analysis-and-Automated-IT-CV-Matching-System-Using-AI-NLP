document.addEventListener('DOMContentLoaded', function () {
    // 1. Kiểm tra trạng thái đăng nhập
    checkAuthStatus();

    // 2. Khởi tạo các sự kiện giao diện (Menu, Tab, Đổi trang)
    setupUIEvents();

    // 3. Khởi tạo các sự kiện phần Chấm điểm CV
    setupMatchEvents();

    // 4. Khởi tạo sự kiện Đăng nhập / Đăng ký
    setupAuthEvents();
});

// Khởi tạo Chart.js khi toàn bộ trang (bao gồm thư viện) đã load xong
window.addEventListener('load', function() {
    if (window.Chart) {
        initDashboardCharts();
    } else {
        console.warn('Chart.js chưa tải được — kiểm tra kết nối mạng.');
    }
});