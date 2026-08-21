from django.contrib import admin
from .models import (
    Funcionario, Cliente, RegraDeEmbarque, Seguro, Mensagem, Averbacao, 
    GerenciadoraRisco, Sinistro, Rotograma, ChecklistVeiculo, ChecklistGR, 
    Checklist, TreinamentoQSMS, CertificadoQSMS, EventoQSMS, ContratoDiverso, 
    ServicoPendente, HistoricoAcao, ServicoPendenteQSMS, HistoricoAcaoQSMS,
    VeiculoAssegurado
)

# --- Classes de Administração Personalizadas ---

# Classe para exibir as Regras de Embarque diretamente na página do Cliente
class RegraDeEmbarqueInline(admin.TabularInline):
    model = RegraDeEmbarque
    extra = 1

# Classe para customizar a exibição de Mensagens
class MensagemAdmin(admin.ModelAdmin):
    list_display = ('remetente', 'destinatario', 'conteudo', 'data_envio', 'is_atencao', 'lida')
    list_filter = ('is_atencao', 'remetente', 'destinatario')
    search_fields = ('conteudo',)

# Classe para customizar a exibição de Clientes
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'gerente_conta', 'email_gc', 'tipo_seguro')
    search_fields = ('cliente', 'gerente_conta')
    inlines = [RegraDeEmbarqueInline]

# Classe para exibir o Histórico de Ações diretamente na página do Serviço Pendente
class HistoricoAcaoInline(admin.TabularInline):
    model = HistoricoAcao
    extra = 0
    readonly_fields = ('usuario', 'data_acao', 'acao')

# Classe para customizar a exibição de Serviços Pendentes
class ServicoPendenteAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'criado_por', 'data_criacao', 'finalizado_por', 'data_finalizacao')
    list_filter = ('status',)
    inlines = [HistoricoAcaoInline]

class HistoricoAcaoQSMSInline(admin.TabularInline):
    model = HistoricoAcaoQSMS
    extra = 0
    readonly_fields = ('usuario', 'data_acao', 'acao')

class ServicoPendenteQSMSAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'criado_por', 'data_criacao')
    list_filter = ('status',)
    inlines = [HistoricoAcaoQSMSInline]

# Classe para customizar a exibição de Veículos Assegurados (Adicionado)
class VeiculoAsseguradoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'modelo', 'marca', 'seguradora', 'vigencia', 'cobertura')
    search_fields = ('placa', 'modelo', 'marca', 'seguradora')
    list_filter = ('seguradora', 'cobertura', 'vidros')
    ordering = ('vigencia',)

# --- Registro dos Modelos no Painel de Administração ---

admin.site.register(Funcionario)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(RegraDeEmbarque)
admin.site.register(Seguro)
admin.site.register(Mensagem, MensagemAdmin)
admin.site.register(Averbacao)
admin.site.register(GerenciadoraRisco)
admin.site.register(Sinistro)
admin.site.register(Rotograma)
admin.site.register(ChecklistVeiculo) 
admin.site.register(ChecklistGR)
admin.site.register(Checklist)
admin.site.register(TreinamentoQSMS)
admin.site.register(CertificadoQSMS)
admin.site.register(EventoQSMS)
admin.site.register(ContratoDiverso)

# Registros do Kanban
admin.site.register(ServicoPendente, ServicoPendenteAdmin)
admin.site.register(HistoricoAcao)
admin.site.register(ServicoPendenteQSMS, ServicoPendenteQSMSAdmin)
admin.site.register(HistoricoAcaoQSMS)

# Registro de Veículos Assegurados (Adicionado)
admin.site.register(VeiculoAssegurado, VeiculoAsseguradoAdmin)