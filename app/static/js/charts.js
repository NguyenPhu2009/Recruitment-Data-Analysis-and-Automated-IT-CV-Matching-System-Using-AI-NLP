if (window.Chart) {
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.color = '#55676A';
    Chart.defaults.font.size = 12;
}

// Khai báo biến toàn cục để lưu instance của biểu đồ (Giúp reset lại khi chuyển trang hoặc cập nhật data)
let skillsChart, salaryChart, jobTypeChart, citiesChart;

async function initDashboardCharts() {
    if (!window.Chart || !document.getElementById('chartSkills')) return;

    // 1. KHỞI TẠO DỮ LIỆU RỖNG (Khắt khe: Không dùng data giả lập)
    let skillsData = { labels: [], values: [] };
    let salaryData = { labels: [], values: [] };
    let typeData = { labels: [], values: [] };
    let cityData = { labels: [], values: [] };

    // 2. GỌI ĐỒNG THỜI 4 API LẤY DỮ LIỆU THẬT TỪ BACKEND
    try {
        // Dùng Promise.all để gọi 4 API cùng lúc (giảm tối đa thời gian chờ)
        const [resSkills, resSalary, resType, resCity] = await Promise.all([
            fetch('/api/dashboard/top-skills').catch(() => null),
            fetch('/api/dashboard/salary-by-level').catch(() => null),
            fetch('/api/dashboard/job-type-distribution').catch(() => null),
            fetch('/api/dashboard/top-locations').catch(() => null)
        ]);

        // Trích xuất dữ liệu Top Skills
        if (resSkills && resSkills.ok) {
            const data = await resSkills.json();
            if (data.top_skills && data.top_skills.length > 0) {
                skillsData.labels = data.top_skills.map(item => item.skill_name);
                skillsData.values = data.top_skills.map(item => item.job_count);
            }
        }

        // Trích xuất dữ liệu Salary
        if (resSalary && resSalary.ok) {
            const data = await resSalary.json();
            if (data.salary_by_level && data.salary_by_level.length > 0) {
                salaryData.labels = data.salary_by_level.map(item => item.job_level);
                salaryData.values = data.salary_by_level.map(item => item.avg_salary_million_vnd);
            }
        }

        // Trích xuất dữ liệu Job Type
        if (resType && resType.ok) {
            const data = await resType.json();
            if (data.job_type_distribution && data.job_type_distribution.length > 0) {
                typeData.labels = data.job_type_distribution.map(item => item.job_type);
                typeData.values = data.job_type_distribution.map(item => item.count);
            }
        }

        // Trích xuất dữ liệu Locations
        if (resCity && resCity.ok) {
            const data = await resCity.json();
            if (data.top_locations && data.top_locations.length > 0) {
                cityData.labels = data.top_locations.map(item => item.location);
                cityData.values = data.top_locations.map(item => item.count);
            }
        }
    } catch (error) {
        console.error('Lỗi kết nối API Dashboard:', error);
    }

    // 3. VẼ BIỂU ĐỒ (Sẽ trống trơn nếu API không trả về dữ liệu)

    // Biểu đồ Top Kỹ Năng
    if(skillsChart) skillsChart.destroy();
    skillsChart = new Chart(document.getElementById('chartSkills'), {
        type: 'bar',
        data: { labels: skillsData.labels,
            datasets: [{ data: skillsData.values, backgroundColor: '#0B7A73', borderRadius: 4, barThickness: 12 }] },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { x: { grid: { color: '#EEF1F0' } }, y: { grid: { display: false } } } }
    });

    // Biểu đồ Mức Lương
    if(salaryChart) salaryChart.destroy();
    salaryChart = new Chart(document.getElementById('chartSalary'), {
        type: 'bar',
        data: { labels: salaryData.labels,
            datasets: [{ data: salaryData.values, backgroundColor: '#5B5BC7', borderRadius: 6, maxBarThickness: 34 }] },
        options: { responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { grid: { color: '#EEF1F0' } }, x: { grid: { display: false } } } }
    });

    // Biểu đồ Loại Hình Công Việc
    // Biểu đồ Loại Hình Công Việc
    if(jobTypeChart) jobTypeChart.destroy();
    jobTypeChart = new Chart(document.getElementById('chartJobType'), {
        type: 'doughnut',
        data: {
            labels: typeData.labels,
            datasets: [{
                data: typeData.values,
                backgroundColor: [
                    '#E11D48', // Đỏ (Crimson)
                    '#F97316', // Cam (Tangerine)
                    '#EAB308', // Vàng (Mustard)
                    '#22C55E', // Lục (Emerald)
                    '#06B6D4', // Ngọc (Cyan)
                    '#3B82F6', // Lam (Sapphire)
                    '#4F46E5', // Chàm (Indigo)
                    '#A855F7', // Tím (Amethyst)
                    '#EC4899', // Hồng (Flamingo)
                    '#64748B'  // Xám (Slate)
                ],
                // THÊM 3 DÒNG NÀY ĐỂ XỬ LÝ CÁC LÁT CẮT QUÁ NHỎ:
                borderWidth: 2,             // Độ dày của viền cắt giữa các khối màu
                borderColor: '#ffffff',     // Viền màu trắng (trùng với màu nền card) để tạo độ thoáng
                hoverOffset: 6              // Phóng to khối màu lồi ra 6px khi rê chuột vào
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 10,
                        boxHeight: 10,
                        padding: 14,
                        usePointStyle: true
                    }
                }
            }
        }
    });

    // Biểu đồ Thành Phố
    if(citiesChart) citiesChart.destroy();
    citiesChart = new Chart(document.getElementById('chartCities'), {
        type: 'bar',
        data: { labels: cityData.labels,
            datasets: [{ data: cityData.values, backgroundColor: '#25794C', borderRadius: 6, maxBarThickness: 34 }] },
        options: { responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { grid: { color: '#EEF1F0' } }, x: { grid: { display: false } } } }
    });
}

// -----------------------------------------------------------------
// BIỂU ĐỒ LỊCH SỬ
// -----------------------------------------------------------------
var historyChartInited = false;
let trendChart;

function initHistoryChartOnce() {
    if (historyChartInited || !window.Chart || !document.getElementById('chartTrend')) return;
    historyChartInited = true;

    // Tương lai gắn API fetch('/api/history/trend') vào đây
    let trendData = { labels: [], values: [] }; // Khởi tạo rỗng chờ API

    if(trendChart) trendChart.destroy();
    trendChart = new Chart(document.getElementById('chartTrend'), {
        type: 'line',
        data: { labels: trendData.labels,
            datasets: [{ data: trendData.values, borderColor: '#0B7A73', backgroundColor: 'rgba(11,122,115,.1)', fill: true, tension: .35, pointRadius: 4, pointBackgroundColor: '#0B7A73' }] },
        options: { responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { min: 0, max: 100, grid: { color: '#EEF1F0' } }, x: { grid: { display: false } } } }
    });
}