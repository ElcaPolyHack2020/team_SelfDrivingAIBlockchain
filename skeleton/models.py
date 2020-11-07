import traci
from main import Person


class Bus:

    def __init__(self, capacity, id):
        self.capacity = capacity
        self.onboard = []
        self.next_destination = None

    def distance_to(self, p):
        pass

    def route_to(self, person):
        self.next_destination = person
        person.assigned_bus = self



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
        if self.step_nbr in self.new_people_waiting_by_tmsp:
            return self.new_people_waiting_by_tmsp[self.step_nbr]
        else:
            return []


    def handle_new_people(self, np):
        self.unassigned.extend(np)

    def buses_with_event(self):
        # Remove the person onbaord!
        return []

    def route_to_new_dest(self, buses_to_be_routed):

        for bus in buses_to_be_routed:

            closest_next = None
            closest_distance = 0
            will_be_pickup = True
            for p_onbaord in bus.onbaord:
                dist = bus.distance_to(p_onbaord)
                if not closest_next or dist < closest_distance:
                    closest_distance = dist
                    closest_next = p_onbaord

            if len(bus.onbaord) < bus.capacity:
                dist = bus.distance_to(p_onbaord)
                for p in self.unassigned:
                    if not closest_next or dist < closest_distance:
                        closest_distance = dist
                        closest_next = p
                        will_be_pickup = False
            
            if closest_next:
                if will_be_pickup:
                    bus.onboard.append(closest_next)
                bus.route_to(closest_next)



