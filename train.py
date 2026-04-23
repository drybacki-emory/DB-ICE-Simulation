import random
from collections import deque

class Train:
    def __init__(self, train_id, scheduled_route, spawn_tick):
        self.train_id = train_id
        self.name = f"ICE {train_id}"
        
        #FORMAT: [(Edge_Object, travel_ticks, dwell_ticks_at_next_station), ...]
        self.scheduled_route = scheduled_route 

        self.spawn_tick = spawn_tick
        
        self.status = "AT_STATION"
        self.onTime = True 
        self.total_delay_ticks = 0 
        self.actual_travel_times = [] 
        
        self.current_leg_index = 0
        self.current_edge = None
        
        self.time_on_current_track = 0
        self.current_target_time = 0
        
        self.time_at_station = 0
        self.current_target_dwell = 15 #15 min spawn assumption

    def get_current_edge(self):
        if self.current_leg_index < len(self.scheduled_route):
            return self.scheduled_route[self.current_leg_index][0] 
        return None

    def enter_track(self, edge):
        self.status = "ON_TRACK"
        self.time_on_current_track = 0
        self.current_edge = edge 
        
        _, scheduled_duration, _ = self.scheduled_route[self.current_leg_index]
        self.current_target_time = scheduled_duration

    def arrive_at_station(self):
        self.status = "AT_STATION"
        
        current_edge = self.get_current_edge()
        destination_station = current_edge.inbound
        
        destination_station.arrival(self) 
        current_edge.occupants.remove(self) 
        
        delay_on_this_leg = self.time_on_current_track - self.current_target_time
        if delay_on_this_leg > 0:
            self.total_delay_ticks += delay_on_this_leg
            self.onTime = False

            self.current_edge.delay_caused_ticks += delay_on_this_leg
            
        self.actual_travel_times.append(self.time_on_current_track)
        
        self.time_at_station = 0
        
        _, _, scheduled_dwell = self.scheduled_route[self.current_leg_index]
        self.current_target_dwell = scheduled_dwell
        
        #5% chance passenger loading takes 1-3 extra ticks
        if random.random() < 0.05:
            stall_delay = random.randint(1, 3)
            self.current_target_dwell += stall_delay
            self.total_delay_ticks += stall_delay # This permanently adds to the train's delay!
            print(f"[{self.name}] Passenger loading delay at {destination_station.name}: +{stall_delay} ticks.")

            destination_station.delay_caused_ticks += stall_delay
            
        # Move pointer to the next stop
        self.current_leg_index += 1
        if self.current_leg_index >= len(self.scheduled_route):
            self.status = "FINISHED"
            destination_station.departure(self)

    def update(self):
        if self.status == "FINISHED":
            return

        # State 1: Dwelling at station
        if self.status == "AT_STATION":
            self.time_at_station += 1

            if self.time_at_station >= self.current_target_dwell:
                if self.current_leg_index < len(self.scheduled_route):
                    
                    next_edge = self.scheduled_route[self.current_leg_index][0]
                    
                    # Request to enter the track queue
                    if self not in next_edge.queue:
                        next_edge.trainToQueue(self)
                    
                    self.total_delay_ticks += 1
                    self.current_node.delay_caused_ticks += 1

        # State 2: traveling on tracks
        elif self.status == "ON_TRACK":
            self.time_on_current_track += 1

            if self.time_on_current_track >= self.current_target_time:
                destination_station = self.current_edge.inbound
                
                if destination_station.atCapacity():
                    self.arrive_at_station()
                else:
                    self.total_delay_ticks += 1
                    destination_station.delay_caused_ticks += 1