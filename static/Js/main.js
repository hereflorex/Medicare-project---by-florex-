// Ye check karne ke liye ki file connect hui ya nahi
console.log("🚀 MediCare Pro Loaded Successfully");

// Modal Functions - Inhe Global (window) object mein daalna zaroori hai
window.openModal = function(id) {
    console.log("Opening Modal: " + id);
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Scroll stop
    }
};

window.closeModal = function(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Scroll start
    }
};

// Handle Login
window.handleLogin = async function() {
    console.log("Login attempt...");
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        alert("Please fill all fields");
        return;
    }

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        const data = await res.json();
        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            alert("❌ " + data.error);
        }
    } catch (err) {
        console.error("Login Error:", err);
    }
};

// Handle Register
window.handleRegister = async function() {
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const role = document.getElementById('regRole').value;

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, email, password, role})
        });
        const data = await res.json();
        if (data.success) {
            alert("✅ Account Created! Please Login.");
            location.reload();
        } else {
            alert("❌ " + data.error);
        }
    } catch (err) {
        console.error("Reg Error:", err);
    }
};

// Book Appointment
window.bookAppointment = async function(docId) {
    const date = prompt("Enter Date (YYYY-MM-DD):");
    const reason = prompt("Enter Reason for Visit:");
    
    if (!date || !reason) return;

    const res = await fetch('/api/book', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({doctor_id: docId, date, reason})
    });
    
    if (res.ok) {
        alert("🗓️ Appointment Scheduled!");
        window.location.href = '/appointments';
    }
};

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
};
