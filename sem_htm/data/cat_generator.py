import random as rand

def generate_cat_exemplars(prototype_length, feature_sparcity, n_exemplars, exemplar_distortion):
    # generate category prototype
    _prototype = [0 for i in range(prototype_length)]

    for i in range(int(feature_sparcity*prototype_length)):
        _feature_flag = False
        while not _feature_flag:
            _index = rand.randint(0, prototype_length-1)

            if _prototype[_index] == 0:
                _prototype[_index] = 1
                _feature_flag = True
        
    # generate category exemplars by fliping prototype bits
    _exemplars = []

    for i in range(n_exemplars):
        _exemplar = _prototype.copy()
        for j in range(int(exemplar_distortion*prototype_length)):
            _index = rand.randint(0, prototype_length-1)
            _exemplar[_index] = int(not _exemplar[_index])
        _exemplars.append(_exemplar)
    
    return _exemplars

    