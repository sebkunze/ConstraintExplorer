class TerminatedSymbooglixState:

    def __init__(self, state_id, status, memory, constraints):
        self.state_id    = state_id
        self.status      = status
        self.memory      = memory
        self.constraints = constraints

    def __repr__(self):
        return "%s(state_id: %s, status: %s, memory: %s, constraints: %s)" % (
            self.__class__.__name__, self.state_id, self.status, self.memory, self.constraints)


class SymbooglixGlobalsIterator:

    def __init__(self, terminated_symbooglix_state):
        self.memory = terminated_symbooglix_state.memory['globals']


class SymbooglixConstraintIterator:

    def __init__(self, terminated_symbooglix_state):
        self.constraints = terminated_symbooglix_state.constraints['constraints']

    def __iter__(self):
        self.n = 0
        return self

    def next(self):
        if self.n < len(self.constraints):
            constraint = self.constraints[self.n]
            self.n += 1
            return constraint
        else:
            raise StopIteration