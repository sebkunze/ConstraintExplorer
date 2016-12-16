from z3          import Solver, sat

def check_overlapping_states(variantX, variantY):
    statesInVariantX = len(variantX.terminatedStates)
    statesInVariantY = len(variantY.terminatedStates)
    
    matrix = [[None for x in range(statesInVariantX)] for y in range(statesInVariantY)]
    
    for y in range(statesInVariantY):
        for x in range(statesInVariantX):
            stateX = variantX.terminatedStates[x]
            stateY = variantY.terminatedStates[y]
            matrix[y][x] = check_overlapping_state(stateX, stateY)
    
    return matrix

def check_overlapping_state(stateX, stateY):
    s = Solver()
    
    for constraint in stateX['constraints']:
        s.add(constraint)
        
    for constraint in stateY['constraints']:
        s.add(constraint)
    
    if s.check() == sat:
        return True
    else:
        return False

# TODO: Check possibility of map-reduce algorithm?
def check_new_states(variantX, variantY):
    statesInVariantX = len(variantX.terminatedStates)
    statesInVariantY = len(variantY.terminatedStates)
    
    matrix = [[None for x in range(statesInVariantX)] for y in range(statesInVariantY)]
    
    for y in range(statesInVariantY):
        for x in range(statesInVariantX):
            stateX = variantX.terminatedStates[x]
            stateY = variantY.terminatedStates[y]
            matrix[y][x] = not check_equal_states_constraints(stateX, stateY)
    
    return matrix

def check_equal_states_constraints(stateX, stateY):
    return True if set(stateX.constraints) == set(stateY.constraints) else False
    
def generate_list_of_equivalent_states(stateX, statesY):
    # TODO: Check for filter function!
    s = []
    for stateY in statesY:
        s.append(check_equal_states_constraints(stateX, stateY))
    
    return s

def check_overlapping_constraints(stateX, stateY):
    s = Solver()
    
    s.push()
    for constraint in stateX.constraints:
        s.add(constraint)
        
    for constraint in stateY.constraints:
        s.add(constraint)
    
    z = True if s.check() == sat else False
    
    s.pop()
    
    return z
    
def generate_list_of_overlapping_states(stateX, statesY):
    s = []
    for stateY in statesY:
        s.append(check_overlapping_constraints(stateX, stateY))
        
    return s