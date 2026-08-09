// Global variables
let userType = null;
let userId = null;

// Show Login Modal
function showLoginModal(type) {
    userType = type;
    document.getElementById('loginModal').style.display = 'block';
}

// Show Register Modal
function showRegisterModal(type) {
    userType = type;
    const patientFields = document.getElementById('patientFields');
    const doctorFields = document.getElementById('doctorFields');
    
    patientFields.style.display = type === 'patient' ? 'flex' : 'none';
    doctorFields.style.display = type === 'doctor' ? 'flex' : 'none';
    
    if (patientFields.style.display === 'flex') {
        patientFields.style.flexDirection = 'column';
    }
    if (doctorFields.style.display === 'flex') {
        doctorFields.style.flexDirection = 'column';
    }
    
    document.getElementById('registerModal').style.display = 'block';
}

// Close Modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        // Simulate login (in production, make API call)
        localStorage.setItem('userEmail', email);
        localStorage.setItem('userType', userType);
        
        alert(`Login successful! Welcome ${email}`);
        closeModal('loginModal');
        window.location.href = '/dashboard';
    } catch (error) {
        alert('Login failed. Please try again.');
        console.error('Login error:', error);
    }
}

// Handle Register
async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const phone = document.getElementById('regPhone').value;
    
    let endpoint, data;
    
    if (userType === 'patient') {
        const age = document.getElementById('regAge').value;
        const address = document.getElementById('regAddress').value;
        
        endpoint = '/api/patients/register';
        data = { name, email, password, phone, age: parseInt(age), address };
    } else {
        const specialization = document.getElementById('regSpecialization').value;
        
        endpoint = '/api/doctors/register';
        data = { name, email, password, phone, specialization };
    }
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            localStorage.setItem('userEmail', email);
            localStorage.setItem('userType', userType);
            localStorage.setItem(`${userType}Id`, result.id);
            
            alert('Registration successful!');
            closeModal('registerModal');
            window.location.href = '/dashboard';
        } else {
            alert(result.error || 'Registration failed');
        }
    } catch (error) {
        alert('Registration error. Please try again.');
        console.error('Register error:', error);
    }
}

// Logout
function logout() {
    localStorage.clear();
    window.location.href = '/';
}

// Close modals when clicking outside
window.onclick = function(event) {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const appointmentModal = document.getElementById('appointmentModal');
    
    if (event.target === loginModal) {
        loginModal.style.display = 'none';
    }
    if (event.target === registerModal) {
        registerModal.style.display = 'none';
    }
    if (event.target === appointmentModal) {
        appointmentModal.style.display = 'none';
    }
}

// Load user info
function loadUserInfo() {
    const userEmail = localStorage.getItem('userEmail');
    const userNameElement = document.getElementById('userName');
    
    if (userEmail && userNameElement) {
        const name = userEmail.split('@')[0];
        userNameElement.textContent = name.charAt(0).toUpperCase() + name.slice(1);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUserInfo();
    
    // Check if user is logged in
    const userEmail = localStorage.getItem('userEmail');
    const currentPath = window.location.pathname;
    
    if (!userEmail && (currentPath === '/dashboard' || currentPath === '/doctors' || currentPath === '/appointments')) {
        window.location.href = '/';
    }
});

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Add active class to navbar based on scroll position
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        if (window.pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href').slice(1) === current) {
            link.classList.add('active');
        }
    });
});

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Format time
function formatTime(dateString) {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleTimeString(undefined, options);
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Validate email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone
function isValidPhone(phone) {
    const re = /^\d{10}$/;
    return re.test(phone);
}

// Add form validation
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const emailInputs = form.querySelectorAll('input[type="email"]');
            
            emailInputs.forEach(input => {
                if (!isValidEmail(input.value)) {
                    e.preventDefault();
                    alert('Please enter a valid email address');
                }
            });
        });
    });
});
