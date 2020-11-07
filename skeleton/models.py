import traci
from main import Person


class Bus:

    def __init__(self, capacity, id):
        self.capacity = capacity
        self.onboard = []



class Pedestrian(Person):
    def __init__(self):
        self.assigned_bus = None


class Director:

    def __init__(self, pedestrians, buses):
        self.buses = buses
        self.pedestrians = pedestrians
        self.step_nbr = 0
        self.unassigned = []
        new_people_waiting_by_tmsp = dict()

        for p in pedestrians:
            tmsp = p.depart
            if tmsp in new_people_waiting_by_tmsp:
                new_people_waiting_by_tmsp[tmsp].add(p)
            else:
                new_people_waiting_by_tmsp[tmsp] = [p]
                
        self.new_people_waiting_by_tmsp = new_people_waiting_by_tmsp

    def step(self):
        np = self.new_people_waiting()
        if np:
            self.handle_new_people(np)

        self.route_to_new_dest(self.buses_with_event())

        self.step_nbr += 1

    def new_people_waiting(self):
        return []

    def handle_new_people(self, np):
        self.unassigned.extend(np)

    def buses_with_event(self):
        return []

    def route_to_new_dest(self, buses_to_be_routed):
        pass

