from enum import Enum

class TestInfo:

    def __init__(self, target, sources, values):
        self.sources = sources
        self.target  = target
        self.values  = values

    def __str__(self):
        return "%s(target:%s, origins:%s, values:%s)" % (
            self.__class__.__name__, self.target, reduce(lambda x,y: str(x) + str(y), self.sources, ''), self.values)


class TestInstance:

    def __init__(self, assertion_conditions, assertion_type, state):
        self.assertion_conditions = assertion_conditions
        self.assertion_type       = assertion_type
        self.state                = state

    def __str__(self):
        return "%s(assertions:%s, state:%s)" % (
            self.__class__.__name__, reduce(lambda x,y: str(x) + str(y), self.assertions, ''), self.state)


# TODO: Implement enumerated type on Haskell side!
class AssertionType(Enum):
    ADD    = "ADD"
    REMOVE = "REMOVE"
    MODIFY = "MODIFY"
    NONE   = "NONE"