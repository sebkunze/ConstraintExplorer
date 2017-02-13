class TestWrapper:
    """class wrapping tests to parse output as a list tests instead of a sequence of multiple documents."""
    def __init__(self, tests):
        self.tests = tests


class Test:

    def __init__(self, target, origins, values):
        self.target  = target
        self.origins = origins
        self.values  = values

    def __repr__(self):
        return "%s(target:%s, origins:%s, values:%s)" % (
            self.__class__.__name__, self.target, reduce(lambda x,y: str(x) + str(y), self.origins, ''), self.values)