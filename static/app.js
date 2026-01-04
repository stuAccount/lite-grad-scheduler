// API base URL
const API_BASE = window.location.origin;

// State
let courseRequests = [];

// ========================================
// PROFESSORS
// ========================================

document.getElementById('add-professor-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const res = await fetch(`${API_BASE}/courses/professors`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: formData.get('prof_id'),
                name: formData.get('prof_name')
            })
        });

        if (res.ok) {
            showMessage('Professor added successfully', 'success');
            e.target.reset();
            loadProfessors();
        } else {
            const error = await res.json();
            showMessage('Error: ' + (error.detail || 'Failed to add professor'), 'error');
        }
    } catch (err) {
        showMessage('Network error: ' + err.message, 'error');
    }
});

async function loadProfessors() {
    try {
        const res = await fetch(`${API_BASE}/courses/professors`);
        const professors = await res.json();

        const listDiv = document.getElementById('professors-list');
        if (professors.length === 0) {
            listDiv.innerHTML = '<p>No professors added yet.</p>';
            return;
        }

        let html = '<table class="list-table"><thead><tr><th>ID</th><th>Name</th></tr></thead><tbody>';
        professors.forEach(prof => {
            html += `<tr><td>${prof.id}</td><td>${prof.name}</td></tr>`;
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
    dropdown.innerHTML = '<option value="">Select Professor</option>';

    if (professors.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No professors available';
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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: formData.get('room_id'),
                name: formData.get('room_name'),
                capacity: parseInt(formData.get('room_capacity'))
            })
        });

        if (res.ok) {
            showMessage('Classroom added successfully', 'success');
            e.target.reset();
            loadClassrooms();
        } else {
            const error = await res.json();
            showMessage('Error: ' + (error.detail || 'Failed to add classroom'), 'error');
        }
    } catch (err) {
        showMessage('Network error: ' + err.message, 'error');
    }
});

async function loadClassrooms() {
    try {
        const res = await fetch(`${API_BASE}/courses/classrooms`);
        const classrooms = await res.json();

        const listDiv = document.getElementById('classrooms-list');
        if (classrooms.length === 0) {
            listDiv.innerHTML = '<p>No classrooms added yet.</p>';
            return;
        }

        let html = '<table class="list-table"><thead><tr><th>ID</th><th>Name</th><th>Capacity</th></tr></thead><tbody>';
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
    dropdown.innerHTML = '<option value="">Select Classroom</option>';

    if (classrooms.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'No classrooms available';
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
        classroom_id: formData.get('course_room')
    };

    courseRequests.push(request);
    form.reset();
    displayCourseRequests();
}

function displayCourseRequests() {
    const listDiv = document.getElementById('course-requests-list');

    if (courseRequests.length === 0) {
        listDiv.innerHTML = '<p>No course requests added yet.</p>';
        return;
    }

    let html = '<table class="list-table"><thead><tr><th>Course ID</th><th>Name</th><th>Professor</th><th>Classroom</th><th>Action</th></tr></thead><tbody>';
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
        showMessage('Please add at least one course request', 'error');
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/courses/schedules/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ course_requests: courseRequests })
        });

        if (res.ok) {
            const data = await res.json();
            showMessage(`Schedule generated: ${data.total} courses scheduled`, 'success');
            displaySchedule(data.courses);
            checkConflicts();
            courseRequests = [];
            displayCourseRequests();
        } else {
            const error = await res.json();
            showMessage('Error: ' + (error.detail || 'Failed to generate schedule'), 'error');
        }
    } catch (err) {
        showMessage('Network error: ' + err.message, 'error');
    }
}

function displaySchedule(courses) {
    const displayDiv = document.getElementById('schedule-display');

    if (courses.length === 0) {
        displayDiv.innerHTML = '<p>No courses scheduled.</p>';
        return;
    }

    // Create schedule grid
    const weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const periods = [1, 2, 3, 4, 5, 6, 7, 8];

    let html = '<div class="schedule-grid"><table><thead><tr><th>Period</th>';
    weekdays.forEach(day => {
        html += `<th>${day}</th>`;
    });
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
            displayDiv.innerHTML = '<p><strong>✓ No conflicts detected!</strong></p>';
            return;
        }

        let html = `<p><strong>⚠ ${totalConflicts} conflict(s) detected:</strong></p>`;

        if (data.professor_conflicts > 0) {
            html += '<div class="conflict-item"><strong>Professor Conflicts:</strong><ul>';
            data.details.professor_conflicts.forEach(c => {
                html += `<li>${c.course_a.id} and ${c.course_b.id} - Professor ${c.professor_id} double-booked</li>`;
            });
            html += '</ul></div>';
        }

        if (data.classroom_conflicts > 0) {
            html += '<div class="conflict-item"><strong>Classroom Conflicts:</strong><ul>';
            data.details.classroom_conflicts.forEach(c => {
                html += `<li>${c.course_a.id} and ${c.course_b.id} - Classroom ${c.classroom_id} double-booked</li>`;
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
// INIT
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    loadProfessors();
    loadClassrooms();
});
