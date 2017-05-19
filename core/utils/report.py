import json

CREATE = "create"

SKIP   = "skip"

ADJUST = "adjust"

data = {}

states = {CREATE : 0, SKIP : 0, ADJUST : 0}


def dump(path):

    # write data to file.
    with open(path, 'w') as f:
        json.dump(states, f)