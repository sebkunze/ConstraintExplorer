import os
import logging

constraint_solver_home_environment = os.environ['CONSTRAINT_SOLVER_HOME']
filename = os.path.join(constraint_solver_home_environment, 'ConstraintSolver.log')

def info(msg, args = []):
    log.info(msg, args)

def debug(msg, args = []):
    log.debug(msg, args)

log = logging.getLogger('ConstraintSolver')
log.setLevel(logging.DEBUG)

fLog = logging.FileHandler(filename)
fLog.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fLog.setFormatter(formatter)

log.addHandler(fLog)