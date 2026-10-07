const API_URL = 'http://127.0.0.1:8000';

// State
let token = localStorage.getItem('access_token');
let currentAuthMode = 'login'; 
let tasks = [];
let currentFilter = 'all'; // all, active, completed
let currentTheme = localStorage.getItem('theme') || 'dark';

// Theme Logic
function initTheme() {
    document.documentElement.className = currentTheme;
    updateThemeIcon();
}

function toggleTheme() {
    currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', currentTheme);
    document.documentElement.className = currentTheme;
    updateThemeIcon();
}

function updateThemeIcon() {
    const iconEl = document.querySelector('#theme-toggle i');
    if (iconEl) {
        iconEl.setAttribute('data-lucide', currentTheme === 'dark' ? 'sun' : 'moon');
        lucide.createIcons();
    }
}

// DOM
const views = { auth: document.getElementById('auth-view'), dashboard: document.getElementById('dashboard-view') };
const authSubmitBtn = document.getElementById('auth-submit-btn');
const authError = document.getElementById('auth-error');
const taskListEl = document.getElementById('task-list');
const editModal = document.getElementById('edit-modal');
const loadingEl = document.getElementById('task-list-loading');
const emptyStateEl = document.getElementById('empty-state');
const currentViewTitle = document.getElementById('current-view-title');

// Initialize Lucide Icons
lucide.createIcons();

// Boot
function init() {
    initTheme();
    if (token) {
        showDashboard();
    } else {
        showAuth();
    }
    
    // Open Shutter
    setTimeout(() => {
        const shutter = document.getElementById('shutter-overlay');
        if (shutter) {
            shutter.classList.add('open');
            setTimeout(() => shutter.remove(), 1000);
        }
    }, 800);
}

// UI Nav
function showAuth() {
    views.auth.classList.remove('hidden');
    views.dashboard.classList.add('hidden');
}

function showDashboard() {
    views.auth.classList.add('hidden');
    views.dashboard.classList.remove('hidden');
    setGreeting();
    fetchTasks();
}

function switchAuthTab(mode) {
    currentAuthMode = mode;
    document.getElementById('tab-login').classList.toggle('active', mode === 'login');
    document.getElementById('tab-register').classList.toggle('active', mode === 'register');
    
    document.getElementById('auth-title').textContent = mode === 'login' ? 'Welcome Back' : 'Create Account';
    document.getElementById('auth-subtitle').textContent = mode === 'login' ? 'Enter your credentials to continue.' : 'Sign up to start organizing your life.';
    
    authSubmitBtn.querySelector('span').textContent = mode === 'login' ? 'Sign In' : 'Sign Up';
    authError.classList.add('hidden');
}

function togglePasswordVisibility() {
    const input = document.getElementById('password');
    const eye = document.getElementById('password-eye');
    if (input.type === 'password') {
        input.type = 'text';
        eye.setAttribute('data-lucide', 'eye-off');
    } else {
        input.type = 'password';
        eye.setAttribute('data-lucide', 'eye');
    }
    lucide.createIcons();
}

// Toast Notifications
function showToast(message, type = 'default') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast`;
    
    let icon = 'info';
    if(type === 'success') icon = 'check-circle';
    if(type === 'error') icon = 'alert-circle';
    
    toast.innerHTML = `
        <i data-lucide="${icon}" class="text-${type === 'error' ? 'danger' : (type === 'success' ? 'success' : 'accent')}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    lucide.createIcons();
    
    setTimeout(() => {
        toast.classList.add('hiding');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}

// Auth Logic
async function handleAuth(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const btnSpan = authSubmitBtn.querySelector('span');
    const originalText = btnSpan.textContent;

    authSubmitBtn.disabled = true;
    btnSpan.textContent = 'Processing...';
    authError.classList.add('hidden');

    try {
        if (currentAuthMode === 'login') {
            await login(username, password);
        } else {
            await register(username, password);
            await login(username, password);
        }
    } catch (err) {
        authError.innerHTML = `<i data-lucide="alert-triangle"></i> ${escapeHtml(err.message)}`;
        lucide.createIcons();
        authError.classList.remove('hidden');
    } finally {
        authSubmitBtn.disabled = false;
        btnSpan.textContent = originalText;
    }
}

// This function sends the user's login details to the backend using form data,
// and stores the returned JWT so protected API requests can use it.
async function login(username, password) {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    const res = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');
    
    token = data.access_token;
    localStorage.setItem('access_token', token);
    document.getElementById('auth-form').reset();
    showToast('Logged in successfully', 'success');
    showDashboard();
}

async function register(username, password) {
    const res = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');
}

function logout() {
    token = null;
    localStorage.removeItem('access_token');
    showToast('Logged out');
    showAuth();
}

// API Fetch Helper
// This helper adds the JWT to requests that require authentication.
// It intercepts 401 (Unauthorized) responses to automatically log the user out.
async function apiFetch(endpoint, options = {}) {
    if (!token) { logout(); throw new Error('Not authenticated'); }
    const headers = { 'Authorization': `Bearer ${token}`, ...options.headers };
    const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
    
    if (res.status === 401) { logout(); throw new Error('Session expired'); }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'API Error');
    return data;
}

// Tasks & Gamification
function setGreeting() {
    const hour = new Date().getHours();
    const greetEl = document.getElementById('user-greeting');
    if (hour < 12) greetEl.textContent = 'Good morning.';
    else if (hour < 18) greetEl.textContent = 'Good afternoon.';
    else greetEl.textContent = 'Good evening.';
}

function updateStats() {
    const completedTasks = tasks.filter(t => t.completed);
    const activeTasks = tasks.filter(t => !t.completed);
    
    // Stats
    document.getElementById('stat-total').textContent = tasks.length;
    document.getElementById('stat-active').textContent = activeTasks.length;
    document.getElementById('stat-completed').textContent = completedTasks.length;
}

function setFilter(filter) {
    currentFilter = filter;
    
    // Update active nav class
    document.querySelectorAll('.nav-item').forEach(btn => {
        if(btn.dataset.filter) {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        }
    });
    
    const titles = { 'all': 'Tasks', 'active': 'Active Tasks', 'completed': 'Completed Tasks' };
    currentViewTitle.textContent = titles[filter];
    
    renderTasks();
}

async function fetchTasks() {
    loadingEl.classList.remove('hidden');
    taskListEl.innerHTML = '';
    emptyStateEl.classList.add('hidden');
    
    try {
        const rawTasks = await apiFetch('/tasks');
        // The backend returns task objects, so we map them directly using named properties
        // such as t.title instead of relying on array positions.
        tasks = rawTasks.map(t => ({ id: t.id, title: t.title, description: t.description, completed: t.completed, user_id: t.user_id }));
        updateStats();
        renderTasks();
    } catch (err) {
        if(token) showToast('Failed to fetch tasks: ' + err.message, 'error');
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// This function renders the user's tasks to the DOM.
// We access explicit properties like task.title to build the HTML safely.
function renderTasks(options = {}) {
    taskListEl.innerHTML = '';
    
    let filtered = tasks;
    if (currentFilter === 'active') filtered = tasks.filter(t => !t.completed);
    if (currentFilter === 'completed') filtered = tasks.filter(t => t.completed);
    
    if (filtered.length === 0) {
        emptyStateEl.classList.remove('hidden');
        return;
    } else {
        emptyStateEl.classList.add('hidden');
    }

    const sorted = [...filtered].sort((a, b) => {
        if (a.completed === b.completed) return b.id - a.id;
        return a.completed ? 1 : -1;
    });

    sorted.forEach((task, index) => {
        const li = document.createElement('li');
        li.className = `task-item ${task.completed ? 'completed' : ''}`;
        li.setAttribute('data-task-id', task.id);
        if (options.animateNew === task.id) {
            li.classList.add('new-item');
        } else if (options.noAnimate) {
            li.style.animation = 'none';
        } else {
            li.style.animationDelay = `${index * 0.05}s`;
        }
        
        li.innerHTML = `
            <div class="task-serial">#${index + 1}</div>
            <div class="task-content" style="cursor: pointer;" onclick="openViewModal(${task.id})">
                <div class="task-title" title="${escapeHtml(task.title)}">
                    <span class="task-title-text">${escapeHtml(task.title)}</span>
                    ${task.completed ? `<span class="status-badge status-completed">(completed)</span>` : `<span class="status-badge status-pending">(pending)</span>`}
                </div>
                ${task.description ? `<div class="task-desc" title="${escapeHtml(task.description)}">${escapeHtml(task.description)}</div>` : ''}
            </div>
            <div class="task-actions">
                ${!task.completed ? 
                    `<button class="btn-icon text-success" onclick="markComplete(${task.id})" title="Mark Complete"><i data-lucide="check"></i></button>
                     <button class="btn-icon text-success" onclick="markComplete(${task.id}, true)" title="Complete & Delete"><i data-lucide="check-check"></i></button>` : 
                    `<button class="btn-icon text-secondary" onclick="markIncomplete(${task.id})" title="Reopen"><i data-lucide="rotate-ccw"></i></button>`
                }
                <button class="btn-icon" onclick="openEditModal(${task.id})" title="Edit"><i data-lucide="edit-2"></i></button>
                <button class="btn-icon text-danger" onclick="deleteTask(${task.id})" title="Delete"><i data-lucide="trash-2"></i></button>
            </div>
        `;
        taskListEl.appendChild(li);
    });
    
    lucide.createIcons();
}

async function handleCreateTask(e) {
    e.preventDefault();
    const titleInput = document.getElementById('task-title');
    const descInput = document.getElementById('task-desc');
    const btn = e.target.querySelector('button');

    if (!titleInput.value.trim() || !descInput.value.trim()) {
        showToast('Title and description are required', 'error');
        return;
    }

    btn.disabled = true;
    try {
        // Send a POST request to create the task. The API contract expects title, description, and completed status.
        const rawTask = await apiFetch('/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: titleInput.value, description: descInput.value, completed: false })
        });
        
        tasks.unshift({ id: rawTask.id, title: rawTask.title, description: rawTask.description, completed: rawTask.completed, user_id: rawTask.user_id });
        
        titleInput.value = '';
        descInput.value = '';
        descInput.style.height = '1.5rem';
        updateStats();
        requestAnimationFrame(() => {
            renderTasks({ animateNew: rawTask.id });
        });
        showToast('Task created', 'success');
    } catch (err) {
        showToast('Failed to create task', 'error');
    } finally {
        btn.disabled = false;
    }
}

async function markComplete(id, shouldDelete = false, skipConfirm = false) {
    if (shouldDelete && !skipConfirm) {
        openConfirmModal(() => markComplete(id, true, true));
        return;
    }

    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    const origCompleted = task.completed;
    task.completed = true;
    
    try {
        await apiFetch(`/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: task.title, description: task.description, completed: true })
        });
        
        fireConfetti();
        updateStats();
        renderTasks({ noAnimate: true });
        showToast('Task marked completed', 'success');
        
        if (shouldDelete) {
            setTimeout(async () => {
                await deleteTask(id, true);
            }, 500);
        }
    } catch (err) {
        task.completed = origCompleted;
        updateStats();
        renderTasks({ noAnimate: true });
        showToast('Failed to complete task', 'error');
    }
}

async function markIncomplete(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    const origCompleted = task.completed;
    task.completed = false;
    
    try {
        await apiFetch(`/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: task.title, description: task.description, completed: false })
        });
        
        updateStats();
        renderTasks({ noAnimate: true });
        showToast('Task reopened', 'success');
    } catch (err) {
        task.completed = origCompleted;
        updateStats();
        renderTasks({ noAnimate: true });
        showToast('Failed to reopen task', 'error');
    }
}

let confirmAction = null;

function openConfirmModal(action) {
    confirmAction = action;
    document.getElementById('confirm-modal').classList.remove('hidden');
}

function closeConfirmModal() {
    confirmAction = null;
    document.getElementById('confirm-modal').classList.add('hidden');
}

document.getElementById('confirm-btn').addEventListener('click', async () => {
    if (confirmAction !== null) {
        const action = confirmAction;
        closeConfirmModal();
        await action();
    }
});

async function deleteTask(id, skipConfirm = false) {
    if (!skipConfirm) {
        openConfirmModal(() => executeDelete(id, false));
        return;
    }
    await executeDelete(id, true);
}

async function executeDelete(id, skipConfirm) {
    try {
        await apiFetch(`/tasks/${id}`, { method: 'DELETE' });
        
        const taskElement = document.querySelector(`li[data-task-id="${id}"]`);
        if (taskElement) {
            taskElement.classList.add('deleting');
            await new Promise(resolve => setTimeout(resolve, 400));
        }
        
        tasks = tasks.filter(t => t.id !== id);
        updateStats();
        renderTasks({ noAnimate: true });
        if(!skipConfirm) showToast('Task deleted');
    } catch (err) {
        showToast('Failed to delete task', 'error');
    }
}

// View Flow
function openViewModal(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    document.getElementById('view-task-title').textContent = task.title;
    document.getElementById('view-task-desc').textContent = task.description || 'No description provided.';
    
    const actionsContainer = document.getElementById('view-task-actions');
    actionsContainer.innerHTML = `
        ${!task.completed ? 
            `<button class="btn btn-ghost text-success" onclick="closeViewModal(); markComplete(${task.id})" title="Mark Complete"><i data-lucide="check"></i> Complete</button>` : 
            `<button class="btn btn-ghost text-secondary" onclick="closeViewModal(); markIncomplete(${task.id})" title="Reopen"><i data-lucide="rotate-ccw"></i> Reopen</button>`
        }
        <button class="btn btn-ghost" onclick="closeViewModal(); openEditModal(${task.id})" title="Edit"><i data-lucide="edit-2"></i> Edit</button>
        <button class="btn btn-ghost text-danger" onclick="closeViewModal(); deleteTask(${task.id})" title="Delete"><i data-lucide="trash-2"></i> Delete</button>
    `;
    
    document.getElementById('view-modal').classList.remove('hidden');
    lucide.createIcons();
}

function closeViewModal() {
    document.getElementById('view-modal').classList.add('hidden');
}

// Edit Flow
function openEditModal(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;
    
    document.getElementById('edit-task-id').value = task.id;
    document.getElementById('edit-task-title').value = task.title;
    document.getElementById('edit-task-desc').value = task.description || '';
    
    editModal.classList.remove('hidden');
}

function closeEditModal() { editModal.classList.add('hidden'); }

async function handleUpdateTask(e) {
    e.preventDefault();
    const id = parseInt(document.getElementById('edit-task-id').value);
    const title = document.getElementById('edit-task-title').value;
    const desc = document.getElementById('edit-task-desc').value;
    
    const task = tasks.find(t => t.id === id);
    if(!task) return;

    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    
    try {
        const rawTask = await apiFetch(`/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description: desc, completed: task.completed })
        });
        
        task.title = rawTask.title;
        task.description = rawTask.description;
        
        renderTasks({ noAnimate: true });
        closeEditModal();
        showToast('Task updated', 'success');
    } catch (err) {
        showToast('Update failed', 'error');
    } finally {
        btn.disabled = false;
    }
}

// Simple Confetti Gamification (Lightweight Canvas Implementation)
let confettiAnimationId = null;

function fireConfetti() {
    const canvas = document.getElementById('confetti-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    if (confettiAnimationId) {
        cancelAnimationFrame(confettiAnimationId);
    }
    
    const particles = [];
    const colors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];
    
    for (let i = 0; i < 50; i++) {
        particles.push({
            x: canvas.width / 2,
            y: canvas.height / 2 + 100,
            r: Math.random() * 6 + 2,
            dx: Math.random() * 10 - 5,
            dy: Math.random() * -10 - 5,
            color: colors[Math.floor(Math.random() * colors.length)],
            tilt: Math.floor(Math.random() * 10) - 10,
            tiltAngle: 0,
            tiltAngleInc: (Math.random() * 0.07) + 0.05
        });
    }
    
    function render() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let active = false;
        
        for (let i = 0; i < particles.length; i++) {
            const p = particles[i];
            p.tiltAngle += p.tiltAngleInc;
            p.y += (Math.cos(p.tiltAngle) + 1 + p.r / 2) / 2;
            p.x += Math.sin(p.tiltAngle) * 2;
            p.dy += 0.1; // gravity
            p.x += p.dx;
            p.y += p.dy;
            
            if (p.y <= canvas.height) active = true;
            
            ctx.beginPath();
            ctx.lineWidth = p.r;
            ctx.strokeStyle = p.color;
            ctx.moveTo(p.x + p.tilt + p.r, p.y);
            ctx.lineTo(p.x + p.tilt, p.y + p.tilt + p.r);
            ctx.stroke();
        }
        
        if (active) {
            confettiAnimationId = requestAnimationFrame(render);
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            confettiAnimationId = null;
        }
    }
    render();
}

document.addEventListener('visibilitychange', () => {
    if (document.hidden && confettiAnimationId) {
        cancelAnimationFrame(confettiAnimationId);
        confettiAnimationId = null;
        const canvas = document.getElementById('confetti-canvas');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }
});

// Utils
function escapeHtml(unsafe) {
    return (unsafe || '').toString()
         .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

init();

document.addEventListener('DOMContentLoaded', () => {
    const taskDescInput = document.getElementById('task-desc');
    if (taskDescInput) {
        taskDescInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                if (e.shiftKey) {
                    e.preventDefault();
                    const start = this.selectionStart;
                    const end = this.selectionEnd;
                    this.value = this.value.substring(0, start) + '\n' + this.value.substring(end);
                    this.selectionStart = this.selectionEnd = start + 1;
                    this.dispatchEvent(new Event('input'));
                } else {
                    e.preventDefault();
                    if (typeof document.getElementById('task-form').requestSubmit === 'function') {
                        document.getElementById('task-form').requestSubmit();
                    } else {
                        document.getElementById('task-form').dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                    }
                }
            }
        });
        
        taskDescInput.addEventListener('input', function() {
            this.style.height = 'auto';
            if (this.value) {
                this.style.height = (this.scrollHeight) + 'px';
            } else {
                this.style.height = '1.5rem';
            }
        });
    }
});
