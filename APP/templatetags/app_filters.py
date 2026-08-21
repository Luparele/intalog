from django import template
import locale

register = template.Library()

@register.filter(name='br_currency')
def br_currency(value):
    """
    Filtro para formatar um número para o padrão monetário brasileiro.
    Exemplo: 28018.13 -> 28.018,13
    """
    try:
        # Converte o valor para float para garantir que a formatação funcione
        value = float(value)
        # Usa a formatação com vírgula de milhar e 2 casas decimais
        formatted_value = f'{value:,.2f}'
        # Inverte os separadores para o padrão brasileiro
        # Troca a vírgula por um placeholder, o ponto pela vírgula, e o placeholder pelo ponto
        return formatted_value.replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        # Se o valor não for um número, retorna o valor original
        return value