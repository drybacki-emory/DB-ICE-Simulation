import random
from collections import deque

class Edge:
    def __init__(self, outboundStation, inboundStation, capacity = 15, failure_rate=0.000001): 
        self.name = f'{outboundStation.name} - {inboundStation.name}'
        self.outbound = outboundStation
        self.inbound = inboundStation
        self.capacity = capacity 
        self.queue = deque() #FIFO queue for trains waiting to enter line
        self.occupants = [] #List of train(s) on line

        #Stochastic element to model track failure/maitnance needed (parameter to be tuned)
        self.failure_rate = failure_rate
        self.down_time = 0        # Down time to track whether track is operational or how many mins/ticks left until operational

        self.delay_caused_ticks = 0


    def isOpen(self):
        return len(self.occupants) < self.capacity and self.down_time == 0
    
    def trainToQueue(self, train):
        if train in self.outbound.current_trains:
            self.queue.append(train)
    
    def acceptTrain(self):
        if len(self.queue) > 0 and self.isOpen():
            activeTrain = self.queue.popleft() #Allow new train to pass through
            self.outbound.departure(activeTrain) #Remove train from station
            self.occupants.append(activeTrain) #Add train to active on track
            
            activeTrain.enter_track(self)

    def track_maintenance(self):
        if self.down_time > 0:
            self.down_time -= 1
        else: #once down, no other failure will occur on that track
            if random.random() < self.failure_rate: #tracks have a failure rate of 0.0001% / min
    
                raw_repair_time = random.lognormvariate(3.4, 0.6) #Maintence time should follow Lognormal with mean of 3.4 and 
                                                                  #stdev of 0.6 which gives a median repair time of approx 30 mins 
                                                                  # and average of approx. 36 mins
                # Ensure it takes at least 1 tick, and round to a whole integer
                self.down_time = max(1, int(raw_repair_time))
                
                print(f"[TRACK FAILURE] {self.name} down; estimated repair: {self.down_time} ticks.")




