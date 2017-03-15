from yaml        import load_all

from core.object import parser

def load_programs(paths):
    programs = []

    for path in paths:
        terminated_symbooglix_states = read_terminated_symbooglix_states(path)
        translated_program = parser.to_program(terminated_symbooglix_states)
        programs.append(translated_program)

    return programs

def read_terminated_symbooglix_states(path):
    stream = file(path,'r')

    terminated_symbooglix_states = load_all(stream)

    stream.close

    return terminated_symbooglix_states