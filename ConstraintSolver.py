class TerminatedSymbooglixState: # TODO: Move this somehow without destroying dependencies!
    def __init__(self, state_id, memory, constraints):
        self.state_id    = state_id
        self.memory      = memory
        self.constraints = constraints
                       
from core         import symbooglix
from core.variant import * # TODO: Fix naming, e.g., productline.variant!
from collections  import defaultdict 
from z3           import * # TODO: Fix dependencies!

# Specifying terminated states.
paths = ['sample/basic-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/highWater-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/lowWater-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/methane-001/Symbooglix.TerminatedWithoutError.yml'
        ,'sample/premium-001/Symbooglix.TerminatedWithoutError.yml']
        
# Reading specified terminated states.
variants = []
for path in paths:
    states  = symbooglix.readTerminatedStates(path)
    variant = translateToVariant(states)
    variants.append(variant)

# Feeding read terminated states to z3
# newStateMatrix = checkNewStates(variants[0], variants[1])

# TODO: Work on map-reduce algorithm!

# ----- sketching map-reduce algorithm -----
# - iterate over states of given variantY
# - check whether state's constraints are equivalent to any set of constraints
# - if so; test cases can be skipped
# - if no; check whether variantY's constraints are overlapping to any of variantX's constraints
#   - if so; test cases may be refined
#   - if no; test cases must be created


# TODO: Define package to abstract algorithm!
# for z in range(len(newStateMatrix)):
#     b = reduce(lambda x, y: True if x and y else False, newStateMatrix[z])
#     print "Retest state " + str(z) + ":" + str(b)

statesX = variants[1].terminatedStates
statesY = variants[2].terminatedStates

equivalentStates  = []
newStates         = range(len(statesY))
overlappingStates = []

print "Assuming number of covered states: " + str(len(statesX))
print "Number of states to be covered: " + str(len(statesY))

for stateY in statesY:
    equivalentToStatesInX = generateListOfEquivalentStates(stateY, statesX)
    pos = [equivalentToStatesInX.index(y) for y in equivalentToStatesInX if y]
    if pos:
        equivalentStates.append((stateY['state_id'][0], pos[0]))

print "equivalent states; test cases to be skipped:\t" + str(equivalentStates)

for stateY in statesY:
    overlappingWithStateInX = generateListOfOverlappingStates(stateY, statesX)
    pos = [overlappingWithStateInX.index(y) for y in overlappingWithStateInX if y]
    if pos:
        overlappingStates.append((stateY['state_id'][0], pos[0]))
        newStates.remove(stateY['state_id'][0])

overlappingStates = filter(lambda x: x not in equivalentStates, overlappingStates)
print "overlapping states; test cases to be refined:\t" + str(overlappingStates)

print "new states; test cases to be created:\t\t" + str(newStates)