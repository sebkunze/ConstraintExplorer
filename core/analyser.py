from core.object.data.test import Test
from core.utils            import logger

def analyse_program_states(program_x, program_y):
    tests = []

    # find overlapping states.
    for symbolic_state_y in program_y.symbolic_states:

        logger.info("Searching for overlapping states of symbolic state %s.", symbolic_state_y.state_id)

        overlapping_symbolic_states_x = symbolic_state_y.find_overlapping_states(program_x.symbolic_states)

        logger.info("Found %i overlapping states.", len(overlapping_symbolic_states_x))

        if overlapping_symbolic_states_x:
            _, values = symbolic_state_y.gen_values()

            logger.info("Creating tests for symbolic state %s.", symbolic_state_y.state_id)

            tests.append(Test(symbolic_state_y, overlapping_symbolic_states_x, str(values).replace('\n','')))

    return tests