from yaml import load_all

def read_terminated_symbooglix_states(path):
    stream = file(path,'r')
    terminated_symbooglix_states = load_all(stream)
    file.close
    return terminated_symbooglix_states