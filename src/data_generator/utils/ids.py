import uuid

def generate_uuid():
    return str(uuid.uuid4())

def generate_uuids(count):
    return [str(uuid.uuid4()) for _ in range(count)]
