from enum import Enum

class TestInfo:

    def __init__(self, trajectory, target, sources, satisfying_values):
        self.trajectory        = trajectory
        self.target            = target
        self.sources           = sources
        self.satisfying_values = satisfying_values

    def __str__(self):
        return "%s(trajectory:$s, target:%s, origins:%s, values:%s)" % (
            self.__class__.__name__,
            self.trajectory,
            self.target,
            reduce(lambda x,y: str(x) + str(y), self.sources, ''),
            reduce(lambda x,y: str(x) + str(y), self.values, ''))


class TestInstance:

    def __init__(self, state, values):
        self.state              = state
        self.overlapping_values = values

    def __str__(self):
        return "%s(state:%s, values:%s)" % (
            self.__class__.__name__,
            self.state,
            self.values)


# TODO: Implement enumerated type on Haskell side!
class AssertionType(Enum):
    ADD    = "ADD"
    REMOVE = "REMOVE"
    MODIFY = "MODIFY"
    NONE   = "NONE"