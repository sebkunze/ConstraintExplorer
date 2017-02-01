from core.object.data.test import Test
from core.utils            import logger

def analyse_program_states(program_x, program_y):
    tests = []

    # find overlapping states.
    for symbolic_state_y in program_y.symbolic_states:

        logger.info("Searching for overlapping states of symbolic state %s.", symbolic_state_y.id)

        overlapping_symbolic_states_x = symbolic_state_y.find_overlapping_states(program_x.symbolic_states)

        logger.info("Found %i overlapping states.", len(overlapping_symbolic_states_x))

        if overlapping_symbolic_states_x:
            _, values = symbolic_state_y.gen_values()

            logger.info("Creating tests for symbolic state %s.", symbolic_state_y.id)

            tests.append(Test(symbolic_state_y, overlapping_symbolic_states_x, str(values).replace('\n','')))

    return tests

# def generate_overlapping_values(constraints_x, constraints_y):
#     model = None
#
#     solver = Solver()
#
#     x = None
#     for constraint in constraints_x:
#         if x is None:
#             x = constraint.z3constraint
#         else:
#             x = And(constraint.z3constraint, x)
#
#     y = None
#     for constraint in constraints_y:
#         if y is None:
#           y = constraint.z3constraint
#         else:
#             y = And(constraint.z3constraint, y)
#
#     solver.push()
#
#     solver.add(Not(Implies(x, y)))
#     if solver.check() == sat:
#         model = solver.model()
#     else:
#         solver.pop()
#         solver.push()
#
#         solver.add(Not(Implies(y, x)))
#         if solver.check() == sat:
#             model = solver.model()
#
#     solver.pop()
#
#     return model