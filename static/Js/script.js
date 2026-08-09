// ============================================================
// MediCare - Global JavaScript
// ============================================================

// Global variables
let userType = null;
let userId = null;


// ============================================================
// SHOW LOGIN MODAL
// ============================================================

function showLoginModal(type) {

    userType = type;

    const modal = document.getElementById('loginModal');
    const loginTitle = document.getElementById('loginTitle');

    if (!modal) {
        console.error('loginModal not found');
        return;
    }

    // Set login title according to user type
    if (loginTitle) {

        if (type === 'doctor') {
            loginTitle.textContent = 'Doctor Login';
        } else {
            loginTitle.textContent = 'Patient Login';
        }

    }

    modal.style.display = 'block';
}


// ============================================================
// SHOW REGISTER MODAL
// ============================================================

function showRegisterModal(type) {

    userType = type;

    const patientFields =
        document.getElementById('patientFields');

    const doctorFields =
        document.getElementById('doctorFields');

    const modal =
        document.getElementById('registerModal');

    const registerTitle =
        document.getElementById('registerTitle');


    if (!patientFields || !doctorFields || !modal) {

        console.error(
            'Registration modal elements not found'
        );

        return;
    }


    // Change registration title
    if (registerTitle) {

        if (type === 'doctor') {
            registerTitle.textContent =
                'Doctor Registration';
        } else {
            registerTitle.textContent =
                'Patient Registration';
        }
    }


    // Show / hide fields
    if (type === 'patient') {

        patientFields.style.display = 'block';
        doctorFields.style.display = 'none';

    } else {

        patientFields.style.display = 'none';
        doctorFields.style.display = 'block';
    }


    modal.style.display = 'block';
}


// ============================================================
// CLOSE MODAL
// ============================================================

function closeModal(modalId) {

    const modal =
        document.getElementById(modalId);

    if (modal) {
        modal.style.display = 'none';
    }
}


// ============================================================
// HANDLE LOGIN
// ============================================================

async function handleLogin(event) {

    event.preventDefault();


    const emailInput =
        document.getElementById('loginEmail');

    const passwordInput =
        document.getElementById('loginPassword');


    if (!emailInput || !passwordInput) {

        console.error(
            'Login form fields not found'
        );

        return;
    }


    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value;


    // Basic validation
    if (!isValidEmail(email)) {

        alert(
            'Please enter a valid email address.'
        );

        return;
    }


    if (!password) {

        alert(
            'Please enter your password.'
        );

        return;
    }


    // Check selected user type
    if (
        userType !== 'patient' &&
        userType !== 'doctor'
    ) {

        alert(
            'Please select Patient or Doctor login.'
        );

        return;
    }


    try {

        /*
         * Login endpoint
         *
         * Patient:
         * /api/patients/login
         *
         * Doctor:
         * /api/doctors/login
         */

        const endpoint =
            userType === 'doctor'
                ? '/api/doctors/login'
                : '/api/patients/login';


        const response =
            await fetch(endpoint, {

                method: 'POST',

                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify({

                    email: email,
                    password: password

                })

            });


        let result = {};

        try {

            result =
                await response.json();

        } catch (jsonError) {

            console.error(
                'Invalid JSON response:',
                jsonError
            );

        }


        if (response.ok) {

            // Save login information
            localStorage.setItem(
                'userEmail',
                email
            );

            localStorage.setItem(
                'userType',
                userType
            );


            // Save returned user ID
            if (result.id) {

                userId =
                    result.id;

                localStorage.setItem(
                    `${userType}Id`,
                    result.id
                );
            }


            // Save user name if backend sends it
            if (result.name) {

                localStorage.setItem(
                    'userName',
                    result.name
                );
            }


            alert(
                `Login successful! Welcome ${result.name || email}`
            );


            closeModal('loginModal');


            // Redirect to dashboard
            window.location.href =
                '/dashboard';


        } else {

            alert(
                result.error ||
                result.message ||
                'Invalid email or password.'
            );

        }


    } catch (error) {

        console.error(
            'Login error:',
            error
        );


        alert(
            'Unable to connect to the server. Please try again.'
        );

    }

}


// ============================================================
// HANDLE REGISTRATION
// ============================================================

async function handleRegister(event) {

    event.preventDefault();


    const nameInput =
        document.getElementById('regName');

    const emailInput =
        document.getElementById('regEmail');

    const passwordInput =
        document.getElementById('regPassword');

    const phoneInput =
        document.getElementById('regPhone');


    if (
        !nameInput ||
        !emailInput ||
        !passwordInput ||
        !phoneInput
    ) {

        console.error(
            'Registration form fields not found'
        );

        return;
    }


    const name =
        nameInput.value.trim();

    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value;

    const phone =
        phoneInput.value.trim();


    // Basic validation
    if (!name) {

        alert(
            'Please enter your full name.'
        );

        return;
    }


    if (!isValidEmail(email)) {

        alert(
            'Please enter a valid email address.'
        );

        return;
    }


    if (password.length < 6) {

        alert(
            'Password must be at least 6 characters.'
        );

        return;
    }


    if (!isValidPhone(phone)) {

        alert(
            'Please enter a valid 10-digit phone number.'
        );

        return;
    }


    let endpoint;
    let data;


    // ========================================================
    // PATIENT REGISTRATION
    // ========================================================

    if (userType === 'patient') {

        const ageInput =
            document.getElementById('regAge');

        const addressInput =
            document.getElementById('regAddress');


        const age =
            ageInput
                ? parseInt(ageInput.value)
                : null;

        const address =
            addressInput
                ? addressInput.value.trim()
                : '';


        if (
            !age ||
            age < 1 ||
            age > 120
        ) {

            alert(
                'Please enter a valid age.'
            );

            return;
        }


        if (!address) {

            alert(
                'Please enter your address.'
            );

            return;
        }


        endpoint =
            '/api/patients/register';


        data = {

            name: name,

            email: email,

            password: password,

            phone: phone,

            age: age,

            address: address

        };


    // ========================================================
    // DOCTOR REGISTRATION
    // ========================================================

    } else if (userType === 'doctor') {

        const specializationInput =
            document.getElementById(
                'regSpecialization'
            );


        const specialization =
            specializationInput
                ? specializationInput.value.trim()
                : '';


        if (!specialization) {

            alert(
                'Please enter your specialization.'
            );

            return;
        }


        endpoint =
            '/api/doctors/register';


        data = {

            name: name,

            email: email,

            password: password,

            phone: phone,

            specialization:
                specialization

        };


    } else {

        alert(
            'Please select Patient or Doctor registration.'
        );

        return;
    }


    try {

        const response =
            await fetch(endpoint, {

                method: 'POST',

                headers: {
                    'Content-Type':
                        'application/json'
                },

                body:
                    JSON.stringify(data)

            });


        let result = {};

        try {

            result =
                await response.json();

        } catch (jsonError) {

            console.error(
                'Invalid JSON response:',
                jsonError
            );

        }


        if (response.ok) {

            // Save user information
            localStorage.setItem(
                'userEmail',
                email
            );

            localStorage.setItem(
                'userType',
                userType
            );


            // Save ID
            if (result.id) {

                userId =
                    result.id;

                localStorage.setItem(
                    `${userType}Id`,
                    result.id
                );
            }


            // Save name
            localStorage.setItem(
                'userName',
                name
            );


            alert(
                result.message ||
                'Registration successful!'
            );


            closeModal(
                'registerModal'
            );


            // Redirect
            window.location.href =
                '/dashboard';


        } else {

            alert(
                result.error ||
                result.message ||
                'Registration failed.'
            );

        }


    } catch (error) {

        console.error(
            'Registration error:',
            error
        );


        alert(
            'Unable to connect to the server. Please try again.'
        );

    }

}
// ============================================================
// LOGOUT
// ============================================================

function logout() {

    // Remove saved login information
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userType');
    localStorage.removeItem('userName');
    localStorage.removeItem('patientId');
    localStorage.removeItem('doctorId');

    // Reset global variables
    userType = null;
    userId = null;

    // Go back to home page
    window.location.href = '/';
}


// ============================================================
// CLOSE MODAL WHEN CLICKING OUTSIDE
// ============================================================

window.addEventListener('click', function (event) {

    const loginModal =
        document.getElementById('loginModal');

    const registerModal =
        document.getElementById('registerModal');

    const appointmentModal =
        document.getElementById('appointmentModal');


    // Login modal
    if (
        loginModal &&
        event.target === loginModal
    ) {

        loginModal.style.display = 'none';
    }


    // Register modal
    if (
        registerModal &&
        event.target === registerModal
    ) {

        registerModal.style.display = 'none';
    }


    // Appointment modal
    if (
        appointmentModal &&
        event.target === appointmentModal
    ) {

        appointmentModal.style.display = 'none';
    }

});


// ============================================================
// ESC KEY - CLOSE MODALS
// ============================================================

document.addEventListener('keydown', function (event) {

    if (event.key !== 'Escape') {
        return;
    }


    const modals =
        document.querySelectorAll('.modal');


    modals.forEach(function (modal) {

        modal.style.display = 'none';

    });

});


// ============================================================
// LOAD USER INFO
// ============================================================

function loadUserInfo() {

    const userEmail =
        localStorage.getItem('userEmail');

    const savedUserName =
        localStorage.getItem('userName');

    const userTypeValue =
        localStorage.getItem('userType');


    const userNameElement =
        document.getElementById('userName');


    if (
        !userNameElement
    ) {
        return;
    }


    // Use saved name first
    if (savedUserName) {

        userNameElement.textContent =
            savedUserName;

        return;
    }


    // Otherwise use email username
    if (userEmail) {

        const name =
            userEmail
                .split('@')[0];


        userNameElement.textContent =
            name.charAt(0).toUpperCase() +
            name.slice(1);

        return;
    }


    // Default
    userNameElement.textContent =
        userTypeValue === 'doctor'
            ? 'Doctor'
            : 'Patient';
}


// ============================================================
// CHECK LOGIN STATUS
// ============================================================

function isUserLoggedIn() {

    const email =
        localStorage.getItem('userEmail');

    const type =
        localStorage.getItem('userType');


    return Boolean(
        email &&
        (
            type === 'patient' ||
            type === 'doctor'
        )
    );
}


// ============================================================
// PROTECT PRIVATE PAGES
// ============================================================

function protectPage() {

    const currentPath =
        window.location.pathname;


    const protectedPages = [

        '/dashboard',

        '/doctors',

        '/appointments'

    ];


    if (
        protectedPages.includes(currentPath) &&
        !isUserLoggedIn()
    ) {

        console.warn(
            'User is not logged in. Redirecting...'
        );


        window.location.href =
            '/';

    }

}


// ============================================================
// SMOOTH SCROLL
// ============================================================

function initializeSmoothScroll() {

    const anchors =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    anchors.forEach(function (anchor) {

        anchor.addEventListener(
            'click',
            function (event) {

                const href =
                    this.getAttribute('href');


                // Ignore empty #
                if (
                    !href ||
                    href === '#'
                ) {

                    return;
                }


                const target =
                    document.querySelector(
                        href
                    );


                if (target) {

                    event.preventDefault();


                    target.scrollIntoView({

                        behavior: 'smooth',

                        block: 'start'

                    });

                }

            }
        );

    });

}


// ============================================================
// ACTIVE NAVBAR ON SCROLL
// ============================================================

function updateActiveNavbar() {

    const sections =
        document.querySelectorAll(
            'section[id]'
        );


    const navLinks =
        document.querySelectorAll(
            '.nav-menu a'
        );


    if (
        sections.length === 0 ||
        navLinks.length === 0
    ) {

        return;
    }


    let currentSection = '';


    sections.forEach(function (section) {

        const sectionTop =
            section.offsetTop;


        const sectionHeight =
            section.offsetHeight;


        if (
            window.scrollY >=
            sectionTop - 200
        ) {

            currentSection =
                section.getAttribute('id');

        }

    });


    navLinks.forEach(function (link) {

        link.classList.remove('active');


        const href =
            link.getAttribute('href');


        if (
            href &&
            href.startsWith('#') &&
            href.substring(1) ===
                currentSection
        ) {

            link.classList.add('active');

        }

    });

}


// ============================================================
// FORMAT DATE
// ============================================================

function formatDate(dateString) {

    if (!dateString) {
        return '';
    }


    const date =
        new Date(dateString);


    if (isNaN(date.getTime())) {
        return '';
    }


    return date.toLocaleDateString(
        undefined,
        {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }
    );

}


// ============================================================
// FORMAT TIME
// ============================================================

function formatTime(dateString) {

    if (!dateString) {
        return '';
    }


    const date =
        new Date(dateString);


    if (isNaN(date.getTime())) {
        return '';
    }


    return date.toLocaleTimeString(
        undefined,
        {
            hour: '2-digit',
            minute: '2-digit'
        }
    );

}


// ============================================================
// TOAST NOTIFICATION
// ============================================================

function showToast(
    message,
    type = 'info'
) {

    // Remove old toast if one exists
    const oldToast =
        document.querySelector('.toast');


    if (oldToast) {
        oldToast.remove();
    }


    const toast =
        document.createElement('div');


    toast.className =
        `toast toast-${type}`;


    toast.textContent =
        message;


    document.body.appendChild(
        toast
    );


    // Remove after 3 seconds
    setTimeout(function () {

        if (toast) {
            toast.remove();
        }

    }, 3000);

}


// ============================================================
// EMAIL VALIDATION
// ============================================================

function isValidEmail(email) {

    if (!email) {
        return false;
    }


    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    return emailPattern.test(
        email.trim()
    );

}


// ============================================================
// PHONE VALIDATION
// ============================================================

function isValidPhone(phone) {

    if (!phone) {
        return false;
    }


    // Indian 10-digit mobile number
    const phonePattern =
        /^[6-9]\d{9}$/;


    return phonePattern.test(
        phone.trim()
    );

}


// ============================================================
// FORM VALIDATION
// ============================================================

function initializeFormValidation() {

    const forms =
        document.querySelectorAll(
            'form'
        );


    forms.forEach(function (form) {

        form.addEventListener(
            'submit',
            function (event) {

                const emailInputs =
                    form.querySelectorAll(
                        'input[type="email"]'
                    );


                let valid = true;


                emailInputs.forEach(
                    function (input) {

                        if (
                            input.value.trim() &&
                            !isValidEmail(
                                input.value
                            )
                        ) {

                            valid = false;

                            input.focus();

                            alert(
                                'Please enter a valid email address.'
                            );

                        }

                    }
                );


                const phoneInputs =
                    form.querySelectorAll(
                        'input[type="tel"]'
                    );


                phoneInputs.forEach(
                    function (input) {

                        if (
                            input.value.trim() &&
                            !isValidPhone(
                                input.value
                            )
                        ) {

                            valid = false;

                            input.focus();

                            alert(
                                'Please enter a valid 10-digit phone number.'
                            );

                        }

                    }
                );


                if (!valid) {

                    event.preventDefault();

                }

            }
        );

    });

}


// ============================================================
// PAGE INITIALIZATION
// ============================================================

document.addEventListener(
    'DOMContentLoaded',
    function () {

        console.log(
            'MediCare JavaScript loaded successfully'
        );


        // Load logged-in user information
        loadUserInfo();


        // Protect dashboard pages
        protectPage();


        // Enable smooth scrolling
        initializeSmoothScroll();


        // Enable form validation
        initializeFormValidation();


        // Initial navbar state
        updateActiveNavbar();

    }
);


// ============================================================
// SCROLL EVENT
// ============================================================

window.addEventListener(
    'scroll',
    function () {

        updateActiveNavbar();

    }
);


// ============================================================
// CONSOLE MESSAGE
// ============================================================

console.log(
    'MediCare script.js initialized.'
);
