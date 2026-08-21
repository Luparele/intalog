document.addEventListener('DOMContentLoaded', function() {
    
    // --- LÓGICA DO MENU HAMBÚRGUER ---
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn && sidebar && overlay) {
        const toggleMenu = () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('active');
        };
        toggleBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', toggleMenu);
    }

    // --- LÓGICA DOS SUB-MENUS ---
    const submenuToggles = document.querySelectorAll('.submenu-toggle');

    submenuToggles.forEach(toggle => {
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            // Impede que o clique no toggle seja pego pelo listener do document,
            // que fecharia o menu que acabamos de abrir.
            event.stopPropagation();

            const parentLi = this.parentElement;

            // Fecha qualquer outro submenu que esteja aberto
            document.querySelectorAll('.sidebar .has-submenu.open').forEach(openLi => {
                if (openLi !== parentLi) {
                    openLi.classList.remove('open');
                }
            });

            // Alterna o estado (abre/fecha) do submenu que foi clicado
            parentLi.classList.toggle('open');
        });
    });

    // --- LÓGICA GLOBAL DE CLIQUES (FECHAR SUBMENUS E ALERTAS) ---
    document.addEventListener('click', function(event) {
        // Lógica para fechar submenus
        // Se o clique foi fora de um item de menu que tem submenu, fecha todos.
        if (!event.target.closest('.has-submenu')) {
            document.querySelectorAll('.sidebar .has-submenu.open').forEach(openLi => {
                openLi.classList.remove('open');
            });
        }

        // Lógica para fechar alertas
        if (event.target.classList.contains('close-message')) {
            const messageDiv = event.target.closest('.message');
            if (messageDiv) { messageDiv.style.display = 'none'; }
        }
        if (event.target.classList.contains('close-btn')) {
            const lgpdAlert = event.target.closest('.lgpd-alert');
            if (lgpdAlert) { lgpdAlert.style.display = 'none'; }
        }
    });

});
