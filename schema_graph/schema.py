from django.apps import apps


def get_app_models():
    for app in apps.get_app_configs():
        for model in app.get_models():
            yield app, model


def get_model_id(model, app=None):
    if not app:
        app = apps.get_app_config(model._meta.app_label)

    return (app.name, model.__name__)


def get_schema():
    nodes = []
    foreign_keys = []
    one_to_one = []
    many_to_many = []
    inheritance = []

    for app, model in get_app_models():
        model_id = get_model_id(model, app)
        nodes.append(model_id)

        # Subclassing
        if model._meta.parents:
            for parent_model in model._meta.parents:
                parent_model_id = get_model_id(parent_model)
                relationship = model_id, parent_model_id
                inheritance.append(relationship)

        for field in model._meta.get_fields():
            if not field.is_relation:
                continue
            # Skip fields defined on superclasses
            if field.model != model:
                continue
            related_model = field.related_model
            related_model_id = get_model_id(related_model)
            relationship = (model_id, related_model_id)
            # Foreign key
            if field.many_to_one:
                foreign_keys.append(relationship)
            # One-to-one
            elif field.one_to_one and not field.auto_created:
                one_to_one.append(relationship)
            # Many-to-many
            elif field.many_to_many and not field.auto_created:
                many_to_many.append(relationship)

    return (
        sorted(nodes),
        sorted(foreign_keys),
        sorted(one_to_one),
        sorted(many_to_many),
        sorted(inheritance),
    )
