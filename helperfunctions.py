"""
Created on Jan, 2021
@author: Jingyuan Hu
"""

EVENT_ENTRIES = 1000
PASSENGER_ENTRIES = 1000

def initialize_vars():
    """
    Consider the time are all integers now for simplicity
    """
    tnow = 0
    # make sure it starts from 1 to num_driver
    driver_list = [Driver(i+1) for i in range(num_driver)] 
    event_list = [] 
    passenger_list = []
    passenger_queue = []

def generate_init_event():
    """
    Generate the first event to start the simulation
    """
    total_passenger_created = 1
    generate_event('ARRIVAL', total_passenger_created, 0)

def insert_event(time, etype, driver_id):
    event_list[num_event_list].update(time, etype, passenger_id, driver_id)
    num_event_list += 1

    if(num_event_list >= EVENT_ENTRIES):
        print('need to expand event list size')

def travel_time(x1, y1, x2, y2):
    dist = sqrt((x2 - x1)**2 + (y2 - y1)**2)
    time = 0.1 * dist
    return time


def select_event():
    """
    Select the next event on the event list，based on the earliest time
    """
    return next_event_index


def save_results():
    with open('result.txt', 'w') as f:
        print('Filename:', filename, file=f) 