from yaml import load_all


class TerminatedSymbooglixState:
    def __init__(self, state_id, memory, constraints):
        self.state_id    = state_id
        self.memory      = memory       # TODO: Figure out of memory is required!
        self.constraints = constraints


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


def read_terminated_symbooglix_states(path):
    stream = file(path,'r')
    termiated_symbooglix_states = load_all(stream)
    file.close
    return termiated_symbooglix_states