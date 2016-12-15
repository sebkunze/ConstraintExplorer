from yaml import load_all
        
def read_terminated_symbooglix_states(path):
    stream = file(path,'r')
    termiated_symbooglix_states = load_all(stream)
    file.close
    return termiated_symbooglix_states

class ConstraintsIterator: # TODO: Rename!
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