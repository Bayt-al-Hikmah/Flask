
const API_BASE = '/api';

function switchView(viewId) {
 
    document.getElementById('login-view').style.display = 'none';
    document.getElementById('register-view').style.display = 'none';
    document.getElementById('app-view').style.display = 'none';
    const targetView = document.getElementById(viewId);
    if (targetView) {
        targetView.style.display = 'block';
    }
}

function displayMessage(elementId, message, isError = false) {
    const msgElement = document.getElementById(elementId);
    msgElement.innerText = message;
    msgElement.style.color = isError ? '#dc3545' : '#28a745';
}


document.addEventListener('DOMContentLoaded', () => {
     const token = localStorage.getItem('token');
    if (token) {
        fetchUserProfile(false);
    } else {
        switchView('login-view');
    }
});

function showRegister() {
    switchView('register-view');
    displayMessage('register-message', '');
}

function showLogin() {
    switchView('login-view');
    displayMessage('login-message', ''); 
}


document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    displayMessage('register-message', 'Registering...', false);

    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const avatar = document.getElementById('reg-avatar-url').value;

    const response = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, avatar })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('register-message', data.message, false);
        document.getElementById('register-form').reset();
        setTimeout(showLogin, 2000); 
    } else {
        displayMessage('register-message', data.message || "Registration failed.", true);
    }
});


document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    displayMessage('login-message', 'Logging in...', false);

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('login-message', data.message, false);
        document.getElementById('login-form').reset();
        localStorage.setItem('token', data.access_token);
        switchView('app-view');
        showTasks(); 
        fetchUserProfile(true); 
    } else {
        displayMessage('login-message', data.message || "Invalid email or password.", true);
    }
});



function showTasks() {
    document.getElementById('tasks-section').style.display = 'block';
    document.getElementById('profile-section').style.display = 'none';
    document.getElementById('btn-tasks').classList.add('active');
    document.getElementById('btn-profile').classList.remove('active');
    fetchTasks();
}

function showProfile() {
    document.getElementById('tasks-section').style.display = 'none';
    document.getElementById('profile-section').style.display = 'block';
    document.getElementById('btn-profile').classList.add('active');
    document.getElementById('btn-tasks').classList.remove('active');
    fetchUserProfile(true); 
    displayMessage('profile-message', '');
}


async function fetchUserProfile(populateForm) {
    const token = localStorage.getItem('token');
    console.log(token)
    const response = await fetch(`${API_BASE}/user`,
        
        {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        }
    );

    if (response.status === 401) {
        switchView('login-view');
        return;
    }

    console.log("User profile response status:", response);

    if (response.ok) {
        const user = await response.json();
        document.getElementById('nav-username').innerText = user.username;
        const avatarUrl = user.avatar || 'https://via.placeholder.com/32?text=U';
        document.getElementById('nav-avatar').src = avatarUrl;
        
        if (!populateForm) {
            switchView('app-view');
            showTasks();
        }

        if (populateForm) {
            document.getElementById('profile-username').value = user.username;
            document.getElementById('profile-email').value = user.email;
            document.getElementById('profile-avatar').value = user.avatar;
            document.getElementById('profile-avatar-preview').src = avatarUrl;
        }
    } else {
        switchView('login-view');
    }
}

async function updateProfile() {
    displayMessage('profile-message', 'Saving profile...', false);
    
    const username = document.getElementById('profile-username').value;
    const email = document.getElementById('profile-email').value;
    const avatar = document.getElementById('profile-avatar').value;
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}/user`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' ,
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ username, email, avatar })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('profile-message', data.message, false);
        fetchUserProfile(true); // Refresh data
    } else {
        displayMessage('profile-message', data.message || "Failed to update profile.", true);
    }
}

async function updatePassword() {
    displayMessage('profile-message', 'Changing password...', false);
    
    const password = document.getElementById('profile-password').value;

    if (!password) {
        displayMessage('profile-message', 'Please enter a new password.', true);
        return;
    }
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}/user`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' ,  'Authorization': `Bearer ${token}`},
        body: JSON.stringify({ password })
    });

    const data = await response.json();

    if (response.ok) {
        displayMessage('profile-message', data.message, false);
        document.getElementById('profile-password').value = ''; // Clear field
    } else {
        displayMessage('profile-message', data.message || "Failed to change password.", true);
    }
}

async function fetchTasks() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE}/tasks`,
        {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        }
    );
    
    if (response.status === 401) return logout(); 
    
    const tasks = await response.json();
    const list = document.getElementById('task-list');
    list.innerHTML = ''; 

    if (tasks.length === 0) {
        list.innerHTML = '<li style="justify-content: center; color: #888;">No tasks yet! Add one above.</li>';
        return;
    }

    tasks.forEach(task => {
        const isDone = task.state === 'done';
        const li = document.createElement('li');
        li.className = isDone ? 'task-done' : '';

        const taskNameSpan = document.createElement('span');
        taskNameSpan.innerText = `${task.name} (${task.state})`;
        

        const toggleBtn = document.createElement('button');
        toggleBtn.innerText = isDone ? 'Reactivate' : 'Mark Done';
        toggleBtn.className = isDone ? 'delete-btn' : 'toggle-btn';
        toggleBtn.onclick = () => updateTaskState(task.id, isDone ? 'active' : 'done');

      
        const deleteBtn = document.createElement('button');
        deleteBtn.innerText = 'Delete';
        deleteBtn.className = 'delete-btn';
        deleteBtn.onclick = () => deleteTask(task.id);

        li.appendChild(taskNameSpan);
        li.appendChild(toggleBtn);
        li.appendChild(deleteBtn);
        list.appendChild(li);
    });
}

// --- Create (POST) Task ---
async function createTask() {
    const nameInput = document.getElementById('task-name');
    const name = nameInput.value.trim();
    if (!name) return;
    const token = localStorage.getItem('token');
    await fetch(`${API_BASE}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
         },
        body: JSON.stringify({ name: name })
    });

    nameInput.value = ''; 
    fetchTasks(); 
}


async function updateTaskState(taskId, newState) {
    const token = localStorage.getItem('token');
    await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' ,
              'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ state: newState }) 
    });
    fetchTasks(); 
}

// --- Delete (DELETE) Task ---
async function deleteTask(taskId) {
    if(!confirm("Are you sure you want to delete this task?")) return;
    const token = localStorage.getItem('token');
    await fetch(`${API_BASE}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' ,
              'Authorization': `Bearer ${token}`
        },
    });
    fetchTasks(); 
}
