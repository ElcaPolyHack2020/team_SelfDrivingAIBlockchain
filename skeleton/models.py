import traci
import utils


class Bus:

    def __init__(self, capacity, id):
        self.capacity = capacity
        self.id = id
        self.onboard = []
        self.next_destination = None
        traci.vehicle.add(vehID=id, typeID="BUS_L", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=capacity)
        traci.vehicle.setRoute(id, [utils.BUS_START_EDGE])

    def distance_to(self, p):
        bus_id = 'test_bus'
        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        traci.vehicle.setRoute(bus_id,[self.get_edge()])
        traci.vehicle.changeTarget(bus_id, p.edge_from)
        return utils.getDist(traci.vehicle.getRoute(bus_id))

    def route_to(self, person):
        self.next_destination = person
        person.assigned_bus = self

    def is_going_to_dropoff(self):
        return self.next_destination in self.onboard

    def get_edge(self):
        return traci.vehicle.getRoute(self.id)[0]

    def is_full(self):
        return len(self.onboard) == self.capacity

    def select_next(self, new_pickups_candidates, is_at_end_of_route):
        if is_at_end_of_route:
            on_board_candidates = self.onboard
        else:
            if self.is_going_to_dropoff():
                on_board_candidates = [self.next_destination]
            else:
                new_pickups_candidates.append(self.next_destination)
                on_board_candidates = []
        closest_next = None
        closest_distance = 0
        will_be_pickup = False

        # Consider to drop off someone first
        for p_onbaord in on_board_candidates:
            dist = self.distance_to(p_onbaord)
            if not closest_next or dist < closest_distance:
                closest_distance = dist
                closest_next = p_onbaord

        # Or pick up?
        if not self.is_full():
            for p_pickup in new_pickups_candidates:
                if not p_pickup.assigned_bus:
                    dist = self.distance_to(p_pickup)
                    if not closest_next or dist < closest_distance:
                        closest_distance = dist
                        closest_next = p_pickup
                        will_be_pickup = True
        
        return (closest_next, closest_distance, will_be_pickup)

class Person:
    # init method or constructor
    def __init__(self, id: str, edge_from: str, edge_to: str, position_from: float, position_to: float, depart: float):
        self.id = id
        self.edge_from = edge_from
        self.edge_to = edge_to
        self.position_from = position_from
        self.position_to = position_to
        self.depart = depart    

class Pedestrian(Person):
    def __init__(self, id, edge_from, edge_to, position_from, position_to, depart):
        super(Pedestrian, self).__init__(id, edge_from, edge_to, position_from, position_to, depart)
        self.assigned_bus = None
        self.is_waiting = True

    def picked_up(self):
        on_bus = self.on_bus()
        if self.is_waiting and on_bus:
            if not on_bus == self.assigned_bus.id:
                raise Exception("Pedestrian picked up by a bus %s but was assigned to %s" %(on_bus, self.assigned_bus.id))
            self.is_waiting = False
            return True
        else:
            return False

    def droped_off(self):
        on_bus = self.on_bus()
        if not self.is_waiting and not on_bus:
            self.is_waiting = True
            return True
        else:
            return False

    def on_bus(self):
        return traci.person.getStage(self.id).description == "driving"


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

        self.route_to_new_dest(self.update_buses_with_event())

        self.step_nbr += 1



    def new_people_waiting(self):
        if self.step_nbr in self.new_people_waiting_by_tmsp:
            return self.new_people_waiting_by_tmsp[self.step_nbr]
        else:
            return []


    def handle_new_people(self, np):
        for p in np:
            closest_bus = None
            closest_bus_distance = 0

            for bus in self.buses:
                next_destination, next_distance, _ = bus.select_next([p], False)

                if next_destination == p and (not closest_bus or next_distance < closest_bus_distance):
                    closest_bus = bus
                    closest_bus_distance = closest_bus_distance
                    

        if closest_bus:

            if not closest_bus.is_going_to_dropoff():
                self.unassigned.append(closest_bus.next_destination)
                closest_bus.next_destination.assigned_bus = None
                p.assigned_bus = closest_bus
            
            closest_bus.route_to(p)

        else:
            self.unassigned.append(p)





    def update_buses_with_event(self):
        ret = []

        for p in self.pedestrians:
            if p.picked_up():
                p.assigned_bus.onbaord.append(p)
                ret.append(p.assigned_bus)
            if p.droped_off():
                p.assigned_bus.onboard.remove(p)
                ret.append(p.assigned_bus)
                self.pedestrians.remove(p)
        return ret

    def route_to_new_dest(self, buses_to_be_routed):

        for bus in buses_to_be_routed:

            closest_next, _, will_be_pickup = bus.select_next(self.unassigned)
            
            if closest_next:
                if will_be_pickup:
                    closest_next.assigned_bus = bus
                    self.unassigned.remove(closest_next)

                bus.route_to(closest_next)


