from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {})

@register.filter
def muscle_slugs_str(rutina):
    """Devuelve los slugs de músculos de una rutina como string CSV, derivados de sus ejercicios."""
    slugs = (
        rutina.ejercicios_rutina
        .values_list('ejercicio__grupo_muscular__slug', flat=True)
        .distinct()
    )
    return ','.join(s for s in slugs if s)
