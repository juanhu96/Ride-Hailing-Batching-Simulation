"""
Created on Jan, 2021
@author: Jingyuan Hu
"""

from numpy import random

from objects import Passenger
from objects import Driver
from objects import Events

from helperfunctions import *

num_driver = 5
total_sim_time = 1000
arrival_lambda = 1
busy_driver = 0


def main():
    # Initilization
    initialize_vars()
    generate_init_event()

    # Simulation
    while t_now < total_sim_time:
        etype, passenger_id, driver_id, time = get_next_event()
        update_stats()

        if(etype == 'ARRIVAL'):
            passenger_arrival(passenger_id, driver_id, time)
        elif(etype == 'COMPLETION'):
            trip_completion(driver_id, time)

    # print_results()
    print(total_passenger_arrived, total_passenger_served)


def passenger_arrival(passenger_id, driver_id, time):
    """
    Consider FIFO for simplicity now,
    so the passenger will be assigned to the first available driver
    and will generate a completion event
    """

    total_passenger_arrived += 1

    # update driver_id from 0 to the next available driver
    # if available, assigned directly; if not, driver_id keep to be 0
    driver_id = get_driver()
    if (driver_id == 0):
        # passenger_queue is a list of id
        passenger_queue.append(passenger_id)
    else:
        # compute the pick up time and service time
        origin_x, origin_y = passenger_list[passenger_id].get_origin()
        destination_x, destination_y = passenger_list[passenger_id].get_origin()
        location_x, location_y = driver_list[driver_id].get_location()
        pickup_time = travel_time(location_x, location_y, origin_x, origin_y)
        trip_time = travel_time(origin_x, origin_y, destination_x, destination_y)

        # need to update the driver's next available time & location
        driver_list[driver_id].update(next_avail_time, passenger_id, \
            destination_x, destination_y, 'busy')
        num_busy_driver += 1
        generate_event('COMPLETION', passenger_id, driver_id, pickup_time + trip_time)

def get_driver():
    """
    Get the idle and closest driver 
    """
    if(num_busy_driver < num_driver)：
    


def trip_completion(driver_id, time):
    """
    Among completion, find the next passenger from the passenger_queue
    """

    total_passenger_served += 1
    passenger_id = get_passenger()

    # if no passenger, set driver to idle; 
    # if exist passenger, generate another completion event
    if(passenger_id == 0):
        driver_list[driver_id].update(time, 0, 'idle')
        num_busy_driver -= 1
    else:
        # compute the pick up time and service time
        origin_x, origin_y = passenger_list[passenger_id].get_origin()
        destination_x, destination_y = passenger_list[passenger_id].get_origin()
        location_x, location_y = driver_list[driver_id].get_location()
        pickup_time = travel_time(location_x, location_y, origin_x, origin_y)
        trip_time = travel_time(origin_x, origin_y, destination_x, destination_y)
        
        # update driver's information 
        driver_list[driver_id].update(time, passenger_id, \
            destination_x, destination_y, 'busy')
        
        # update passenger_queue and event
        passenger_queue.remove(passenger_id)
        generate_event('COMPLETION', passenger_id, driver_id, pickup_time + trip_time)



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
        time = tnow + random.poisson(lam = arrival_lambda, size = 1)
    elif(etype == 'COMPLETION'):
        time = tnow + trip_time

    insert_event(time, etype, passenger_id, driver_id)


def get_next_event():
    """
    Return the information of the next event
    """
    next_event_index = select_event()

    event_type = event_list[next_event_index].get_type()
    passenger_id = event_list[next_event_index].get_passenger_id()
    driver_id = event_list[next_event_index].get_driver_id()
    time = event_list[next_event_index].get_time()

    # if not last spot, reassign this spot to the last one and free up the last one (?)
    if(next_event_index < num_event_list - 1):
        event_list[next_event_index] = event_list[num_event_list - 1]

    return event_type, passenger_id, driver_id, time



