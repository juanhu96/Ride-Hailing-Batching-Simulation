"""
Created on Jan, 2021
@author: Jingyuan Hu
"""

import numpy as np

from objects import Passenger
from objects import Driver
from objects import Event

from helperfunctions import *

num_driver = 5
total_sim_time = 10
arrival_lambda = 0.5
busy_driver = 0
tnow = 0
driver_list = [Driver(i+1) for i in range(num_driver)] 
event_list = [] 
num_event_list = 0
num_busy_driver = 0
total_passenger_arrived = 0
total_passenger_created = 0
total_passenger_served = 0
passenger_list = []
passenger_queue = []

def main():
    global tnow, total_sim_time
    # Initilization
    initialize_vars()
    generate_init_event()

    # Simulation
    while tnow < total_sim_time:
        etype, passenger_id, driver_id, time = get_next_event()
        # update_stats()
        tnow = time
        print(passenger_id, etype, driver_id)
        if(etype == 'ARRIVAL'):
            passenger_arrival(passenger_id, driver_id, time)
        elif(etype == 'COMPLETION'):
            trip_completion(driver_id, time)

    # print_results()
    print(total_passenger_arrived, total_passenger_served, num_busy_driver)


def passenger_arrival(passenger_id, driver_id, time):
    """
    Consider FIFO for simplicity now,
    so the passenger will be assigned to the first available driver
    and will generate a completion event

    1. Process the current arrival from the event_list
    2. Insert the corresponding completion to the event_list
    3. Insert a new arrival to the event_list

    Note that total_passenger_created > total_passenger_arrived, 
    some arrival events are created but still in the event list not being processed
    """
    global tnow, total_passenger_arrived, total_passenger_created, num_busy_driver

    total_passenger_arrived += 1
    passenger_id = total_passenger_arrived
    passenger_list.append(Passenger(passenger_id, time))

    # update driver_id from 0 to the next available driver
    # if available, assigned directly; if not, driver_id keep to be 0
    driver_id = get_driver(passenger_id)
    if (driver_id == 0):
        # passenger_queue is a list of id, which passenger_list is a list of passengers
        passenger_queue.append(passenger_id)
    else:
        # compute the pick up time and service time
        origin_x, origin_y = passenger_list[passenger_id - 1].get_origin()
        destination_x, destination_y = passenger_list[passenger_id - 1].get_origin()
        location_x, location_y = driver_list[driver_id - 1].get_location()
        pickup_time = travel_time(location_x, location_y, origin_x, origin_y)
        trip_time = travel_time(origin_x, origin_y, destination_x, destination_y)

        # need to update the driver's next available time & location
        driver_list[driver_id - 1].update(tnow + pickup_time + trip_time, passenger_id, 'busy')
        driver_list[driver_id - 1].update_location(destination_x, destination_y)
        num_busy_driver += 1
        generate_event('COMPLETION', passenger_id, driver_id, pickup_time + trip_time)

    # schedule next arrival
    total_passenger_created += 1
    generate_event('ARRIVAL', total_passenger_created, 0)



def get_driver(passenger_id):
    """
    Get the idle and closest driver 
    """
    global num_busy_driver, num_driver, passenger_list, driver_list
    min_driver_id = 0
    min_time = 1000
    origin_x, origin_y = passenger_list[passenger_id - 1].get_origin()

    if(num_busy_driver < num_driver):
        for driver in driver_list:
            if(driver.get_status() == 'idle'):
                # compute distance select the nearest one
                location_x, location_y = driver.get_location()
                curr_time = travel_time(origin_x, origin_y, location_x, location_y)
                # update the nearest one
                if(curr_time < min_time):
                    min_driver_id = driver.get_id()
                    min_time = curr_time
        return min_driver_id
    else:
        return 0

def trip_completion(driver_id, time):
    """
    Among completion, find the next passenger from the passenger_queue
    """
    global num_busy_driver, total_passenger_served, passenger_list, driver_list
    total_passenger_served += 1
    passenger_id = get_passenger()

    # if no passenger, set driver to idle; 
    # if exist passenger, generate another completion event
    if(passenger_id == 0):
        driver_list[driver_id - 1].update(time, 0, 'idle')
        num_busy_driver -= 1
    else:
        # compute the pick up time and service time
        origin_x, origin_y = passenger_list[passenger_id - 1].get_origin()
        destination_x, destination_y = passenger_list[passenger_id - 1].get_origin()
        location_x, location_y = driver_list[driver_id - 1].get_location()
        pickup_time = travel_time(location_x, location_y, origin_x, origin_y)
        trip_time = travel_time(origin_x, origin_y, destination_x, destination_y)
        
        # update driver's information 
        driver_list[driver_id - 1].update(time, passenger_id, 'busy')
        driver_list[driver_id - 1].update_location(destination_x, destination_y)
        
        # update passenger_queue and event
        passenger_queue.remove(passenger_id)
        generate_event('COMPLETION', passenger_id, driver_id, pickup_time + trip_time)


def get_passenger():
    """
    Get the earliest passenger on the list, i.e. the maximum time stayed
    """
    global passenger_list, total_sim_time
    min_arrival_time = total_sim_time
    min_arrival_passenger = 0

    for passenger_id in passenger_queue:
        curr_arrival_time = passenger_list[passenger_id - 1].get_arrival_time()
        if(curr_arrival_time < min_arrival_time):
            min_arrival_passenger = passenger_id
            min_arrival_time = curr_arrival_time
    
    return min_arrival_passenger


def generate_event(etype, passenger_id, driver_id, trip_time = 0):
    """
    Event type: ARRIVAL, COMPLETION
    Time: time of arrival, time of completion of ride
    Passenger_id: The corresponding passenger id
    Driver_id: The corresponding driver's id, if it's an arrival event, 
    then the driver id would be 0
    Trip time: 0 for arrival since it does not have any meanings

    Generate either a new 
    Upon completion of a ride, the driver knows exactly who he is going to pick,
    and the pickup time & ride time can be computed immediately,
    and we can update the driver's next available time based on the information
    """

    if(etype == 'ARRIVAL'):
        # current time plus interarrival time
        time = tnow + np.random.poisson(lam = arrival_lambda, size = 1)
    elif(etype == 'COMPLETION'):
        time = tnow + trip_time

    insert_event(time, etype, passenger_id, driver_id)


def get_next_event():
    """
    Return the information of the next event
    """
    global event_list, num_event_list
    next_event_index = select_event()

    event_type = event_list[next_event_index].get_type()
    passenger_id = event_list[next_event_index].get_passenger_id()
    driver_id = event_list[next_event_index].get_driver_id()
    time = event_list[next_event_index].get_time()

    # clean up the space
    del event_list[next_event_index] # doesn't need to -1 as it is from select_event()
    num_event_list -= 1

    return event_type, passenger_id, driver_id, time


"""
Helper function
"""


def initialize_vars():
    """
    Consider the time are all integers now for simplicity
    """
    tnow = 0
    # make sure it starts from 1 to num_driver
    

def generate_init_event():
    """
    Generate the first event to start the simulation
    """
    global total_passenger_created
    total_passenger_created = 1
    generate_event('ARRIVAL', total_passenger_created, 0)

def insert_event(time, etype, passenger_id, driver_id):
    global num_event_list
    event_list.append(Event(time, etype, passenger_id, driver_id))
    num_event_list += 1

def travel_time(x1, y1, x2, y2):
    dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    time = 0.1 * dist
    return time


def select_event():
    """
    Select the next event on the event list，based on the earliest time
    """
    global total_sim_time
    next_event_index = 0
    min_event_time = total_sim_time
    for event in event_list:
        curr_event_time = event.get_time()
        if(curr_event_time < min_event_time):
            next_event_index = event_list.index(event)
            min_event_time = curr_event_time
    return next_event_index


def save_results():
    with open('result.txt', 'w') as f:
        print('Filename:', filename, file=f)

if __name__ == "__main__":
    main()