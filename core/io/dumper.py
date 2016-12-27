def dump(equivalent_states, overlapping_states, new_states):
    stream = open('out', 'w')

    stream.write('###   Equivalent States  ###\n')
    for x, y in equivalent_states:
        stream.write(str(x) + '\n\t' + str(y) + '\n')

    stream.write('\n### Overlapping States ###\n')
    for x, y in overlapping_states:
        stream.write(str(x) + '\n\t' + str(y) + '\n')

    stream.write('\n###     New States     ###\n')
    for x in new_states:
        stream.write(str(x) + '\n')