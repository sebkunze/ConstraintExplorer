# TODO: Move this somehow without destroying dependencies!
class TerminatedSymbooglixState:
    def __init__(self, state_id, memory, constraints):
        self.state_id    = state_id
        self.memory      = memory       # TODO: Figure out of memory is required!
        self.constraints = constraints

    # TODO: Figure out if the following code is necessary!
    def get_state_id(self):
        return self.state_id

    def get_memory(self):
        return self.memory

    def get_constraints(self):
        return self.constraints
                       
from core         import symbooglix
from core         import interpreter
from core.variant import * # TODO: Fix naming, e.g., productline.variant!
from z3           import * # TODO: Fix dependencies!

# Specifying program variants.
paths = ['sample/basic-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/highWater-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/lowWater-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/methane-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/premium-001/Symbooglix.TerminatedWithoutError.yml']

# Interpreting specified program variants.
programs = []
for path in paths:
    states  = symbooglix.readTerminatedStates(path)
    program = interpreter.translate_to_program(states)
    programs.append(program)

# Feeding interpreted program variants to z3
statesX = programs[4].terminated_states
statesY = programs[3].terminated_states

equivalentStates  = []
newStates         = range(len(statesY))
overlappingStates = []

print "Assuming number of covered states: " + str(len(statesX))
print "Number of states to be covered: " + str(len(statesY))

for stateY in statesY:
    equivalentToStatesInX = generateListOfEquivalentStates(stateY, statesX)
    pos = [equivalentToStatesInX.index(y) for y in equivalentToStatesInX if y]
    if pos:
        equivalentStates.append((stateY.id, pos[0]))

print "equivalent states; test cases to be skipped:\t" + str(equivalentStates)

for stateY in statesY:
    overlappingWithStateInX = generateListOfOverlappingStates(stateY, statesX)
    pos = [overlappingWithStateInX.index(y) for y in overlappingWithStateInX if y]
    if pos:
        overlappingStates.append((stateY.id, pos[0]))
        newStates.remove(stateY.id)

overlappingStates = filter(lambda x: x not in equivalentStates, overlappingStates)

print "overlapping states; test cases to be refined:\t" + str(overlappingStates)
print "new states; test cases to be created:\t\t" + str(newStates)