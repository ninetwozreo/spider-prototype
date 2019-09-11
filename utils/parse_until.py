import types

def to_dict(dumyself):
    result = {}
    for a in dir(dumyself):

        # filter inner field by fieldname
        if a.startswith('_') or a == 'metadata':
            continue

        v = getattr(dumyself, a)

        # filter inner field by value type
        if callable(v):
            continue


        if type(v) not in (type(None),str, int,float):
            continue

        result[a] = getattr(dumyself, a)
    return result
