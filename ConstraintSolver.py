import os, sys
from core     import symbooglix
from core     import interpreter
from core     import analyser
from optparse import OptionParser
from core     import console

PROG = os.path.basename(os.path.splitext(__file__)[0])

VERSION = '0.1'

def main():
    # Creating console interface.
    parser = OptionParser(option_class = console.MultipleOption,
                          usage        = 'usage: %prog [options] arg1 arg2',
                          version      = '%s %s' % (PROG, VERSION))
    console.populate_option_parser(parser)

    # Retrieving given options.
    options, args = parser.parse_args()

    # Asserting that console
    # - provides any option,
    # - specifies two input files,
    # - and this input files are not empty.
    if len(sys.argv) == 1 or len(options.inputs) < 2 or any (not s for s in options.inputs):
        parser.parse_args(['--help'])

    # Fetching program variants.
    paths = options.inputs

    # Interpreting specified program variants.
    programs = []
    for path in paths:
        states = symbooglix.read_terminated_symbooglix_states(path)
        program = interpreter.translate_to_program(states)
        programs.append(program)

    # Feeding interpreted program variants to z3
    statesX = programs[0].terminated_states
    statesY = programs[1].terminated_states

    equivalentStates = []
    newStates = range(len(statesY))
    overlappingStates = []

    print "Assuming number of covered states: " + str(len(statesX))
    print "Number of states to be covered: " + str(len(statesY))

    for stateY in statesY:
        equivalentToStatesInX = analyser.generate_list_of_equivalent_states(stateY, statesX)
        # equivalentStates.append(filter(lambda x: x is not None, map(lambda x: (stateY.id, equivalentToStatesInX.index(x)) if x is True else None, equivalentToStatesInX)))
        pos = [equivalentToStatesInX.index(y) for y in equivalentToStatesInX if y is True]
        if pos:
            equivalentStates.append((stateY.id, pos[0]))

    print "equivalent states; test cases to be skipped:\t" + str(equivalentStates)

    for stateY in statesY:
        overlappingWithStateInX = analyser.generate_list_of_overlapping_states(stateY, statesX)
        pos = [overlappingWithStateInX.index(y) for y in overlappingWithStateInX if y]
        if pos:
            overlappingStates.append((stateY.id, pos[0]))
            newStates.remove(stateY.id)

    overlappingStates = filter(lambda x: x not in equivalentStates, overlappingStates)

    print "overlapping states; test cases to be refined:\t" + str(overlappingStates)
    print "new states; test cases to be created:\t\t" + str(newStates)

if __name__ == '__main__':
    main()