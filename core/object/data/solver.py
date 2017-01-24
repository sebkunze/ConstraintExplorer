class Program:
    """class representing an analysed program"""
    def __init__(self, symbolic_states = []):
        self.symbolic_states = symbolic_states

    def __repr__(self):
        return "%s(terminated_states: %s)" % (
            self.__class__.__name__, self.symbolic_states)

    def __str__(self):
        return "%s(terminated_states: %s)" % (
            self.__class__.__name__, self.symbolic_states)

    def add_symbolic_state(self, symbolic_state):
        self.symbolic_states.append(symbolic_state)


class SymbolicState:
    """class representing a symbolic state"""
    def __init__(self, id = None, constraints = []):
        self.id          = id
        self.constraints = constraints

    def __repr__(self):
        return "\n\t%s\n\tid: %s\n\tconstraints: %s" % (
            self.yaml_object_header(), self.id, self.constraints)

    def yaml_object_header(self):
        return "!!python/object:core.object.data.solver.SymbolicState"

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

class Constraint:
    """class encapsulating a z3 constraint"""
    def __init__(self, z3constraint):
        self.z3constraint = z3constraint

    def __repr__(self):
        return "\n\t\t%s\n\t\t%s" % (
            self.yaml_object_header(), str(self.z3constraint).replace('/n',''))

    def yaml_object_header(self):
        return "!!python/object:core.object.data.solver.Constraint"