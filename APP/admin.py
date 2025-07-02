from django.contrib import admin
# 1. Importe o novo modelo Seguro aqui
from .models import Funcionario, Cliente, RegraDeEmbarque, Seguro, Mensagem, Averbacao, GerenciadoraRisco

# Classe para exibir as Regras de Embarque diretamente na página do Cliente
class RegraDeEmbarqueInline(admin.TabularInline):
    model = RegraDeEmbarque
    extra = 1

class MensagemAdmin(admin.ModelAdmin):
    list_display = ('remetente', 'destinatario', 'conteudo', 'data_envio', 'is_atencao', 'lida')
    list_filter = ('is_atencao', 'remetente', 'destinatario')
    search_fields = ('conteudo',)

# Classe de administração para o modelo Cliente
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'gerente_conta', 'email_gc', 'tipo_seguro')
    search_fields = ('cliente', 'gerente_conta')
    inlines = [RegraDeEmbarqueInline]

# Registra os modelos no painel de administração
admin.site.register(Funcionario)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(RegraDeEmbarque)

# registrar o modelo Seguro
admin.site.register(Seguro)

# registrar o modelo Mensagem com a classe de administração
admin.site.register(Mensagem, MensagemAdmin)

# registrar o modelo Averbacao
admin.site.register(Averbacao)

# registrar o modelo GerenciadoraRisco
admin.site.register(GerenciadoraRisco)