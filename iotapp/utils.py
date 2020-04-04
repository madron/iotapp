import json as jsonlib
from jinja2 import Template


def get_template_value(value, template=None, json=True):
        if template:
            data = value
            if json:
                data = jsonlib.loads(value)
            return Template(template).render(value=data)
        return value
