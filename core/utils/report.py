import json
import time

# keys

CREATE = "create"

SKIP   = "skip"

EXTEND = "extend"

ADJUST = "adjust"

STATES = "states"

TIME = 'analysis time'

# values

states = {CREATE : 0, SKIP : 0, EXTEND : 0, ADJUST : 0}

start_execution_time = None

stop_execution_time = None

total_execution_time = None


def start_tracking_execution_time():

    # modifying global variables.
    global start_execution_time

    # tracking start time.
    start_execution_time = time.time()

    return start_execution_time


def stop_tracking_execution_time():

    # modifying global variables.
    global stop_execution_time, total_execution_time

    # tracking stop time.
    stop_execution_time = time.time()

    # calculating total execution time.
    total_execution_time = stop_execution_time - start_execution_time

    return stop_execution_time


def update_states(create, skip, extend, adjust):

    # save number of created states to report.
    states[CREATE] = len(create)

    # save number of skipped states to report.
    states[SKIP] = len(skip)

    # save number of extended states to report.
    states[EXTEND] = len(extend)

    # save number of adjusted states to report.
    states[ADJUST] = len(adjust)


def dump(path):

    # collect information for report.
    data = {STATES: states, TIME: "{:.3f} seconds".format(total_execution_time)}

    # write data to file.
    with open(path, 'w') as f:
        json.dump(data, f)