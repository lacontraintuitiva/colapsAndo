document.addEventListener('DOMContentLoaded', function() {
    // Email validation
    const emailInput = document.getElementById('email-input');
    const emailFeedback = document.getElementById('email-feedback');
    if (emailInput && emailFeedback) {
        emailInput.addEventListener('input', function() {
            const value = emailInput.value;
            const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
            if (value.length === 0) {
                emailFeedback.textContent = '';
                emailFeedback.classList.remove('valid');
            } else if (valid) {
                emailFeedback.textContent = 'Correo válido';
                emailFeedback.classList.add('valid');
            } else {
                emailFeedback.textContent = 'Correo no válido';
                emailFeedback.classList.remove('valid');
            }
        });
    }

    // Password validation
    const passwordInput = document.getElementById('password-input');
    const confirmInput = document.getElementById('confirm-input');
    const passwordFeedback = document.getElementById('password-feedback');
    const confirmFeedback = document.getElementById('confirm-feedback');

    function validatePasswordFormat(password) {
        // Al menos 8 caracteres, una mayúscula, una minúscula y un número
        return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(password);
    }

    function showPasswordFeedback() {
        const value = passwordInput.value;
        if (value.length === 0) {
            passwordFeedback.textContent = '';
            passwordFeedback.classList.remove('valid');
            return false;
        } else if (validatePasswordFormat(value)) {
            passwordFeedback.textContent = 'Contraseña válida';
            passwordFeedback.classList.add('valid');
            return true;
        } else {
            passwordFeedback.textContent = 'Debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número';
            passwordFeedback.classList.remove('valid');
            return false;
        }
    }

    function showConfirmFeedback() {
        if (confirmInput.value.length === 0) {
            confirmFeedback.textContent = '';
            confirmFeedback.classList.remove('valid');
            return false;
        } else if (confirmInput.value === passwordInput.value) {
            confirmFeedback.textContent = 'Las contraseñas coinciden';
            confirmFeedback.classList.add('valid');
            return true;
        } else {
            confirmFeedback.textContent = 'Las contraseñas no coinciden';
            confirmFeedback.classList.remove('valid');
            return false;
        }
    }

    if (passwordInput && passwordFeedback) {
        passwordInput.addEventListener('input', showPasswordFeedback);
    }
    if (confirmInput && confirmFeedback) {
        confirmInput.addEventListener('input', showConfirmFeedback);
        passwordInput && passwordInput.addEventListener('input', showConfirmFeedback);
    }

    // Prevenir envío si hay errores
    const form = document.querySelector('form');
    if (form && passwordInput && confirmInput) {
        form.addEventListener('submit', function(e) {
            const passOk = showPasswordFeedback();
            const confirmOk = showConfirmFeedback();
            if (!passOk || !confirmOk) {
                e.preventDefault();
                if (!passOk) passwordInput.focus();
                else if (!confirmOk) confirmInput.focus();
            } else {
                // Limpia el mensaje de correo válido al enviar el formulario
                if (emailFeedback) {
                    emailFeedback.textContent = '';
                    emailFeedback.classList.remove('valid');
                }
            }
        });
    }

    const nameInput = document.querySelector('input[name="name"]');
    const registerBtn = document.getElementById('register-btn');

    function isFormValid() {
        // Valida nombre, email, contraseña y confirmación
        const nameOk = nameInput && nameInput.value.trim().length > 0;
        const emailOk = emailInput && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value);
        const passOk = passwordInput && /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(passwordInput.value);
        const confirmOk = confirmInput && confirmInput.value === passwordInput.value && confirmInput.value.length > 0;
        return nameOk && emailOk && passOk && confirmOk;
    }

    function toggleRegisterBtn() {
        if (registerBtn) {
            registerBtn.disabled = !isFormValid();
        }
    }

    // Escucha cambios en todos los campos relevantes
    [nameInput, emailInput, passwordInput, confirmInput].forEach(input => {
        if (input) input.addEventListener('input', toggleRegisterBtn);
    });

    // Inicializa el estado del botón
    toggleRegisterBtn();
});