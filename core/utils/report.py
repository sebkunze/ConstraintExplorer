import json
import os

data = {"SKIP" : 0, "ADJUST" : 0, "CREATE" : 0}

def to_be_skipped_test():
    data['SKIP'] += 1


def to_be_adjusted_test():
    data['ADJUST'] += 1


def to_be_created_test():
    data['CREATE'] += 1


def dump(path):
    with open(path, 'w') as f:
        json.dump(data, f)