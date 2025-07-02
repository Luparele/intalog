document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('id_new_password1');
    const strengthBarFill = document.getElementById('strength-bar-fill');
    
    const requirements = {
        length: document.getElementById('req-length'),
        lowercase: document.getElementById('req-lowercase'),
        uppercase: document.getElementById('req-uppercase'),
        number: document.getElementById('req-number'),
        special: document.getElementById('req-special')
    };

    const regex = {
        lowercase: /[a-z]/,
        uppercase: /[A-Z]/,
        number: /[0-9]/,
        special: /[^A-Za-z0-9]/ // Qualquer caractere que não seja letra ou número
    };

    passwordInput.addEventListener('input', function() {
        const password = this.value;
        let score = 0;

        // 1. Verifica o comprimento
        if (password.length >= 8) {
            requirements.length.classList.add('valid');
            score++;
        } else {
            requirements.length.classList.remove('valid');
        }

        // 2. Verifica letra minúscula
        if (regex.lowercase.test(password)) {
            requirements.lowercase.classList.add('valid');
            score++;
        } else {
            requirements.lowercase.classList.remove('valid');
        }

        // 3. Verifica letra maiúscula
        if (regex.uppercase.test(password)) {
            requirements.uppercase.classList.add('valid');
            score++;
        } else {
            requirements.uppercase.classList.remove('valid');
        }

        // 4. Verifica número
        if (regex.number.test(password)) {
            requirements.number.classList.add('valid');
            score++;
        } else {
            requirements.number.classList.remove('valid');
        }

        // 5. Verifica caractere especial
        if (regex.special.test(password)) {
            requirements.special.classList.add('valid');
            score++;
        } else {
            requirements.special.classList.remove('valid');
        }
        
        // Atualiza a barra de força
        updateStrengthBar(score);
    });

    function updateStrengthBar(score) {
        strengthBarFill.className = 'strength-bar-fill'; // Reseta as classes de cor

        if (score <= 1) {
            strengthBarFill.style.width = '20%';
            strengthBarFill.classList.add('weak');
        } else if (score === 2) {
            strengthBarFill.style.width = '40%';
            strengthBarFill.classList.add('weak');
        } else if (score === 3) {
            strengthBarFill.style.width = '60%';
            strengthBarFill.classList.add('medium');
        } else if (score === 4) {
            strengthBarFill.style.width = '80%';
            strengthBarFill.classList.add('strong');
        } else if (score === 5) {
            strengthBarFill.style.width = '100%';
            strengthBarFill.classList.add('very-strong');
        } else {
            strengthBarFill.style.width = '0%';
        }
    }
});