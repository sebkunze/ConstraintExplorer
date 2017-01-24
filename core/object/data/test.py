class Test:
    def __init__(self, state):
        self.state = state

    def __repr__(self):
        return "%s(state=%s)" % (
            self.__class__.__name__, self.state)

class TestArtefact(Test):
    """class representing new test input data"""
    def __init__(self, state, values):
        self.state  = state
        self.values = values

    def __repr__(self):
        return "---\n%s\ntarget:%s\nvalues:%s" % (
            self.__class__.__name__, self.state, self.values)

    def yaml_object_header(self):
        return "!!python/object:core.object.data.test.TestArtefact"

class TestRefinement(Test):
    """class representing modified test input data"""

    def __init__(self, state, origins, values):
        self.state   = state
        self.origins = origins
        self.values  = values

    def __repr__(self):
        origins = reduce(lambda x,y: str(x) + str(y), self.origins)
        return "---\n%s\ntarget:%s\norigins:%s\nvalues:%s" % (
            self.yaml_object_header(), self.state, origins, self.values)

    def yaml_object_header(self):
        return "!!python/object:core.object.data.test.TestRefinement"