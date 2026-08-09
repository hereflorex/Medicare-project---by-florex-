function openModal(id) { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

async function handleRegister() {
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const role = document.getElementById('regRole').value;

    const res = await fetch('/api/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, password, role})
    });
    const data = await res.json();
    if(data.success) { alert("Registration Successful! Please Login."); location.reload(); }
    else { alert(data.error); }
}

async function handleLogin() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    });
    const data = await res.json();
    if(data.success) { window.location.href = '/dashboard'; }
    else { alert(data.error); }
}

async function bookAppointment(docId) {
    const date = prompt("Enter Appointment Date (e.g., 2024-10-25):");
    const reason = prompt("Enter Reason:");
    if(!date || !reason) return;

    const res = await fetch('/api/book', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({doctor_id: docId, date, reason})
    });
    if(res.ok) { alert("Booked Successfully!"); window.location.href = '/appointments'; }
}
