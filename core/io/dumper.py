import yaml

from core.utils import logger

# def dump(equivalent_states, overlapping_states, new_states, output_file):
#     stream = open(output_file, 'a')
#
#     # print equivalent states.
#     stream.write('###   Equivalent States  ###\n')
#     for x, y in equivalent_states:
#         stream.write(str(x) + '\n\t' + str(y) + '\n\n')
#
#     # print overlapping states.
#     stream.write('\n### Overlapping States ###\n')
#     for x, y in overlapping_states:
#         stream.write(str(x) + '\n\t' + str(y) + '\n\n')
#
#     # print new states.
#     stream.write('\n###     New States     ###\n')
#     for x in new_states:
#         stream.write(str(x) + '\n\n')
#
#     stream.close()

def dump(test_artefacts, test_refinements, output_file):
    stream = file(output_file, 'a')

    if test_artefacts:
        for artefact in test_artefacts:
            # d = str(artefact.__dict__).replace('\n','')
            # logger.debug('%s', d)
            # yaml.dump(d, stream)
            # yaml.dump(str(artefact).replace('\n',''), stream)
            stream.write(str(artefact) + '\n')

    stream.write('\n')

    if test_refinements:
        for refinement in test_refinements:
            # d = str(refinement.__dict__).replace('\n','')
            # logger.debug('%s', d)
            # yaml.dump(d, stream)
            # yaml.dump(str(refinement).replace('\n',''), stream)
            stream.write(str(refinement) + '\n')

    # # print equivalent states.
    # stream.write('###   Equivalent States  ###\n')
    # for x, y in equivalent_states:
    #     stream.write(str(x) + '\n\t' + str(y) + '\n\n')
    #
    # # print overlapping states.
    # stream.write('\n### Overlapping States ###\n')
    # for x, y in overlapping_states:
    #     stream.write(str(x) + '\n\t' + str(y) + '\n\n')
    #
    # # print new states.
    # stream.write('\n###     New States     ###\n')
    # for x in new_states:
    #     stream.write(str(x) + '\n\n')

    stream.close()