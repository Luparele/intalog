document.addEventListener('DOMContentLoaded', () => {
    // --- LÓGICA DO MODAL (EXISTENTE) ---
    const modal = document.getElementById('modal-averbacao');
    const abrirBtn = document.getElementById('abrir-modal-btn');
    const fecharBtns = document.querySelectorAll('.close-modal, .close-modal-btn');

    if (modal && abrirBtn && fecharBtns) {
        abrirBtn.onclick = function() {
            modal.style.display = 'flex';
        }
        fecharBtns.forEach(btn => {
            btn.onclick = function() {
                modal.style.display = 'none';
            }
        });
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    }

    // --- NOVA LÓGICA PARA MÁSCARA DE CNPJ ---
    const cnpjInput = document.getElementById('id_cnpj');
    if (cnpjInput) {
        cnpjInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            value = value.replace(/^(\d{2})(\d)/, '$1.$2');
            value = value.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
            value = value.replace(/\.(\d{3})(\d)/, '.$1/$2');
            value = value.replace(/(\d{4})(\d)/, '$1-$2');
            e.target.value = value.substring(0, 18);
        });
    }

    // --- LÓGICA DO GRÁFICO DE PIZZA (ATUALIZADA) ---
    const ctx = document.getElementById('graficoAverbacoes');
    const chartDataElement = document.getElementById('chart-data');

    if (ctx && chartDataElement) {
        const chartData = JSON.parse(chartDataElement.textContent);

        new Chart(ctx, {
            type: 'pie', // Alterado para 'pie' para um visual mais limpo
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Nº de Cadastros',
                    data: chartData.data,
                    backgroundColor: [
                        'rgba(0, 82, 204, 0.8)',
                        'rgba(255, 102, 0, 0.8)',
                    ],
                    borderColor: 'rgba(255, 255, 255, 0.7)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? (value / total * 100).toFixed(1) + '%' : '0%';
                                return `${label}: ${value} (${percentage})`;
                            }
                        }
                    }
                }
            }
        });
    }
});