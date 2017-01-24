from z3 import Bool, Int, And, Implies, Not, Solver, sat

from core.object.data.test import TestArtefact, TestRefinement
from core.utils            import logger

def analyse_program_states(program_x, program_y):
    test_artefacts = []

    test_refinements = []

    # find overlapping states.
    for symbolic_state_y in program_y.symbolic_states:

        logger.debug('Searching for overlapping states of state %s', symbolic_state_y.id)

        # TODO: Refactor!
        overlapping_symbolic_states_x = symbolic_state_y.find_overlapping_states(program_x.symbolic_states)

        logger.debug('Found %i overlapping states.', len(overlapping_symbolic_states_x))

        if overlapping_symbolic_states_x:
            test_refinements.append(TestRefinement(symbolic_state_y, overlapping_symbolic_states_x, None))

        # if overlapping_symbolic_states_x:
        #     model = generate_overlapping_values(symbolic_state_y.constraints,
        #                                         overlapping_symbolic_states_x[0].constraints)
        #
        #     test_refinements.append(TestRefinement(symbolic_state_y, overlapping_symbolic_states_x, model))
        # else:
        #     model = generate_new_values(symbolic_state_y.constraints)
        #
        #     test_artefacts.append(TestArtefact(symbolic_state_y, model))

    return test_artefacts, test_refinements

def generate_overlapping_values(constraints_x, constraints_y):
    model = None

    solver = Solver()

    x = None
    for constraint in constraints_x:
        if x is None:
            x = constraint.z3constraint
        else:
            x = And(constraint.z3constraint, x)

    y = None
    for constraint in constraints_y:
        if y is None:
          y = constraint.z3constraint
        else:
            y = And(constraint.z3constraint, y)

    solver.push()

    solver.add(Not(Implies(x, y)))
    if solver.check() == sat:
        model = solver.model()
    else:
        solver.pop()
        solver.push()

        solver.add(Not(Implies(y, x)))
        if solver.check() == sat:
            model = solver.model()

    solver.pop()

    return model

def generate_new_values(constraints):
    model = None

    solver = Solver()

    x = None
    for constraint in constraints:
        if x is None:
            x = constraint.z3constraint
        else:
            x = And(constraint.z3constraint, x)

    solver.push()

    solver.add(x)
    if solver.check == sat:
        model = solver.model()

    return model