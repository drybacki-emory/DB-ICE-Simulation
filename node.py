class Node:
    def __init__(self, name, lat, long, id, capacity = 2):
        self.name = name
        self.lat = lat
        self.long = long
        self.id = id
        self.capacity = capacity

        self.current_trains = []

        self.delay_caused_ticks = 0

        self.down_time = 0
    
    def atCapacity(self):
        return len(self.current_trains) < self.capacity and self.down_time == 0
    
    def arrival(self, train):
        self.current_trains.append(train)

    def departure(self, train):
        if(train not in self.current_trains):
            print(f"Warning: Train {train.train_id} not in station {self.name}...")
            pass
        else:
            self.current_trains.remove(train)
    
    def nodeDown(self):
        if self.down_time > 0:
            self.down_time -= 1
