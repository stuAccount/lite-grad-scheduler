// API base URL
const API_BASE = window.location.origin;

// State
let courseRequests = [];
let isSignupMode = false;

// ========================================
// i18n (Localization)
// ========================================

const translations = {
    en: {
        app_title: "Graduate Course Scheduler",
        app_subtitle: "Automated conflict-free scheduling for graduate courses",
        login_btn: "🔑 Login",
        logout_btn: "Logout",
        login_title: "Login",
        signup_title: "Sign Up",
        label_username: "Username:",
        label_email: "Email:",
        label_password: "Password:",
        login_btn_modal: "Login",
        signup_btn_modal: "Sign Up",
        no_account_label: "Don't have an account?",
        signup_link: "Sign up",
        has_account_label: "Already have an account?",
        login_link: "Login",
        section_1_title: "1. Add Resources",
        add_professor_title: "Add Professor",
        label_prof_id: "Professor ID:",
        label_prof_name: "Professor Name:",
        label_dept: "Department (optional):",
        label_title: "Title (optional):",
        option_none: "None",
        option_assistant: "Assistant Professor",
        option_lecturer: "Lecturer",
        option_associate: "Associate Professor",
        option_full: "Full Professor",
        btn_add_professor: "Add Professor",
        add_classroom_title: "Add Classroom",
        label_room_id: "Classroom ID:",
        label_room_name: "Classroom Name:",
        label_capacity: "Capacity:",
        btn_add_classroom: "Add Classroom",
        section_2_title: "2. View Schedule",
        select_view_title: "Select View",
        label_view_by: "View By:",
        option_weekly: "Weekly Grid",
        option_by_professor: "By Professor",
        option_by_classroom: "By Classroom",
        option_select: "Select...",
        btn_load: "Load",
        export_schedule_title: "Export Schedule",
        export_description: "Download the schedule for printing or sharing.",
        btn_export_pdf: "📄 Export as PDF",
        btn_export_excel: "📊 Export as Excel",
        generate_schedule_title: "Generate New Schedule",
        generate_description: "Add course requests above, then click generate to create a conflict-free schedule.",
        label_course_id: "Course ID:",
        label_course_name: "Course Name:",
        label_professor: "Professor:",
        select_professor: "Select Professor",
        label_classroom: "Classroom:",
        select_classroom: "Select Classroom",
        label_credits: "Credits (optional):",
        label_hours: "Hours (optional):",
        label_type: "Type (optional):",
        option_required: "Required (必修)",
        option_elective: "Elective (选修)",
        btn_add_to_list: "Add to List",
        btn_generate: "Generate Schedule",
        section_3_title: "3. View Results",
        conflicts_title: "Conflicts",
        no_professors: "No professors added yet.",
        no_classrooms: "No classrooms added yet.",
        no_requests: "No course requests added yet.",
        msg_logged_in: "Logged in!",
        msg_logged_out: "Logged out",
        msg_account_created: "Account created!",
        msg_prof_added: "Professor added successfully",
        msg_room_added: "Classroom added successfully",
        msg_please_add_request: "Please add at least one course request",
        msg_schedule_generated: "Schedule generated: {total} courses scheduled",
        msg_no_courses: "No courses scheduled.",
        msg_no_conflicts: "✓ No conflicts detected!",
        msg_conflicts_detected: "⚠ {total} conflict(s) detected:",
        msg_error: "Error: ",
        msg_auth_failed: "Auth failed",
        msg_network_error: "Network error: ",
        label_period: "Period",
        label_prof: "Prof",
        label_room: "Room",
        label_day: "Day",
        monday: "Monday",
        tuesday: "Tuesday",
        wednesday: "Wednesday",
        thursday: "Thursday",
        friday: "Friday"
    },
    zh: {
        app_title: "研究生课程排课系统",
        app_subtitle: "为研究生课程提供自动化的无冲突排课解决方案",
        login_btn: "🔑 登录",
        logout_btn: "登出",
        login_title: "登录",
        signup_title: "注册",
        label_username: "用户名:",
        label_email: "电子邮箱:",
        label_password: "密码:",
        login_btn_modal: "登录",
        signup_btn_modal: "注册",
        no_account_label: "还没有账号？",
        signup_link: "立即注册",
        has_account_label: "已经有账号了？",
        login_link: "立即登录",
        section_1_title: "1. 添加资源",
        add_professor_title: "添加教师",
        label_prof_id: "教师ID:",
        label_prof_name: "教师姓名:",
        label_dept: "院系 (可选):",
        label_title: "职称 (可选):",
        option_none: "无",
        option_assistant: "助理教授",
        option_lecturer: "讲师",
        option_associate: "副教授",
        option_full: "教授",
        btn_add_professor: "添加教师",
        add_classroom_title: "添加教室",
        label_room_id: "教室ID:",
        label_room_name: "教室名称:",
        label_capacity: "容量:",
        btn_add_classroom: "添加教室",
        section_2_title: "2. 查看课表",
        select_view_title: "选择视图",
        label_view_by: "查看方式:",
        option_weekly: "周课表",
        option_by_professor: "按教师查看",
        option_by_classroom: "按教室查看",
        option_select: "请选择...",
        btn_load: "加载",
        export_schedule_title: "导出课表",
        export_description: "下载课表以便打印或分享。",
        btn_export_pdf: "📄 导出为 PDF",
        btn_export_excel: "📊 导出为 Excel",
        generate_schedule_title: "生成新课表",
        generate_description: "在上方添加课程请求，然后点击生成以创建无冲突课表。",
        label_course_id: "课程ID:",
        label_course_name: "课程名称:",
        label_professor: "任课教师:",
        select_professor: "选择教师",
        label_classroom: "上课教室:",
        select_classroom: "选择教室",
        label_credits: "学分 (可选):",
        label_hours: "学时 (可选):",
        label_type: "课程类型 (可选):",
        option_required: "必修",
        option_elective: "选修",
        btn_add_to_list: "添加到列表",
        btn_generate: "生成课表",
        section_3_title: "3. 查看结果",
        conflicts_title: "冲突信息",
        no_professors: "尚未添加教师。",
        no_classrooms: "尚未添加教室。",
        no_requests: "尚未添加课程请求。",
        msg_logged_in: "登录成功！",
        msg_logged_out: "已登出",
        msg_account_created: "账号创建成功！",
        msg_prof_added: "教师添加成功",
        msg_room_added: "教室添加成功",
        msg_please_add_request: "请至少添加一个课程请求",
        msg_schedule_generated: "课表已生成：共安排 {total} 门课程",
        msg_no_courses: "未安排任何课程。",
        msg_no_conflicts: "✓ 未发现冲突！",
        msg_conflicts_detected: "⚠ 发现 {total} 处冲突：",
        msg_error: "错误：",
        msg_auth_failed: "认证失败",
        msg_network_error: "网络错误：",
        label_period: "节次",
        label_prof: "教师",
        label_room: "教室",
        label_day: "日期",
        monday: "星期一",
        tuesday: "星期二",
        wednesday: "星期三",
        thursday: "星期四",
        friday: "星期五"
    }
};

let currentLang = localStorage.getItem('lang') || 'en';

function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'zh' : 'en';
    localStorage.setItem('lang', currentLang);
    updateLanguage();
}

function updateLanguage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang][key]) {
            el.textContent = translations[currentLang][key];
        }
    });

    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) {
        langBtn.textContent = currentLang === 'en' ? '中文' : 'English';
    }
}

function t(key, params = {}) {
    let text = translations[currentLang][key] || key;
    for (const [k, v] of Object.entries(params)) {
        text = text.replace(`{${k}}`, v);
    }
    return text;
}

function getDayName(dayIndex) {
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
    return t(days[dayIndex - 1]);
}

// ========================================
// AUTH
// ========================================

function getToken() {
    return localStorage.getItem('auth_token');
}

function setToken(token) {
    localStorage.setItem('auth_token', token);
}

function clearToken() {
    localStorage.removeItem('auth_token');
}

function getAuthHeaders() {
    const token = getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function isLoggedIn() {
    return !!getToken();
}

function updateAuthUI() {
    const loggedIn = isLoggedIn();
    document.getElementById('auth-logged-out').style.display = loggedIn ? 'none' : 'block';
    document.getElementById('auth-logged-in').style.display = loggedIn ? 'block' : 'none';

    // Show/hide admin-only content
    document.querySelectorAll('.admin-only').forEach(el => {
        el.style.display = loggedIn ? '' : 'none';
    });

    if (loggedIn) {
        // Get user info
        fetch(`${API_BASE}/auth/me`, { headers: getAuthHeaders() })
            .then(res => res.ok ? res.json() : null)
            .then(data => {
                if (data) {
                    document.getElementById('user-display').textContent = `👤 ${data.username}`;
                }
            });
    }
}

function showLoginModal() {
    document.getElementById('login-modal').style.display = 'flex';
}

function hideLoginModal() {
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('login-form').reset();
}

function toggleSignup() {
    isSignupMode = true;
    document.getElementById('modal-title').textContent = t('signup_title');
    document.getElementById('email-row').style.display = 'block';
    document.getElementById('login-btn').textContent = t('signup_btn_modal');
    document.getElementById('toggle-signup').style.display = 'none';
    document.getElementById('toggle-login').style.display = 'inline';
}

function toggleLogin() {
    isSignupMode = false;
    document.getElementById('modal-title').textContent = t('login_title');
    document.getElementById('email-row').style.display = 'none';
    document.getElementById('login-btn').textContent = t('login_btn_modal');
    document.getElementById('toggle-signup').style.display = 'inline';
    document.getElementById('toggle-login').style.display = 'none';
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const email = document.getElementById('login-email').value;

    try {
        let res;
        if (isSignupMode) {
            res = await fetch(`${API_BASE}/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
                body: JSON.stringify({ username, email, password })
            });
        } else {
            res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });
        }

        if (res.ok) {
            const data = await res.json();
            setToken(data.access_token);
            hideLoginModal();
            updateAuthUI();
            showMessage(isSignupMode ? t('msg_account_created') : t('msg_logged_in'), 'success');
        } else {
            const err = await res.json();
            showMessage(err.detail || t('msg_auth_failed'), 'error');
        }
    } catch (err) {
        showMessage(t('msg_network_error') + err.message, 'error');
    }
}

function logout() {
    clearToken();
    updateAuthUI();
    showMessage(t('msg_logged_out'), 'success');
}

document.getElementById('login-form').addEventListener('submit', handleAuthSubmit);

// ========================================
// PROFESSORS
// ========================================

document.getElementById('add-professor-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const res = await fetch(`${API_BASE}/courses/professors`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({
                id: formData.get('prof_id'),
                name: formData.get('prof_name'),
                department: formData.get('prof_dept') || null,
                title: formData.get('prof_title') || null,
            })
        });

        if (res.ok) {
            showMessage(t('msg_prof_added'), 'success');
            e.target.reset();
            loadProfessors();
        } else {
            const error = await res.json();
            showMessage(t('msg_error') + (error.detail || 'Failed to add professor'), 'error');
        }
    } catch (err) {
        showMessage(t('msg_network_error') + err.message, 'error');
    }
});

async function loadProfessors() {
    try {
        const res = await fetch(`${API_BASE}/courses/professors`);
        const professors = await res.json();

        const listDiv = document.getElementById('professors-list');
        if (professors.length === 0) {
            listDiv.innerHTML = `<p>${t('no_professors')}</p>`;
            return;
        }

        let html = `<table class="list-table"><thead><tr>
            <th>ID</th>
            <th>${t('label_prof_name').replace(':', '')}</th>
            <th>${t('label_dept').replace(' (optional):', '')}</th>
            <th>${t('label_title').replace(' (optional):', '')}</th>
        </tr></thead><tbody>`;
        professors.forEach(prof => {
            html += `<tr><td>${prof.id}</td><td>${prof.name}</td><td>${prof.department || '-'}</td><td>${prof.title || '-'}</td></tr>`;
        });
        html += '</tbody></table>';
        listDiv.innerHTML = html;

        // Also populate the dropdown
        populateProfessorDropdown(professors);
    } catch (err) {
        console.error('Failed to load professors:', err);
    }
}

function populateProfessorDropdown(professors) {
    const dropdown = document.getElementById('course_prof');
    // Clear existing options except the first one
    dropdown.innerHTML = `<option value="">${t('select_professor')}</option>`;

    if (professors.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = t('no_professors');
        option.disabled = true;
        dropdown.appendChild(option);
    } else {
        professors.forEach(prof => {
            const option = document.createElement('option');
            option.value = prof.id;
            option.textContent = `${prof.name} (${prof.id})`;
            dropdown.appendChild(option);
        });
    }
}

// ========================================
// CLASSROOMS
// ========================================

document.getElementById('add-classroom-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const res = await fetch(`${API_BASE}/courses/classrooms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({
                id: formData.get('room_id'),
                name: formData.get('room_name'),
                capacity: parseInt(formData.get('room_capacity'))
            })
        });

        if (res.ok) {
            showMessage(t('msg_room_added'), 'success');
            e.target.reset();
            loadClassrooms();
        } else {
            const error = await res.json();
            showMessage(t('msg_error') + (error.detail || 'Failed to add classroom'), 'error');
        }
    } catch (err) {
        showMessage(t('msg_network_error') + err.message, 'error');
    }
});

async function loadClassrooms() {
    try {
        const res = await fetch(`${API_BASE}/courses/classrooms`);
        const classrooms = await res.json();

        const listDiv = document.getElementById('classrooms-list');
        if (classrooms.length === 0) {
            listDiv.innerHTML = `<p>${t('no_classrooms')}</p>`;
            return;
        }

        let html = `<table class="list-table"><thead><tr>
            <th>ID</th>
            <th>${t('label_room_name').replace(':', '')}</th>
            <th>${t('label_capacity').replace(':', '')}</th>
        </tr></thead><tbody>`;
        classrooms.forEach(room => {
            html += `<tr><td>${room.id}</td><td>${room.name}</td><td>${room.capacity}</td></tr>`;
        });
        html += '</tbody></table>';
        listDiv.innerHTML = html;

        // Also populate the dropdown
        populateClassroomDropdown(classrooms);
    } catch (err) {
        console.error('Failed to load classrooms:', err);
    }
}

function populateClassroomDropdown(classrooms) {
    const dropdown = document.getElementById('course_room');
    // Clear existing options except the first one
    dropdown.innerHTML = `<option value="">${t('select_classroom')}</option>`;

    if (classrooms.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = t('no_classrooms');
        option.disabled = true;
        dropdown.appendChild(option);
    } else {
        classrooms.forEach(room => {
            const option = document.createElement('option');
            option.value = room.id;
            option.textContent = `${room.name} (${room.id})`;
            dropdown.appendChild(option);
        });
    }
}

// ========================================
// COURSE REQUESTS
// ========================================

function addCourseRequest() {
    const form = document.getElementById('add-course-request-form');
    const formData = new FormData(form);

    const request = {
        id: formData.get('course_id'),
        name: formData.get('course_name'),
        professor_id: formData.get('course_prof'),
        classroom_id: formData.get('course_room'),
        credits: formData.get('course_credits') ? parseFloat(formData.get('course_credits')) : null,
        hours: formData.get('course_hours') ? parseInt(formData.get('course_hours')) : null,
        course_type: formData.get('course_type') || null,
        department: formData.get('course_dept') || null,
    };

    courseRequests.push(request);
    form.reset();
    displayCourseRequests();
}

function displayCourseRequests() {
    const listDiv = document.getElementById('course-requests-list');

    if (courseRequests.length === 0) {
        listDiv.innerHTML = `<p>${t('no_requests')}</p>`;
        return;
    }

    let html = `<table class="list-table"><thead><tr>
        <th>${t('label_course_id').replace(':', '')}</th>
        <th>${t('label_course_name').replace(':', '')}</th>
        <th>${t('label_professor').replace(':', '')}</th>
        <th>${t('label_classroom').replace(':', '')}</th>
        <th>Action</th>
    </tr></thead><tbody>`;
    courseRequests.forEach((req, idx) => {
        html += `<tr>
            <td>${req.id}</td>
            <td>${req.name}</td>
            <td>${req.professor_id}</td>
            <td>${req.classroom_id}</td>
            <td><button onclick="removeCourseRequest(${idx})">Remove</button></td>
        </tr>`;
    });
    html += '</tbody></table>';
    listDiv.innerHTML = html;
}

function removeCourseRequest(idx) {
    courseRequests.splice(idx, 1);
    displayCourseRequests();
}

// ========================================
// SCHEDULE GENERATION
// ========================================

async function generateSchedule() {
    if (courseRequests.length === 0) {
        showMessage(t('msg_please_add_request'), 'error');
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/courses/schedules/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({ course_requests: courseRequests })
        });

        if (res.ok) {
            const data = await res.json();
            showMessage(t('msg_schedule_generated', { total: data.total }), 'success');
            displaySchedule(data.courses);
            checkConflicts();
            courseRequests = [];
            displayCourseRequests();
        } else {
            const error = await res.json();
            showMessage(t('msg_error') + (error.detail || 'Failed to generate schedule'), 'error');
        }
    } catch (err) {
        showMessage(t('msg_network_error') + err.message, 'error');
    }
}

function displaySchedule(courses) {
    const displayDiv = document.getElementById('schedule-display');

    if (courses.length === 0) {
        displayDiv.innerHTML = `<p>${t('msg_no_courses')}</p>`;
        return;
    }

    // Create schedule grid
    const periods = [1, 2, 3, 4, 5, 6, 7, 8];

    let html = `<div class="schedule-grid"><table><thead><tr><th>${t('label_period')}</th>`;
    for (let day = 1; day <= 5; day++) {
        html += `<th>${getDayName(day)}</th>`;
    }
    html += '</tr></thead><tbody>';

    periods.forEach(period => {
        html += `<tr><td><strong>P${period}</strong></td>`;
        for (let day = 1; day <= 5; day++) {
            const coursesInSlot = courses.filter(c => c.weekday === day && c.period === period);
            html += '<td>';
            coursesInSlot.forEach(course => {
                html += `<div class="course-item">
                    <strong>${course.id}</strong><br>
                    ${course.name}<br>
                    Prof: ${course.professor_id}<br>
                    Room: ${course.classroom_id}
                </div>`;
            });
            html += '</td>';
        }
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    displayDiv.innerHTML = html;
}

async function checkConflicts() {
    try {
        const res = await fetch(`${API_BASE}/courses/check-conflicts`, {
            method: 'POST'
        });

        const data = await res.json();
        const displayDiv = document.getElementById('conflicts-display');

        const totalConflicts = data.professor_conflicts + data.classroom_conflicts;

        if (totalConflicts === 0) {
            displayDiv.innerHTML = `<p><strong>${t('msg_no_conflicts')}</strong></p>`;
            return;
        }

        let html = `<p><strong>${t('msg_conflicts_detected', { total: totalConflicts })}</strong></p>`;

        if (data.professor_conflicts > 0) {
            html += `<div class="conflict-item"><strong>${t('label_prof')} ${t('conflicts_title')}:</strong><ul>`;
            data.details.professor_conflicts.forEach(c => {
                html += `<li>${c.course_a.id} & ${c.course_b.id} - ${t('label_prof')} ${c.professor_id} double-booked</li>`;
            });
            html += '</ul></div>';
        }

        if (data.classroom_conflicts > 0) {
            html += `<div class="conflict-item"><strong>${t('label_room')} ${t('conflicts_title')}:</strong><ul>`;
            data.details.classroom_conflicts.forEach(c => {
                html += `<li>${c.course_a.id} & ${c.course_b.id} - ${t('label_room')} ${c.classroom_id} double-booked</li>`;
            });
            html += '</ul></div>';
        }

        displayDiv.innerHTML = html;
    } catch (err) {
        console.error('Failed to check conflicts:', err);
    }
}

// ========================================
// UTILITIES
// ========================================

function showMessage(text, type = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;

    document.querySelector('main').insertBefore(messageDiv, document.querySelector('main').firstChild);

    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}



// ========================================
// SCHEDULE VIEWS
// ========================================

function changeView() {
    const viewType = document.getElementById('view-type').value;
    const entitySelect = document.getElementById('view-entity');
    const loadBtn = document.getElementById('load-view-btn');

    if (viewType === 'weekly') {
        entitySelect.style.display = 'none';
        loadBtn.style.display = 'none';
        loadWeeklyView();
    } else {
        entitySelect.style.display = 'inline';
        loadBtn.style.display = 'inline';
        populateEntityDropdown(viewType);
    }
}

async function populateEntityDropdown(viewType) {
    const entitySelect = document.getElementById('view-entity');
    const endpoint = viewType === 'professor' ? '/courses/professors' : '/courses/classrooms';

    try {
        const res = await fetch(`${API_BASE}${endpoint}`);
        const items = await res.json();

        entitySelect.innerHTML = `<option value="">${t('option_select')}</option>`;
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = `${item.name} (${item.id})`;
            entitySelect.appendChild(option);
        });
    } catch (err) {
        console.error('Failed to load entities:', err);
    }
}

async function loadSelectedView() {
    const viewType = document.getElementById('view-type').value;
    const entityId = document.getElementById('view-entity').value;

    if (!entityId) {
        showMessage(t('option_select'), 'error');
        return;
    }

    try {
        const endpoint = `/courses/schedules/${viewType}/${entityId}`;
        const res = await fetch(`${API_BASE}${endpoint}`);

        if (res.ok) {
            const data = await res.json();
            displayEntitySchedule(data, viewType);
        } else {
            const error = await res.json();
            showMessage(t('msg_error') + (error.detail || 'Failed to load schedule'), 'error');
        }
    } catch (err) {
        showMessage(t('msg_network_error') + err.message, 'error');
    }
}

function displayEntitySchedule(data, viewType) {
    const displayDiv = document.getElementById('schedule-display');
    const entity = data.professor || data.classroom;
    const entityType = viewType === 'professor' ? t('label_prof') : t('label_room');

    let html = `<h3>${entityType}: ${entity.name}</h3>`;

    if (data.courses.length === 0) {
        html += `<p>${t('msg_no_courses')}</p>`;
    } else {
        html += '<table class="list-table"><thead><tr>';
        html += `<th>${t('label_course_id').replace(':', '')}</th>
                 <th>${t('label_course_name').replace(':', '')}</th>
                 <th>${t('label_day')}</th>
                 <th>${t('label_period')}</th>`;
        if (viewType === 'professor') {
            html += `<th>${t('label_room')}</th>`;
        } else {
            html += `<th>${t('label_prof')}</th>`;
        }
        html += '</tr></thead><tbody>';

        data.courses.forEach(course => {
            html += `<tr>
                <td>${course.id}</td>
                <td>${course.name}</td>
                <td>${getDayName(course.weekday)}</td>
                <td>${course.period}</td>
                <td>${viewType === 'professor' ? course.classroom_id : course.professor_id}</td>
            </tr>`;
        });

        html += '</tbody></table>';
        html += `<p><strong>Total: ${data.total}</strong></p>`;
    }

    displayDiv.innerHTML = html;
}

async function loadWeeklyView() {
    try {
        const res = await fetch(`${API_BASE}/courses/schedules/weekly`);

        if (res.ok) {
            const data = await res.json();
            displayWeeklyGrid(data);
        } else {
            const error = await res.json();
            showMessage(t('msg_error') + (error.detail || 'Failed to load schedule'), 'error');
        }
    } catch (err) {
        showMessage(t('msg_network_error') + err.message, 'error');
    }
}

function displayWeeklyGrid(data) {
    const displayDiv = document.getElementById('schedule-display');

    if (data.total_courses === 0) {
        displayDiv.innerHTML = `<p>${t('msg_no_courses')}</p>`;
        return;
    }

    let html = `<div class="schedule-grid"><table><thead><tr><th>${t('label_period')}</th>`;
    for (let day = 1; day <= 5; day++) {
        html += `<th>${getDayName(day)}</th>`;
    }
    html += '</tr></thead><tbody>';

    for (let period = 1; period <= 12; period++) {
        html += `<tr><td><strong>P${period}</strong></td>`;
        for (let day = 1; day <= 5; day++) {
            const coursesInSlot = data.grid[day][period];
            html += '<td>';
            coursesInSlot.forEach(course => {
                html += `<div class="course-item">
                    <strong>${course.id}</strong><br>
                    ${course.name}<br>
                    ${t('label_prof')}: ${course.professor_id}<br>
                    ${t('label_room')}: ${course.classroom_id}
                </div>`;
            });
            html += '</td>';
        }
        html += '</tr>';
    }

    html += '</tbody></table></div>';
    html += `<p><strong>Total: ${data.total_courses}</strong></p>`;
    displayDiv.innerHTML = html;
}



// ========================================
// FILE EXPORT
// ========================================

function exportPDF() {
    window.location.href = `${API_BASE}/courses/export/schedule/pdf`;
    showMessage('Downloading PDF...', 'success');
}

function exportExcel() {
    window.location.href = `${API_BASE}/courses/export/schedule/excel`;
    showMessage('Downloading Excel file...', 'success');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateLanguage();
    updateAuthUI();
    loadProfessors();
    loadClassrooms();
    loadWeeklyView();
});
