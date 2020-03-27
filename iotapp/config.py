def validate_devices(devices):
    ok = dict()
    ko = dict()
    for key, value in devices.items():
        error = validate_device(key, value)
        if error:
            ko[key] = dict(value=value, error=error)
        else:
            ok[key] = value
    entities = dict()
    errors = []
    for key, value in ok.items():
        for entity in value.get('entities', dict()).keys():
            if entity in entities:
                error = 'Duplicated entity.'
                ko[key] = dict(value=value, error=error)
                errors.append(key)
            else:
                entities[entity] = key
    for device_name in errors:
        del ok[device_name]
    return ok, ko


def validate_device(key, value):
    if 'type' not in value:
        return 'Missing type.'
    if not isinstance(value['type'], str):
        return 'Wrong type.'
    return None


def validate_apps(devices, apps):
    ok = dict()
    ko = dict()
    entities = get_entities(devices)
    for key, value in apps.items():
        value['entities'] = value.get('entities', [])
        error = validate_app(key, value, entities)
        if error:
            ko[key] = dict(value=value, error=error)
        else:
            ok[key] = value
    return ok, ko


def validate_app(app_name, app, entities):
    available_entities = list(entities.keys())
    if 'module' not in app:
        return 'Missing module.'
    if 'class' not in app:
        return 'Missing class.'
    for entity in app['entities']:
        if entity not in available_entities:
            return 'Entity "{}" not available.'.format(entity)
    return None


def get_entities(devices):
    entities = dict()
    for key, value in devices.items():
        for entity in value.get('entities', dict()).keys():
            entities[entity] = key
    return entities
