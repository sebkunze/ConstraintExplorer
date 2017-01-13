def dump(equivalent_states, overlapping_states, new_states, output_file):
    stream = open(output_file, 'a')

    # print equivalent states.
    stream.write('###   Equivalent States  ###\n')
    for x, y in equivalent_states:
        stream.write(str(x) + '\n\t' + str(y) + '\n\n')

    # print overlapping states.
    stream.write('\n### Overlapping States ###\n')
    for x, y in overlapping_states:
        stream.write(str(x) + '\n\t' + str(y) + '\n\n')

    # print new states.
    stream.write('\n###     New States     ###\n')
    for x in new_states:
        stream.write(str(x) + '\n\n')

    stream.close()