class TestInfo:

    def __init__(self, trajectory, target, sources, satisfying_values, differential_values):
        self.trajectory          = trajectory
        self.target              = target
        self.sources             = sources
        self.satisfying_values   = satisfying_values
        self.differential_values = differential_values

    def __str__(self):
        return "%s(trajectory:$s, target:%s, origins:%s, values(satisfying):%s, values(differential):%s" % (
            self.__class__.__name__,
            self.trajectory,
            self.target,
            reduce(lambda x,y: str(x) + str(y), self.sources, ''),
            reduce(lambda x,y: str(x) + str(y), self.values, ''),
            self.differential_values)


class TestInstance:

    def __init__(self, state, values):
        self.state              = state
        self.overlapping_values = values

    def __str__(self):
        return "%s(state:%s, values:%s)" % (
            self.__class__.__name__,
            self.state,
            self.values)