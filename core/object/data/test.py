class Test:
    """class representing modified test input data"""

    def __init__(self, target, origins, values):
        self.target   = target
        self.origins = origins
        self.values  = values

    def __repr__(self):
        origins = reduce(lambda x,y: str(x) + str(y), self.origins)

        return "%s(target:%s, origins:%s, values:%s)" % (
            self.__class__.__name__, self.target, origins, self.values)