from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Criamos tuplas para as opções de 'choices' para evitar erros de digitação
ESTADOS_BRASILEIROS = [
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
    uf = models.CharField("UF", max_length=2, choices=ESTADOS_BRASILEIROS)
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
        # ALTERAÇÃO AQUI: Agora usa o telefone_corporativo
        if not self.telefone_corporativo:
            return ""
        
        numero_limpo = self.telefone_corporativo.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        return f"https://wa.me/{numero_limpo}"

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"


# Modelos para Cadastro de Clientes
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
    # NOVO CAMPO DE RELACIONAMENTO
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='seguros', verbose_name="Cliente", null=True, blank=True)

    tipo_apolice = models.CharField("Tipo de Apólice", max_length=100)
    corretora = models.CharField("Corretora", max_length=100)
    corretor = models.CharField("Corretor", max_length=100)
    tel_corretor = models.CharField("Telefone do Corretor", max_length=20)
    email_corretor = models.EmailField("E-mail do Corretor")
    vigencia = models.DateField("Vigência do Seguro")
    descricao = models.TextField("Descrição do Seguro")
    apolice_anexo = models.FileField("Anexo da Apólice (PDF)", upload_to='apolices/', blank=True, null=True)
    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True, null=True, blank=True)

    # Dentro da classe Seguro em models.py
    def __str__(self):
        if self.cliente:
            return f"{self.tipo_apolice} - {self.cliente.cliente}"
        return f"{self.tipo_apolice} - (Sem cliente associado)"

    class Meta:
        verbose_name = "Seguro"
        verbose_name_plural = "Seguros"
        ordering = ['cliente__cliente', 'tipo_apolice'] # Ordena por nome do cliente, depois por apólice

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

# Em APP/models.py

class GerenciadoraRisco(models.Model):
    nome = models.CharField("Gerenciadora de Risco", max_length=150)
    
    # Validade de pesquisa de Condutor
    validade_condutor_clt = models.PositiveIntegerField("Validade de pesquisa de Condutor CLT")
    validade_condutor_agregado = models.PositiveIntegerField("Validade de pesquisa de Condutor Agregado")
    validade_condutor_terceiro = models.CharField("Validade de pesquisa de Condutor Terceiro", max_length=50, default="Por Embarque")

    # Validade de pesquisa de Veículo
    validade_veiculo_frota = models.PositiveIntegerField("Validade de pesquisa de Veículo Frota")
    validade_veiculo_agregado = models.PositiveIntegerField("Validade de pesquisa de Veículo Agregado")
    validade_veiculo_terceiro = models.CharField("Validade de pesquisa de Veículo Terceiro", max_length=50, default="Por Embarque")
    
    # Validade de Checklist de Veículo
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