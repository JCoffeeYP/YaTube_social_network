from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def uglify(value) -> str:
    result = []
    for i in range(len(value)):
        if i % 2 == 1:
            result.append(value[i].upper())
        else:
            result.append(value[i].lower())
    return(''.join(result))
