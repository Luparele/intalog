from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField

# Criamos tuplas para as opções de 'choices' para evitar erros de digitação
ESTADOS_BRASILEiros = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]

TIPOS_CONTRATO = [
    ('CLT', 'CLT'),
    ('MEI', 'MEI'),
]

class Funcionario(models.Model):
    nome = models.CharField("Nome Completo", max_length=100)
    data_nascimento = models.DateField("Data de Nascimento", null=True, blank=True)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    rg = models.CharField("RG", max_length=20)
    data_expedicao = models.DateField("Data de Expedição")
    orgao_expedicao = models.CharField("Órgão de Expedição", max_length=50)
    uf = models.CharField("UF", max_length=2, choices=ESTADOS_BRASILEiros)
    endereco = models.TextField("Endereço")
    telefone_pessoal = models.CharField("Telefone Pessoal", max_length=20)
    setor = models.CharField("Setor", max_length=50)
    funcao = models.CharField("Função", max_length=50)
    tipo_contrato = models.CharField("Tipo de Contrato", max_length=3, choices=TIPOS_CONTRATO)
    telefone_corporativo = models.CharField("Telefone Corporativo", max_length=20, blank=True, null=True)
    email_corporativo = models.EmailField("E-mail Corporativo", blank=True, null=True)
    anotacoes = models.TextField("Anotações", blank=True, null=True)
    foto = models.ImageField("Foto", upload_to='fotos_funcionarios/', blank=True, null=True)
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.nome
    @property
    def whatsapp_link(self):
        if not self.telefone_corporativo:
            return ""
        numero_limpo = self.telefone_corporativo.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        return f"https://wa.me/{numero_limpo}"
    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

class Cliente(models.Model):
    TIPO_SEGURO_CHOICES = [
        ('DDR', 'DDR/Carta Conforto'),
        ('INTALOG', 'Averbado no Seguro Intalog'),
    ]
    cliente = models.CharField("Cliente", max_length=150, null=True, blank=True)
    gerente_conta = models.CharField("Gerente de Conta (GC)", max_length=100, null=True, blank=True)
    telefone_gc = models.CharField("Telefone do GC", max_length=20, null=True, blank=True)
    email_gc = models.EmailField("E-mail do GC", null=True, blank=True)
    tipo_seguro = models.CharField("Tipo de Seguro", max_length=10, choices=TIPO_SEGURO_CHOICES, null=True, blank=True)
    vigencia_pgr = models.DateField("Vigência do PGR", null=True, blank=True)
    pgr_arquivo = models.FileField("Arquivo PGR (PDF)", upload_to='pgr/', null=True, blank=True)
    ddr_arquivo = models.FileField("Arquivo DDR/Carta (PDF)", upload_to='ddr/', null=True, blank=True)
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.cliente or "Cliente sem nome"
    @property
    def whatsapp_link_gc(self):
        if not self.telefone_gc:
            return ""
        numero_limpo = self.telefone_gc.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        return f"https://wa.me/{numero_limpo}"
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class RegraDeEmbarque(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='regras_de_embarque')
    valor_min = models.DecimalField("Valor Mínimo da Carga", max_digits=10, decimal_places=2, null=True, blank=True)
    valor_max = models.DecimalField("Valor Máximo da Carga", max_digits=10, decimal_places=2, null=True, blank=True)
    contrato_frota = models.BooleanField("Frota", default=False)
    contrato_agregado = models.BooleanField("Agregado", default=False)
    contrato_terceiro = models.BooleanField("Terceiro", default=False)
    rastreado = models.BooleanField("Rastreado", default=False)
    isca_movel = models.BooleanField("Isca Móvel", default=False)
    quantidade_iscas = models.CharField("Quantidade de Iscas", max_length=2, choices=[('1', '01'), ('2', '02')], null=True, blank=True)
    escolta = models.BooleanField("Escolta", default=False)
    rastreador_redundancia = models.BooleanField("Rastreador/Bloqueador de Redundância", default=False)
    idade_max_cavalo = models.PositiveIntegerField("Idade Máxima do Cavalo (anos)", null=True, blank=True)
    idade_max_carreta = models.PositiveIntegerField("Idade Máxima da Carreta (anos)", null=True, blank=True)
    observacoes = models.TextField("Observações", null=True, blank=True)
    def __str__(self):
        return f"Regra para {self.cliente.cliente} (R$ {self.valor_min} - R$ {self.valor_max})"
    class Meta:
        verbose_name = "Regra de Embarque"
        verbose_name_plural = "Regras de Embarque"

class Seguro(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='seguros', verbose_name="Cliente", null=True, blank=True)
    seguradora = models.CharField("Seguradora", max_length=100, null=True, blank=True)
    tipo_apolice = models.CharField("Tipo de Apólice", max_length=100)
    corretora = models.CharField("Corretora", max_length=100)
    corretor = models.CharField("Corretor", max_length=100)
    tel_corretor = models.CharField("Telefone do Corretor", max_length=20)
    email_corretor = models.EmailField("E-mail do Corretor")
    vigencia = models.DateField("Vigência do Seguro")
    descricao = models.TextField("Descrição do Seguro")
    apolice_anexo = models.FileField("Anexo da Apólice (PDF)", upload_to='apolices/', blank=True, null=True)
    certificado_anexo = models.FileField("Anexo do Certificado (PDF)", upload_to='certificados/', blank=True, null=True)
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True, null=True, blank=True)
    def __str__(self):
        if self.cliente:
            return f"{self.tipo_apolice} - {self.cliente.cliente}"
        return f"{self.tipo_apolice} - (Sem cliente associado)"
    class Meta:
        verbose_name = "Seguro"
        verbose_name_plural = "Seguros"
        ordering = ['cliente__cliente', 'tipo_apolice']

class Mensagem(models.Model):
    remetente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_recebidas', null=True, blank=True)
    conteudo = models.TextField("Conteúdo")
    data_envio = models.DateTimeField(auto_now_add=True)
    is_atencao = models.BooleanField("Mensagem de Atenção", default=False)
    lida = models.BooleanField(default=False)
    def __str__(self):
        if self.destinatario:
            return f"De {self.remetente.username} para {self.destinatario.username}"
        else:
            return f"Mensagem Geral de {self.remetente.username}"
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['-data_envio']

class Averbacao(models.Model):
    TIPO_SEGURO_CHOICES = [
        ('DDR', 'DDR/Carta Conforto'),
        ('INTALOG', 'Averbado ao Seguro Intalog'),
    ]
    cliente_nome = models.CharField("Nome do Cliente", max_length=150)
    cnpj = models.CharField("CNPJ", max_length=18)
    tipo_seguro = models.CharField("Tipo de Seguro", max_length=10, choices=TIPO_SEGURO_CHOICES)
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return f"{self.cliente_nome} ({self.cnpj}) - {self.get_tipo_seguro_display()}"
    class Meta:
        verbose_name = "Averbação"
        verbose_name_plural = "Averbações"
        ordering = ['cliente_nome']

class GerenciadoraRisco(models.Model):
    nome = models.CharField("Gerenciadora de Risco", max_length=150)
    validade_condutor_clt = models.PositiveIntegerField("Validade de pesquisa de Condutor CLT")
    validade_condutor_agregado = models.PositiveIntegerField("Validade de pesquisa de Condutor Agregado")
    validade_condutor_terceiro = models.CharField("Validade de pesquisa de Condutor Terceiro", max_length=50, default="Por Embarque")
    validade_veiculo_frota = models.PositiveIntegerField("Validade de pesquisa de Veículo Frota")
    validade_veiculo_agregado = models.PositiveIntegerField("Validade de pesquisa de Veículo Agregado")
    validade_veiculo_terceiro = models.CharField("Validade de pesquisa de Veículo Terceiro", max_length=50, default="Por Embarque")
    validade_checklist_frota = models.PositiveIntegerField("Validade de Checklist de Veículo Frota")
    validade_checklist_agregado = models.PositiveIntegerField("Validade de Checklist de Veículo Agregado")
    validade_checklist_terceiro = models.CharField("Validade de Checklist de Veículo Terceiro", max_length=50, default="Por Embarque")
    observacoes = models.TextField("Observações diversas", blank=True, null=True)
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Gerenciadora de Risco"
        verbose_name_plural = "Gerenciadoras de Risco"
        ordering = ['nome']

class Sinistro(models.Model):
    STATUS_CHOICES = [ ('ANDAMENTO', 'Em andamento'), ('FINALIZADO', 'Finalizado'), ]
    data_hora_sinistro = models.DateTimeField("Data e Hora do Sinistro")
    veiculo_assegurado = models.CharField("Veículo Assegurado", max_length=150)
    seguradora = models.CharField("Seguradora", max_length=100)
    status = models.CharField("Status do Sinistro", max_length=10, choices=STATUS_CHOICES, default='ANDAMENTO')
    detalhes = RichTextField("Detalhes")
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return f"Sinistro em {self.data_hora_sinistro.strftime('%d/%m/%Y')} - Veículo: {self.veiculo_assegurado}"
    class Meta:
        verbose_name = "Sinistro"
        verbose_name_plural = "Sinistros"
        ordering = ['status', '-data_hora_sinistro']

class Rotograma(models.Model):
    nome = models.CharField("Nome", max_length=150)
    origem = models.CharField("Origem", max_length=150)
    destino = models.CharField("Destino", max_length=150)
    arquivo_pdf = models.FileField("Arquivo (PDF)", upload_to='rotogramas/')
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.nome
    class Meta:
        verbose_name = "Rotograma"
        verbose_name_plural = "Rotogramas"
        ordering = ['nome']

class ChecklistVeiculo(models.Model):
    CATEGORIA_CHOICES = [('FROTA', 'Frota'), ('AGREGADO', 'Agregado')]
    TIPO_CHOICES = [('CAVALO', 'Cavalo'), ('CARRETA', 'Carreta')]
    placa = models.CharField("Placa", max_length=10, unique=True)
    categoria = models.CharField("Categoria", max_length=10, choices=CATEGORIA_CHOICES)
    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.placa

class ChecklistGR(models.Model):
    VALIDADE_CHOICES = [(30, '30 dias'), (60, '60 dias'), (90, '90 dias')]
    nome = models.CharField("Nome da GR", max_length=150, unique=True)
    validade_checklist = models.IntegerField("Validade do Checklist", choices=VALIDADE_CHOICES)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def __str__(self):
        return self.nome

class Checklist(models.Model):
    veiculo = models.ForeignKey(ChecklistVeiculo, on_delete=models.CASCADE, related_name='checklists')
    gr = models.ForeignKey(ChecklistGR, on_delete=models.CASCADE, related_name='checklists')
    aprovado = models.BooleanField("Aprovado")
    data_aprovacao = models.DateField("Data de Aprovação/Realização", null=True, blank=True)
    data_validade_manual = models.DateField("Data de Validade Manual", null=True, blank=True)
    motivo_reprovacao = models.TextField("Motivo da Reprovação", null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    atualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Atualizado por")
    def __str__(self):
        return f"Checklist de {self.veiculo.placa} para {self.gr.nome}"
    class Meta:
        unique_together = ('veiculo', 'gr')

class TreinamentoQSMS(models.Model):
    assunto = models.CharField("Assunto do Treinamento", max_length=200)
    data_evento = models.DateField("Data do Evento")
    hora_evento = models.TimeField("Hora do Evento")
    detalhes = RichTextField("Detalhes", blank=True, null=True)
    concluido = models.BooleanField("Concluído", default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.assunto
    class Meta:
        verbose_name = "Treinamento QSMS"
        verbose_name_plural = "Treinamentos QSMS"
        ordering = ['concluido', 'data_evento', 'hora_evento']

class CertificadoQSMS(models.Model):
    nome_certificado = models.CharField("Certificado", max_length=200)
    orgao_competente = models.CharField("Órgão Competente", max_length=200)
    link_orgao = models.URLField("Link do Órgão", blank=True, null=True)
    data_validade = models.DateField("Validade")
    descricao = RichTextField("Descrição", blank=True, null=True)
    anexo = models.FileField("Anexo (PDF)", upload_to='certificados_qsm/', blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nome_certificado
    class Meta:
        verbose_name = "Certificado QSMS"
        verbose_name_plural = "Certificados QSMS"
        ordering = ['data_validade']

class EventoQSMS(models.Model):
    titulo = models.CharField("Título do Evento", max_length=200)
    data_evento = models.DateField("Data")
    hora_evento = models.TimeField("Hora")
    descricao = RichTextField("Descrição", blank=True, null=True)
    concluido = models.BooleanField("Concluído", default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.titulo
    class Meta:
        verbose_name = "Evento QSMS"
        verbose_name_plural = "Eventos QSMS"
        ordering = ['concluido', 'data_evento', 'hora_evento']

class ContratoDiverso(models.Model):
    titulo = models.CharField("Contrato", max_length=200)
    data_inicio = models.DateField("Data de Início", blank=True, null=True)
    data_fim = models.DateField("Data de Fim", blank=True, null=True)
    arquivo = models.FileField("Arquivo", upload_to='contratos_diversos/', blank=True, null=True)
    descricao = RichTextField("Descrição", blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.titulo
    class Meta:
        verbose_name = "Contrato Diverso"
        verbose_name_plural = "Contratos Diversos"
        ordering = ['-data_cadastro']

class ServicoPendente(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('INICIADO', 'Iniciado'),
        ('FINALIZADO', 'Finalizado'),
    ]
    titulo = models.CharField("Título", max_length=200)
    descricao = RichTextField("Descrição")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, related_name='tarefas_criadas', on_delete=models.SET_NULL, null=True, blank=True)
    data_inicio_tratativa = models.DateTimeField(null=True, blank=True)
    iniciado_por = models.ForeignKey(User, related_name='tarefas_iniciadas', on_delete=models.SET_NULL, null=True, blank=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    finalizado_por = models.ForeignKey(User, related_name='tarefas_finalizadas', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.titulo
    class Meta:
        verbose_name = "Serviço Pendente"
        verbose_name_plural = "Serviços Pendentes"
        ordering = ['data_criacao']

class HistoricoAcao(models.Model):
    servico = models.ForeignKey(ServicoPendente, related_name='historico_acoes', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_acao = models.DateTimeField(auto_now_add=True)
    acao = models.TextField("Ação")
    class Meta:
        ordering = ['data_acao']
    def __str__(self):
        return f"Ação em '{self.servico.titulo}' por {self.usuario.username}"
    
class ServicoPendenteQSMS(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('INICIADO', 'Iniciado'),
        ('FINALIZADO', 'Finalizado'),
    ]

    titulo = models.CharField("Título", max_length=200)
    descricao = models.TextField("Descrição")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, related_name='tarefas_criadas_qsms', on_delete=models.SET_NULL, null=True, blank=True)
    data_inicio_tratativa = models.DateTimeField(null=True, blank=True)
    iniciado_por = models.ForeignKey(User, related_name='tarefas_iniciadas_qsms', on_delete=models.SET_NULL, null=True, blank=True)
    data_finalizacao = models.DateTimeField(null=True, blank=True)
    finalizado_por = models.ForeignKey(User, related_name='tarefas_finalizadas_qsms', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Serviço Pendente QSMS"
        verbose_name_plural = "Serviços Pendentes QSMS"
        ordering = ['data_criacao']

class HistoricoAcaoQSMS(models.Model):
    servico = models.ForeignKey(ServicoPendenteQSMS, related_name='historico_acoes_qsms', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    data_acao = models.DateTimeField(auto_now_add=True)
    acao = models.TextField("Ação")

    class Meta:
        ordering = ['data_acao']

    def __str__(self):
        return f"Ação em '{self.servico.titulo}' por {self.usuario.username}"
    
class VeiculoAssegurado(models.Model):
    COBERTURA_CHOICES = [
        ('TOTAL', 'Total'),
        ('PARCIAL', 'Parcial'),
    ]

    seguradora = models.CharField("SEGURADORA", max_length=150)
    vigencia = models.DateField("VIGÊNCIA")
    placa = models.CharField("PLACA", max_length=10, unique=True)
    marca = models.CharField("MARCA", max_length=100)
    modelo = models.CharField("MODELO", max_length=100)
    ano_fabricacao = models.PositiveIntegerField("ANO Fabricação")
    ano_modelo = models.PositiveIntegerField("ANO Modelo")
    cobertura = models.CharField("COBERTURA", max_length=10, choices=COBERTURA_CHOICES)
    valor_fipe = models.PositiveIntegerField("VALOR FIPE (%)")
    franquia = models.DecimalField("FRANQUIA", max_digits=10, decimal_places=2)
    danos_materiais = models.DecimalField("DANOS MATERIAIS", max_digits=10, decimal_places=2)
    danos_corporais = models.DecimalField("DANOS CORPORAIS", max_digits=10, decimal_places=2)
    danos_morais = models.DecimalField("DANOS MORAIS", max_digits=10, decimal_places=2)
    app_morte = models.DecimalField("APP MORTE", max_digits=10, decimal_places=2)
    app_invalidez = models.DecimalField("APP INVALIDEZ", max_digits=10, decimal_places=2)
    assistencia_24h = models.CharField("ASSISTENCIA 24 HORAS (KM)", max_length=50)
    carro_reserva = models.CharField("CARRO RESERVA (Dias)", max_length=50)
    vidros = models.BooleanField("VIDROS", default=False, help_text="Marque se houver cobertura adicional de vidros.")
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.placa} - {self.seguradora}"

    class Meta:
        verbose_name = "Veículo Assegurado"
        verbose_name_plural = "Veículos Assegurados"
        ordering = ['seguradora', 'placa']

class BlackList(models.Model):
    nome_completo = models.CharField("Nome Completo", max_length=150)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    motivo_bloqueio = models.TextField(verbose_name="Motivo do Bloqueio")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")

    def __str__(self):
        return f"{self.nome_completo} - {self.cpf}"

    class Meta:
        verbose_name = "Black-List"
        verbose_name_plural = "Black-List"
        ordering = ['-data_cadastro']

class Permissoes(models.Model):
    class Meta:
        managed = False
        permissions = [
            ("can_view_dashboard", "Pode visualizar o Dashboard (Início)"),
            ("can_view_risk_management_menu", "Pode visualizar o menu Gerenciamento de Risco"),
            ("can_view_pgr_list", "Pode visualizar a lista de PGRs"),
            ("can_view_gr_list", "Pode visualizar a lista de Gerenciadoras de Risco"),
            ("can_view_rotogramas_list", "Pode visualizar a lista de Rotogramas"),
            ("can_view_checklist_page", "Pode visualizar a página de Checklist"),
            ("can_view_servicos_pendentes", "Pode visualizar a página de Serviços Pendentes"),
            ("can_add_pgr", "Pode adicionar novo PGR"),
            ("can_change_pgr", "Pode editar PGR"),
            ("can_delete_pgr", "Pode excluir PGR"),
            ("can_add_gr", "Pode adicionar nova Gerenciadora de Risco"),
            ("can_add_rotograma", "Pode adicionar novo Rotograma"),
            ("can_add_checklist_veiculo", "Pode adicionar veículo no Checklist"),
            ("can_add_checklist_gr", "Pode adicionar GR no Checklist"),
            ("can_add_checklist", "Pode adicionar/editar um Checklist"),
            ("can_add_servico_pendente", "Pode adicionar nova Tarefa Pendente"),
            ("can_start_servico_pendente", "Pode iniciar tratativa de Tarefa"),
            ("can_update_action_servico_pendente", "Pode gravar ação em Tarefa"),
            ("can_finalize_servico_pendente", "Pode finalizar Tarefa"),
            ("can_view_security_menu", "Pode visualizar o menu Security"),
            ("can_view_seguros_list", "Pode visualizar a lista de Seguros"),
            ("can_view_sinistros_list", "Pode visualizar a lista de Sinistros"),
            ("can_view_ddr_list", "Pode visualizar a lista de DDR"),
            ("can_view_contratos_list", "Pode visualizar a lista de Contratos Diversos"),
            ("can_view_veiculos_assegurados", "Pode visualizar Veículos Assegurados"),
            ("can_add_veiculo_assegurado", "Pode adicionar Veículo Assegurado"),
            ("can_change_veiculo_assegurado", "Pode editar Veículo Assegurado"),
            ("can_add_seguro", "Pode adicionar novo Seguro"),
            ("can_view_anexos_seguro", "Pode visualizar anexos dos Seguros"),
            ("can_add_sinistro", "Pode adicionar novo Sinistro"),
            ("can_change_sinistro", "Pode editar Sinistro"),
            ("can_add_ddr", "Pode adicionar nova Averbação (DDR)"),
            ("can_add_contrato", "Pode adicionar novo Contrato Diverso"),
            ("can_change_contrato", "Pode editar Contrato Diverso"),
            ("can_view_qsms_menu", "Pode visualizar o menu QSMS"),
            ("can_view_treinamentos_list", "Pode visualizar a Agenda de Treinamentos"),
            ("can_view_certificados_list", "Pode visualizar a lista de Certificados"),
            ("can_view_eventos_list", "Pode visualizar o Calendário de Eventos"),
            ("can_view_servicos_pendentes_qsms", "Pode visualizar Serviços Pendentes de QSMS"),
            ("can_add_servico_pendente_qsms", "Pode adicionar Tarefa Pendente de QSMS"),
            ("can_start_servico_pendente_qsms", "Pode iniciar tratativa de Tarefa de QSMS"),
            ("can_update_action_servico_pendente_qsms", "Pode gravar ação em Tarefa de QSMS"),
            ("can_finalize_servico_pendente_qsms", "Pode finalizar Tarefa de QSMS"),
            ("can_add_treinamento", "Pode adicionar novo Treinamento"),
            ("can_change_treinamento", "Pode editar Treinamento"),
            ("can_add_certificado", "Pode adicionar novo Certificado"),
            ("can_change_certificado", "Pode editar Certificado"),
            ("can_add_evento", "Pode adicionar novo Evento"),
            ("can_change_evento", "Pode editar Evento"),
            ("can_view_downloads", "Pode visualizar a página de Downloads"),
            ("can_view_blacklist", "Pode visualizar a Black-List"),
        ]