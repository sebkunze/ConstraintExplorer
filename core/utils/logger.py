import os
import logging

constraint_solver_home_environment \
    = os.environ['CONSTRAINT_SOLVER_HOME']
filename \
    = os.path.join(constraint_solver_home_environment, 'ConstraintSolver.log')

def info(msg, args = []):
    log.info(msg, args)

def debug(msg, args = []):
    log.debug(msg, args)

log = logging.getLogger('ConstraintSolver')
log.setLevel(logging.DEBUG)

# create a file handler
fLog = logging.FileHandler(filename)
fLog.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fLog.setFormatter(formatter)

# add the handlers to the logger
log.addHandler(fLog)