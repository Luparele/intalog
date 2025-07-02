// static/js/main.js

// Espera o documento carregar
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.querySelector('.sidebar');
    const sidebarLinks = document.querySelectorAll('.sidebar a');

    // Adiciona um listener de clique a cada link da sidebar
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(event) {

            // Adiciona uma classe temporária para 'travar' a animação de hover
            sidebar.classList.add('sidebar-clicked');

            // Remove a classe após a animação de retração terminar (300ms)
            // Isso permite que o efeito de hover volte a funcionar normalmente
            setTimeout(() => {
                sidebar.classList.remove('sidebar-clicked');
            }, 300);
        });
    });
});

const closeMessageButtons = document.querySelectorAll('.close-message');
closeMessageButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        // Pega o elemento pai (o alerta inteiro) e o esconde
        const messageDiv = btn.closest('.message');
        if (messageDiv) {
            messageDiv.style.display = 'none';
        }
    });
});

// Lógica para fechar o alerta LGPD
document.addEventListener('DOMContentLoaded', function() {
    const lgpdAlert = document.querySelector('.lgpd-alert');
    if (lgpdAlert) {
        const closeBtn = lgpdAlert.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                lgpdAlert.style.display = 'none';
            });
        }
    }
});