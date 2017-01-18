from yaml       import load_all

from core.object.data import program


def load_programs(paths):
    programs = []

    for path in paths:
        terminated_symbooglix_states = read_terminated_symbooglix_states(path)
        translated_program = program.translate_to_program(terminated_symbooglix_states)
        programs.append(translated_program)

    return programs

def read_terminated_symbooglix_states(path):
    stream = file(path,'r')
    terminated_symbooglix_states = load_all(stream)
    file.close
    return terminated_symbooglix_states