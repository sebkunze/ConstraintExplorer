class TerminatedState:
    def __init__(self, state_id, memory, constraints):
        self.state_id    = state_id
        self.memory      = memory
        self.constraints = constraints
        
    def __repr__(self):
            return "%s(state_id=%r, memory=%r, constraints=%r)" % (
                self.__class__.__name__, self.state_id, self.memory, self.constraints)

class Constraint:
    def __init__(self, variable, operator, value):
        self.variable = variable
        self.operator = operator
        self.value    = value
        
    def __repr__(self):
        return "%s(variable=%r, operator=%r, value=%r)" % (
            self.__class__.__name__, self.variable, self.operator, self.value)

def readTerminatedStates(path):
    stream = file(path,'r')
    termiatedStates = yaml.load_all(stream)
    file.close
    return termiatedStates

def getConstraints(terminatedState):
    constraints = []
    for constraint in terminatedState.constraints['constraints']:
        x = constraint['origin'][:-1].split()
        _, _, _, var, op, val = x
        c = Constraint(var, op, val)
        constraints.append(c)
    return constraints

from collections import defaultdict
from z3          import *
import yaml # TODO: Fix import statement

terminatedStates = readTerminatedStates('basic-001/Symbooglix.TerminatedWithoutError.yml')


query = {}
for terminatedState in terminatedStates:
    constraints = getConstraints(terminatedState)
    print '### ' + str(terminatedState.state_id) + ' ###'
    print constraints