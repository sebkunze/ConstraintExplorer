from yaml import load_all
        
def readTerminatedStates(path):
    stream = file(path,'r')
    termiatedStates = load_all(stream)
    file.close
    return termiatedStates