instances = []

def register(cls):
    print('registering', cls.__name__)
    instances.append(cls())
    return cls