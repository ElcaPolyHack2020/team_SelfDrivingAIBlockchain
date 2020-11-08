import traci
import traci.constants as tc
import utils
import code


class Bus:

    def __init__(self, typeID, id):
        self.id = id
        self.capacity = utils.getCapacityFromType(typeID)
        self.onboard = []
        self.next_destination = None
        self.stopped = True
        self.start_at = -500
        self.going_to_dropoff = False
        traci.vehicle.add(vehID=id, typeID=typeID, routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=self.capacity)
        traci.vehicle.setRoute(id, [utils.BUS_START_EDGE])
        traci.vehicle.setStop(vehID=self.id, edgeID=utils.BUS_START_EDGE, pos=0.6, laneIndex=0, duration=300, flags=tc.STOP_DEFAULT)

    def distance_to(self, p):
        bus_id = 'test_bus'
        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        traci.vehicle.setRoute(bus_id,[self.get_edge()])
        traci.vehicle.changeTarget(bus_id, p.edge_from)
        dist = utils.getDist(traci.vehicle.getRoute(bus_id))
        traci.vehicle.remove(vehID=bus_id)
        return dist

    def route_to(self, person, pickup, step_nbr):
        self.next_destination = person
        person.assigned_bus = self

        self.going_to_dropoff = not pickup
        
        self.stopped = False
        self.start_at = step_nbr

        print("####################### Setting new route to ", str(person.id) )

        #split = traci.vehicle.getRoute(self.id)[-1].split("#")
        #edge = int(split[0])
        
        #traci.vehicle.setRoute(self.id, [edge + str(-int(1 - edge))])
        #traci.vehicle.changeTarget(self.id, str(-edge)+"#"+split[1])

        if pickup:
            traci.vehicle.changeTarget(self.id,person.edge_from)
            traci.vehicle.setStop(vehID=self.id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=utils.STOP_TIME, flags=tc.STOP_DEFAULT)
        else:
            traci.vehicle.changeTarget(self.id, person.edge_to)
            traci.vehicle.setStop(vehID=self.id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=utils.STOP_TIME, flags=tc.STOP_DEFAULT)
        print("asdfasdfasdfasdfasdfasdfsadf")
        print(traci.vehicle.getRoute(self.id))


    def just_stopped(self, step_nbr):
        window_buffer = 55 if self.going_to_dropoff else 0
        ret = not self.stopped and traci.vehicle.isStopped(self.id) and self.start_at < step_nbr - window_buffer
        if ret:
            self.stopped = True
            #traci.simulationStep()
        return ret

    def pickup(self):
        traci.vehicle.changeTarget(self.id, self.next_destination.edge_to)
        traci.vehicle.setStop(vehID=self.id, edgeID=self.next_destination.edge_to, pos=self.next_destination.position_to, laneIndex=0, duration=utils.STOP_TIME, flags=tc.STOP_DEFAULT)
        #if utils.DEBUG_MODE:
        #    print("Marius's pickup stop")
        #    code.interact(local=locals())
        #traci.simulationStep()

    def dropoff(self):
        #traci.vehicle.changeTarget(self.id, utils.BUS_STOP_EDGE)
        #traci.vehicle.setStop(vehID=self.id, edgeID=utils.BUS_STOP_EDGE, pos=0.1, laneIndex=0, duration=utils.STOP_TIME, flags=tc.STOP_DEFAULT)
        #traci.simulationStep()
        if utils.DEBUG_MODE:
            print("Marius's drop stop !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            #code.interact(local=locals())

        #traci.vehicle.setRoute(self.id, [utils.BUS_START_EDGE])
        
        #traci.vehicle.changeTarget(self.id, utils.BUS_START_EDGE)
        #traci.vehicle.setStop(vehID=self.id, edgeID=utils.BUS_START_EDGE, pos=0.1, laneIndex=0, duration=utils.STOP_TIME, flags=tc.STOP_DEFAULT)
        
        #traci.simulationStep()
        

    def is_going_to_dropoff(self):
        ret = self.next_destination in self.onboard
        if ret != self.going_to_dropoff:
            raise Exception("nope")
        return ret

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
                if self.next_destination:
                    new_pickups_candidates.append(self.next_destination)
                on_board_candidates = []
        closest_next = None
        closest_distance = 0
        will_be_pickup = False

        # Consider to drop off someone first
        for p_onboard in on_board_candidates:
            dist = self.distance_to(p_onboard)
            if not closest_next or dist < closest_distance:
                closest_distance = dist
                closest_next = p_onboard

        # Or pick up?
        #if not self.is_full() and len(self.onboard) == 0:
        if not self.is_full():
            for p_pickup in new_pickups_candidates:
                if not p_pickup.assigned_bus or p_pickup.assigned_bus == self:
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
        self.is_dropped_off = False
        self.is_picked_up = False

class Pedestrian(Person):
    def __init__(self, id, edge_from, edge_to, position_from, position_to, depart):
        super(Pedestrian, self).__init__(id, edge_from, edge_to, position_from, position_to, depart)
        self.assigned_bus = None
        self.is_waiting = True
        self.has_been_on_a_bus = False

    def picked_up(self):
        on_bus = self.on_bus()
        if not self.has_been_on_a_bus and self.is_waiting and on_bus:
            if not on_bus == self.assigned_bus.id:
                raise Exception("Pedestrian picked up by a bus %s but was assigned to %s" %(on_bus, self.assigned_bus.id))
            self.is_waiting = False
            self.has_been_on_a_bus = True
            return True
        else:
            return False

    def droped_off(self):
        on_bus = self.on_bus()
        if not self.is_waiting and not on_bus:
            self.is_waiting = False
            self.is_dropped_off = True
            return True
        else:
            return False

    def on_bus(self):
        return traci.person.getVehicle(self.id)


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
                new_people_waiting_by_tmsp[tmsp].append(p)
            else:
                new_people_waiting_by_tmsp[tmsp] = [p]

        self.new_people_waiting_by_tmsp = new_people_waiting_by_tmsp


    def step(self):
        try:
            if self.step_nbr == 2067 or self.step_nbr == 2068:
                print("Stopping at step ", self.step_nbr)
                code.interact(local=locals())


            self.ensure_events()
  
            self.handle_new_people(self.new_people_waiting())
            
            self.route_to_new_dest(self.update_buses_with_event())
         
            self.step_nbr += 1
            return 1
        except Exception as e:
            print(e)
            code.interact(local=locals())

    def ensure_events(self):
        for bus in self.buses:
            if bus.just_stopped(self.step_nbr):
                if bus.is_going_to_dropoff():
                    bus.dropoff()
                else:
                    bus.pickup()
                

    def new_people_waiting(self):

        if self.step_nbr in self.new_people_waiting_by_tmsp:
            return self.new_people_waiting_by_tmsp[self.step_nbr]
        else:
            return []


    def handle_new_people(self, np):
        if utils.DEBUG_MODE and np:
            print(len(np), " new people at step ", self.step_nbr)

        for p in np:
            closest_bus = None

            for bus in self.buses:
                next_destination, next_distance, _ = bus.select_next([p], False)

                if next_destination == p and (not closest_bus or next_distance < closest_bus_distance):
                    closest_bus = bus
                    closest_bus_distance = next_distance
                    

            if closest_bus:

                if not closest_bus.is_going_to_dropoff() and closest_bus.next_destination:
                    self.unassigned.append(closest_bus.next_destination)
                    closest_bus.next_destination.assigned_bus = None
                p.assigned_bus = closest_bus
                
                closest_bus.route_to(p, True, self.step_nbr)

            else:
                self.unassigned.append(p)


    def update_buses_with_event(self):
        ret = []

        for p in self.pedestrians:
            #if p.depart < self.step_nbr and not p.has_been_on_a_bus and p.is_waiting:
            if p.depart < self.step_nbr:
                
                if p.is_waiting:
                   
                    if p.picked_up():
                        
                        p.assigned_bus.onboard.append(p)
                        ret.append(p.assigned_bus)
                
                    
                elif not p.is_dropped_off:
                    if p.droped_off():
                        print("#################################################")
                        p.assigned_bus.onboard.remove(p)
                        ret.append(p.assigned_bus)
                        self.pedestrians.remove(p)
                
        return ret

    def route_to_new_dest(self, buses_to_be_routed):
        
        for bus in buses_to_be_routed:
            
            closest_next, _, will_be_pickup = bus.select_next(self.unassigned, True)
           
            if closest_next:
               
                if will_be_pickup:
                    closest_next.assigned_bus = bus
                    self.unassigned.remove(closest_next)

                bus.route_to(closest_next, will_be_pickup, self.step_nbr)
            else:
                print("####################### Did not find closest next ")


