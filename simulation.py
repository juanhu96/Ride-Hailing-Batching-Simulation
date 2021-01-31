# coding: utf-8
"""
Created on Jan, 2021
@author: Jingyuan Hu
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from objects import Passenger
from objects import Driver
from objects import Event

import networkx as nx
from networkx.algorithms import bipartite

from decimal import Decimal

# from helperfunctions import *

num_driver = 40
total_sim_time = 1000
arrival_lambda = 20
busy_driver = 0
tnow = 0
driver_list = [Driver(i+1) for i in range(num_driver)] 
event_list = [] 
num_event_list = 0
num_busy_driver = 0
# create -> arrive -> match -> serve
total_passenger_created = 0
total_passenger_arrived = 0
total_passenger_matched = 0
total_passenger_served = 0
passenger_list = []
passenger_waitmatch_list = [] # store the time spent before being matched 
passenger_waitpick_list = [] # store the pick up time 
passenger_insystem_list = [] # store the time spent in the system (till they finish their trip)
passenger_queue = []


def main():
    os.chdir("/Users/jingyuanhu/Desktop/Batching/Simulation/Code")

    match_time_list = []
    pick_time_list = []
    insystem_time_list = []
    w_list = []
    for i in range(30):
        w = (i + 1)
        w_list.append(w)
        print('Start simulation with w =', w)
        # for a batching window w, run the simulation j times and compute the average of the statistics
        match_time_list_trial = []
        pick_time_list_trial = []
        insystem_time_list_trial = []
        for j in range(5):
            # print('Trial', j)
            # the average time a passenger spend before being matched/pick up/leave the system
            avg_match_time, avg_pick_time, avg_insystem_time = run_simulation(w)
            match_time_list_trial.append(avg_match_time)
            pick_time_list_trial.append(avg_pick_time)
            insystem_time_list_trial.append(avg_insystem_time)
        
        match_time_list.append(compute_avg(match_time_list_trial))
        pick_time_list.append(compute_avg(pick_time_list_trial))
        insystem_time_list.append(compute_avg(insystem_time_list_trial))
        print('End simulation with w =', w)

    # Plot the results over w and save the figure
    fig, ax = plt.subplots(figsize=(20, 20))
    plt.plot(w_list, match_time_list)
    plt.plot(w_list, pick_time_list)
    plt.legend(["Wait time before matching", "Pick up time"])
    plt.title('Average time over w' + '(Number of drivers: ' + str(num_driver) + ', arrival rate: ' + str(arrival_lambda) + ')', fontdict = {'fontsize' : 36})
    plt.savefig(f'../Figs/Time({num_driver}driver_rate{arrival_lambda}).png')
    plt.cla()
    
    # plt.title('Pick-up time' + '(Number of drivers: ' + str(num_driver) + ', arrival rate: ' + str(arrival_lambda) + ')', fontdict = {'fontsize' : 40})
    # plt.savefig(f'../Figs/Time_picked({num_driver}driver_arrivalrate{arrival_lambda}).png')
    # plt.cla()

    # plt.plot(w_list, insystem_time_list)
    # plt.title('Total time spend in the system' + '(Number of drivers: ' + str(num_driver) + ', arrival rate: ' + str(arrival_lambda) + ')', fontdict = {'fontsize' : 40})
    # plt.savefig(f'../Figs/Time_insystem({num_driver}driver_arrivalrate{arrival_lambda}).png')
    # plt.cla()

    print('Finish plotting.')



def run_simulation(w):
    global tnow, total_sim_time, total_passenger_arrived, total_passenger_matched, \
        total_passenger_served, num_busy_driver, passenger_waitmatch_list, passenger_waitpick_list, \
            passenger_insystem_list, passenger_queue

    # Initilization
    initialize_vars()
    generate_init_event()
    generate_batch_event(w)

    # Simulation
    while tnow < total_sim_time:
        etype, passenger_id, driver_id, time = get_next_event()
        tnow = time
        # print(etype, time)
        if(etype == 'ARRIVAL'):
            passenger_arrival(passenger_id, time)
        elif(etype == 'COMPLETION'):
            trip_completion(driver_id, time)
        elif(etype == 'MATCH'):
            match_request(time)
        else:
            pass

    # print_results()
    # print('Total passenger arrived', total_passenger_arrived)
    # print('Total passenger matched', total_passenger_matched)
    # print('Total passenger served', total_passenger_served)
    return compute_avg(passenger_waitmatch_list), compute_avg(passenger_waitpick_list), \
        compute_avg(passenger_insystem_list)


def passenger_arrival(passenger_id, time):
        global tnow, total_passenger_arrived, total_passenger_created, \
            passenger_list, passenger_waitmatch_list, passenger_waitpick_list, \
                passenger_queue

        total_passenger_arrived += 1
        passenger_id = total_passenger_arrived
        passenger_list.append(Passenger(passenger_id, time))

        # passenger_waitmatch_list.append(0)
        # passenger_waitpick_list.append(0)
        # passenger_insystem_list.append(0)

        passenger_queue.append(passenger_id)
        
        # schedule next arrival
        total_passenger_created += 1
        generate_event('ARRIVAL', total_passenger_created, 0)
        


def trip_completion(driver_id, time):
    """
    Among completion, set driver back to idle
    """
    global num_busy_driver, total_passenger_served, passenger_list, driver_list
    total_passenger_served += 1
    driver_list[driver_id - 1].update(time, 0, 'idle')
    num_busy_driver -= 1


def match_request(time):
    """
    Do a bipartite matching between the list of idle drivers and passengers in the queue,
    this will generate a sequence of completion events.
    To do so, 
    1. Collect the information from passenger queue
    2. Collect the idle drivers from the driver list
    3. Do the bipartite matching, and generate completion events

    Note: suppose there are m idle drivers and n passengers
    Don't need to consider the size of m and n, apply minimum weight matching directly.
    NetworkX function named minimum_weight_full_matching to obtain 
    the minimum weight full matching of the bipartite graph 
    """
    global passenger_queue, driver_list, num_busy_driver, total_passenger_matched

    num_idle_drivers = num_driver - num_busy_driver
    num_passengers_queue = len(passenger_queue)

    if(num_idle_drivers > 0 and num_passengers_queue > 0):
        # since the list are 0-index
        if(num_passengers_queue > num_idle_drivers):
            passenger_in_pool = passenger_queue[:(num_idle_drivers - 1)]
        else:
            passenger_in_pool = passenger_queue

        idle_drivers = []
        for driver in driver_list:
            if(driver.get_status() == 'idle'):
                idle_drivers.append(driver)
        
        # Initialise the graph
        pool = nx.Graph()

        # Add nodes with the node attribute "bipartite"
        top_nodes = passenger_in_pool
        bottom_nodes = []
        for driver in idle_drivers:
            bottom_nodes.append(driver.get_id())
        pool.add_nodes_from(top_nodes, bipartite=0)
        pool.add_nodes_from(bottom_nodes, bipartite=1)

        # Add edges with weights (travel time which is equivalent to distance)
        for passenger_id in top_nodes:
            origin_x, origin_y = passenger_list[passenger_id - 1].get_origin()
            for driver_id in bottom_nodes:
                location_x, location_y = driver_list[driver_id - 1].get_location()
                # Note: we transfer driver_id to string to distinguish from passenger
                pool.add_edge(passenger_id, str(driver_id), \
                    weight = travel_time(origin_x, origin_y, location_x, location_y))

        # Obtain the minimum weight full matching
        if((not top_nodes) or (not bottom_nodes)):
            return

        matching_results = bipartite.matching.minimum_weight_full_matching(pool, top_nodes, "weight")
        
        # Generate events
        for passenger_id in passenger_in_pool:
            if passenger_id in matching_results:
                # Note: we transfer the value back to int to access
                driver_id = int(matching_results[passenger_id]) 

                origin_x, origin_y = passenger_list[passenger_id - 1].get_origin()
                destination_x, destination_y = passenger_list[passenger_id - 1].get_destination()
                location_x, location_y = driver_list[driver_id - 1].get_location()
                arrival_time = passenger_list[passenger_id - 1].get_arrival_time()
                pickup_time = travel_time(location_x, location_y, origin_x, origin_y)
                trip_time = travel_time(origin_x, origin_y, destination_x, destination_y)

                generate_event('COMPLETION', passenger_id, driver_id, pickup_time + trip_time)

                # Update statistics
                passenger_queue.remove(passenger_id)
                total_passenger_matched += 1
                num_busy_driver += 1
                # passenger_waitmatch_list[passenger_id - 1] = Decimal(time) - Decimal(arrival_time)
                # passenger_waitpick_list[passenger_id - 1] = Decimal(pickup_time)
                # passenger_insystem_list[passenger_id - 1] = Decimal(time) - Decimal(arrival_time) + \
                #     Decimal(pickup_time) + Decimal(trip_time)

                # print(time, arrival_time, pickup_time, trip_time)

                # the first 100 seconds are for warmup
                if(time > 100):
                    passenger_waitmatch_list.append(Decimal(time) - Decimal(arrival_time))
                    passenger_waitpick_list.append(Decimal(pickup_time))
                    passenger_insystem_list.append(Decimal(time) - Decimal(arrival_time) + \
                        Decimal(pickup_time) + Decimal(trip_time))
                



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
    global tnow
    if(etype == 'ARRIVAL'):
        # current time plus interarrival time
        # we use '%.1f' & float to avoid representation problem
        interarrival_time = round(Decimal(np.random.exponential(scale = arrival_lambda, size = 1)[0]),1)
        time = tnow + interarrival_time
    elif(etype == 'COMPLETION'):
        time = tnow + trip_time
    elif(etype == 'MATCH'):
        time = trip_time

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
    global tnow, busy_driver, driver_list, event_list, num_event_list, num_busy_driver
    global total_passenger_created, total_passenger_arrived, total_passenger_matched, total_passenger_served
    global passenger_list, passenger_waitmatch_list, passenger_waitpick_list, passenger_insystem_list, passenger_queue

    tnow = 0
    busy_driver = 0
    driver_list = [Driver(i+1) for i in range(num_driver)] 
    event_list = [] 
    num_event_list = 0
    num_busy_driver = 0
    # create -> arrive -> match -> serve
    total_passenger_created = 0
    total_passenger_arrived = 0
    total_passenger_matched = 0
    total_passenger_served = 0
    passenger_list = []
    passenger_waitmatch_list = [] # store the time spent before being matched 
    passenger_waitpick_list = [] # store the time spent before being picked
    passenger_insystem_list = [] # store the time spent in the system (till they finish their trip)
    passenger_queue = []

    

def generate_init_event():
    """
    Generate the first event to start the simulation
    """
    global total_passenger_created
    total_passenger_created = 1
    generate_event('ARRIVAL', total_passenger_created, 0)


def generate_batch_event(w):
    """
    Generate batching event every w seconds over the total simulation time
    """
    global total_sim_time
    matching_period = total_sim_time / w
    for i in range(int(matching_period)):
        # passenger_id = 0 is dummy passenger
        generate_event('MATCH', 0, 0, (i+1) * w)


def insert_event(time, etype, passenger_id, driver_id):
    global num_event_list
    event_list.append(Event(time, etype, passenger_id, driver_id))
    num_event_list += 1


def travel_time(x1, y1, x2, y2):
    dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    travel_time = round(0.5*dist[0], 1)
    return travel_time


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


def compute_avg(lst):
    """
    Compute the average of a list of number
    """
    return round(Decimal(sum(lst) / len(lst)), 2)

# def save_results():
#     with open('result.txt', 'w') as f:
#         print('Filename:', filename, file=f)

if __name__ == "__main__":
    main()