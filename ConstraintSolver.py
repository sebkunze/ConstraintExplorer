class TerminatedSymbooglixState:
    def __init__(self, state_id, memory, constraints):
        self.state_id    = state_id
        self.memory      = memory
        self.constraints = constraints

class Variant: # TODO: Find more appropiate name!
    def __init__(self):
        self.globals          = set()
        self.variables        = set()
        self.terminatedStates = []

    def __repr__(self):
        return "%s(\n globals=%r,\n variables=%r,\n terminatedStates=%r)" % (self.__class__.__name__, self.globals, self.variables, self.terminatedStates)

    def appendGlobals(self, terminatedSymbooglixState): # TODO: Rename to extend
        for c in terminatedSymbooglixState.constraints['constraints']:
            constraint = self.unpackConstraint(c)
            while True:
                val = constraint[2] if not constraint[2].endswith(')') else constraint[2][:-1]
                self.globals |= set([Int(val)])
                constraint = constraint[4:]
                if not len(constraint) > 0:
                    break            
        # self.globals |= set([Int(g) for g in terminatedSymbooglixState.memory['globals'] if g not in self.globals])

    def getGlobal(self, gbl):
        # TODO: Use function index instead!
        lst = [g for g in self.globals if g == Int(gbl)]
        return lst[0]

    def appendVariables(self, terminatedSymbooglixState): # TODO: Rename to extend
        for c in terminatedSymbooglixState.constraints['constraints']:
            constraint = self.unpackConstraint(c)
            while True:
                var = constraint[0] if not constraint[0].startswith('!(') else constraint[0][2:]
                self.variables |= set([Int(var)])
                constraint = constraint[4:]
                if not len(constraint) > 0:
                    break
            
    def getVariable(self, var):
        # TODO: Use function index instead!
        lst = [v for v in self.variables if v == Int(var)]
        return lst[0]

    def addTerminatedState(self, terminatedSymbooglixState):
        # TODO: Structure this mess!
        d = defaultdict(list)
        d['state_id'].append(terminatedSymbooglixState.state_id)
        for c in terminatedSymbooglixState.constraints['constraints']: # TODO: Naming
            constraint = self.unpackConstraint(c)
            if self.isConjoinedConstraint(constraint): # conjoined constraints
                constraints = []
                while True:                     # do-while body
                    var = constraint[0] if not constraint[0].startswith('!(') else constraint[0][2:]
                    op  = constraint[1]
                    val = constraint[2] if not constraint[2].endswith(')') else constraint[2][:-1]
                    c   = self.genConstraint(var, op, val)
                    constraints.append(c)
                    constraint = constraint[4:] # TODO: Find a more appropiate name!
                    if not len(constraint) > 0 : # do-while condition
                        break
                
                j = None
                for c in constraints:
                    if j == None:
                        j = c
                    else:
                        j = And(j, c)
                
                d['constraints'].append(j)
            else: # non-conjoined constraints
                var = constraint[0]
                op  = constraint[1]
                val = constraint[2]
                c = self.genConstraint(var, op, val)
                
                d['constraints'].append(c)
                
        self.terminatedStates.append(d)
    
    def unpackConstraint(self, constraint): # TODO: Rename!
        x = constraint['origin'][:-1].split()
        x = x[3:]
        return x
            
    def isConjoinedConstraint(self, constraint):
        return len(constraint) > 3 # TODO: Check for keyword as well
        
    def genConstraint(self, var, op, val):
        if op == '==':
           if val.isdigit():
               return self.getVariable(var) == val
           else:
               return self.getVariable(var) == self.getGlobal(val) 
        else:
            if val.isdigit():
                return self.getVariable(var) != val
            else:
                return self.getVariable(var) != self.getGlobal(val)
                       
def translateToVariant(terminatedSymbooglixState): # Rename function to something more appropiate!
    v = Variant()
    for state in terminatedSymbooglixState:
        v.appendGlobals(state)      # TODO: Split into two separate function calls
        v.appendVariables(state)    # TODO: Split into two separate function calls!
        v.addTerminatedState(state) # TODO: Split into two separate function calls!
    return v

def checkOverlappingStates(variantX, variantY):
    # TODO: Check out sparse matrix representation!
    statesInVariantX = len(variantX.terminatedStates)
    statesInVariantY = len(variantY.terminatedStates)
    
    matrix = [[None for x in range(statesInVariantX)] for y in range(statesInVariantY)]
    
    for y in range(statesInVariantY):
        for x in range(statesInVariantX):
            stateX = variantX.terminatedStates[x]
            stateY = variantY.terminatedStates[y]
            matrix[y][x] = checkOverlappingState(stateX, stateY)
    
    return matrix

def checkOverlappingState(stateX, stateY):
    s = Solver()
    
    for constraint in stateX['constraints']:
        s.add(constraint)
        
    for constraint in stateY['constraints']:
        s.add(constraint)
    
    if s.check() == sat:
        return "refine"
    else:
        return "create"

def checkNewStates(variantX, variantY):
    # TODO: Check out sparse matrix representation!
    statesInVariantX = len(variantX.terminatedStates)
    statesInVariantY = len(variantY.terminatedStates)
    
    matrix = [[None for x in range(statesInVariantX)] for y in range(statesInVariantY)]
    
    for y in range(statesInVariantY):
        for x in range(statesInVariantX):
            stateX = variantX.terminatedStates[x]
            stateY = variantY.terminatedStates[y]
            matrix[y][x] = checkNewState(stateX, stateY)
    
    return matrix

def checkNewState(stateX, stateY):
    if set(stateX['constraints']) == set(stateY['constraints']):
        return "skip"
    else:
        return "test"

def readTerminatedStates(path):
    stream = file(path,'r')
    termiatedStates = load_all(stream)
    file.close
    return termiatedStates

from yaml        import load_all 
from collections import defaultdict
from z3          import *

# Specifying terminated states.
paths = ['sample/basic-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/highWater-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/lowWater-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/methane-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/premium-001/Symbooglix.TerminatedWithoutError.yml']
        
# Reading specified terminated states.
variants = []
for path in paths:
    states = readTerminatedStates(path)
    variant = translateToVariant(states)
    variants.append(variant)

# Feeding read terminated states to z3
newStateMatrix = checkNewStates(variants[0], variants[1])

for x in newStateMatrix:
    print x

overlappingStateMatrix = checkOverlappingStates(variants[0], variants[1])

for x in overlappingStateMatrix:
    print x 