async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    });

    const data = await res.json();
    if(data.success) {
        window.location.href = '/dashboard';
    } else {
        alert(data.error);
    }
}

async function bookAppointment(doctorId) {
    const date = prompt("Enter Date (YYYY-MM-DD):");
    const reason = prompt("Reason for Appointment:");

    if(!date || !reason) return;

    const res = await fetch('/api/book', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({doctor_id: doctorId, date, reason})
    });

    if(res.ok) {
        alert("Appointment Booked Successfully!");
        window.location.href = '/appointments';
    }
}
