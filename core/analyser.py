from z3 import Solver, sat

def analyse_program_states(program_x, program_y):

    # specify list of equivalent states.
    equivalent_states = []

    # specify list of overlapping states.
    overlapping_states = []

    # specify list of new states.
    new_states = []

    # find equivalent states.
    for state_y in program_y.terminated_states:
        states_x = find_equivalent_states(state_y, program_x.terminated_states)
        if states_x:
            for state_x in states_x:
                equivalent_states.append((state_x, state_y))

    # find overlapping states.
    for state_y in program_y.terminated_states:
        states_x = find_overlapping_states(state_y, program_x.terminated_states)
        if states_x:
            for state_x in states_x:
                # filter equivalent states.
                if (state_x, state_y) not in equivalent_states:
                    overlapping_states.append((state_x, state_y))
        else:
            new_states.append(state_y)

    return equivalent_states, overlapping_states, new_states

def find_equivalent_states(state_x, states_y):
    return [state_y for state_y in states_y if check_equal_states_constraints(state_x, state_y)]

def check_equal_states_constraints(state_x, state_y):
    return True if set(state_x.constraints) == set(state_y.constraints) else False

def find_overlapping_states(state_x, states_y):
    return [state_y for state_y in states_y if check_overlapping_constraints(state_x, state_y)]

def check_overlapping_constraints(state_x, state_y):
    s = Solver()

    s.push()
    for constraint in state_x.constraints:
        s.add(constraint)

    for constraint in state_y.constraints:
        s.add(constraint)

    z = True if s.check() == sat else False

    s.pop()

    return z