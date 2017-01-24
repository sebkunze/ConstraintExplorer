from z3 import Bool, Int, And, Implies, Not, Solver, sat

from core.utils import logger

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
        return "\n %s\n id: %s\n constraints: %s" % (
            self.yaml_object_header(), self.id, self.constraints)

    def yaml_object_header(self):
        return "!!python/object:core.object.data.solver.SymbolicState"

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def find_overlapping_states(self, states):
        return [s for s in states if self.is_overlapping_state(s) and not self.is_equivalent_state(s)]

    def is_overlapping_state(self, state):
        s = Solver()

        for constraint in self.constraints:
            s.add(constraint.z3constraint)

        for constraint in state.constraints:
            s.add(constraint.z3constraint)

        return True if s.check() == sat else False

    def is_equivalent_state(self, state): # TODO: Something seems to be wrong here!
        return True if set(self.constraints) == set(state.constraints) else False

class Constraint:
    """class encapsulating a z3 constraint"""
    def __init__(self, z3constraint):
        self.z3constraint = z3constraint

    def __repr__(self):
        constraint = str(self.z3constraint)
        constraint = constraint.replace('\n',' ')
        constraint = "'" + constraint + "'"

        return "\n  %s" % (
            constraint)

    def yaml_object_header(self):
        return "!!python/object:core.object.data.solver.Constraint"

    def constraint(self):
        return self.z3constraint