import numpy as np

class Passenger:
    def __init__(self, id, arrival_time):
        self.id = id
        self.patience = 0 # not considered for now
        self.origin_x = np.random.uniform(0, 100, 1)
        self.origin_y = np.random.uniform(0, 100, 1)
        self.destination_x = np.random.uniform(0, 100, 1)
        self.destination_y = np.random.uniform(0, 100, 1)
        self.arrival_time = arrival_time
        self.time_stayed = 0

    def get_id(self):
        return self.id

    def get_origin(self):
        return self.origin_x, self.origin_y
    
    def get_destination(self):
        return self.destination_x, self.destination_y
        
    def get_arrival_time(self):
        return self.arrival_time


class Driver: 
    def __init__(self, id):
        """
        id
        location: x, y axis
        status: idle, busy
        avail_time: when is the driver available
        passenger: id of the passenger who is riding
        """
        self.id = id
        self.location_x = np.random.uniform(0, 100, 1)
        self.location_y = np.random.uniform(0, 100, 1)
        self.status = 'idle'
        self.avail_time = 0
        self.passenger_id = 0
    
    def get_id(self):
        return self.id

    def get_location(self):
        # returns a tuple of x, y coordinates
        return self.location_x, self.location_y 

    def get_status(self):
        return self.status

    def next_avail_time(self):
        return self.avail_time

    def get_passenger(self):
        return self.passenger_id

    def update(self, avail_time, passenger_id, status):
        self.avail_time = avail_time
        self.passenger_id = passenger_id
        self.status = status
    
    def update_location(self, location_x, location_y):
        self.location_x = location_x
        self.location_y = location_y

class Event:
    def __init__(self, time, event_type, passenger_id, driver_id):
        self.time = time
        self.event_type = event_type
        self.passenger_id = passenger_id
        self.driver_id = driver_id

    def get_time(self):
        return self.time
    
    def get_type(self):
        return self.event_type

    def get_passenger_id(self):
        return self.passenger_id
    
    def get_driver_id(self):
        return self.driver_id

    def update(self, time, event_type):
        self.time = time
        self.event_type = event_type
