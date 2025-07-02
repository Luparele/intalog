document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modal-mensagem');
    if (!modal) return;

    const modalRemetente = document.getElementById('modal-remetente');
    const modalConteudo = document.getElementById('modal-conteudo');
    const modalData = document.getElementById('modal-data');
    const btnLida = document.getElementById('modal-btn-lida');
    const btnResponder = document.getElementById('modal-btn-responder');
    const fecharBtn = modal.querySelector('.close-modal');
    
    // Pega o CSRF token de um cookie para as requisições POST via fetch
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrfToken = getCookie('csrftoken');

    let mensagemId = null;

    document.querySelectorAll('.mensagem-item').forEach(item => {
        item.addEventListener('click', function() {
            // Guarda o ID da mensagem clicada
            mensagemId = this.dataset.id;
            const remetenteId = this.dataset.remetenteId;
            const isNaoLida = this.classList.contains('nao-lida');
            
            // Popula o modal com os dados da mensagem
            modalRemetente.textContent = this.dataset.remetente;
            modalConteudo.textContent = this.dataset.conteudo;
            modalData.textContent = `Enviada em: ${this.dataset.data}`;
            
            // Configura o botão de resposta
            const responderUrl = `/mensagens/enviar/?responder_para=${remetenteId}`;
            btnResponder.href = responderUrl;

            // Mostra ou esconde o botão "Marcar como Lida"
            btnLida.style.display = isNaoLida ? 'inline-block' : 'none';

            // Mostra o modal
            modal.style.display = 'flex';
        });
    });

    // Ação do botão "Sinalizar como Lida"
    btnLida.addEventListener('click', () => {
        if (!mensagemId) return;

        fetch(`/mensagens/marcar-lida/${mensagemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const itemMensagem = document.querySelector(`.mensagem-item[data-id="${mensagemId}"]`);
                if (itemMensagem) {
                    itemMensagem.classList.remove('nao-lida');
                }
                btnLida.style.display = 'none';
            }
        });
    });

    // Ações para fechar o modal
    fecharBtn.onclick = () => { modal.style.display = 'none'; };
    window.onclick = (event) => { if (event.target == modal) { modal.style.display = 'none'; } };
});