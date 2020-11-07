from time import sleep
import sys
import traci
import traci.constants as tc
import code
from models import Bus, Pedestrian, Director
import utils

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

    def waiting_pedestrians(self, current_time):
        waiting = []
        for ped in self.pedestrians:
            if ped.depart <= current_time:
               # print(traci.person.getStage(ped.id))
                waiting.append(ped)
        #print(waiting)
        return waiting

    def run(self):
        current_time = 500
        for i in range(500):traci.simulationStep()

        for veh_type_id in traci.vehicletype.getIDList():
            print(veh_type_id)
            print(traci.vehicletype.getPersonCapacity(veh_type_id))


        bus_id = "bus1"
        traci.vehicle.add(vehID=bus_id, typeID="BUS_L", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=40)
        traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
        while current_time < self.simulation_steps:
            waiting = self.waiting_pedestrians(current_time)
            if len(waiting) == 0:
                for i in range(300): traci.simulationStep()
                current_time += 300
            else:
                for person in waiting:
                    traci.vehicle.changeTarget(vehID=bus_id, edgeID=person.edge_from)
                    traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
                    #wait for driving
                    while not (traci.vehicle.isStopped(bus_id)):
                        traci.simulationStep()
                        current_time += 1

                    traci.vehicle.changeTarget(vehID=bus_id, edgeID=person.edge_to)
                    traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
                    while traci.vehicle.isStopped(bus_id):
                        traci.simulationStep()
                        current_time += 1
                    #wait for driving
                    #while not (traci.vehicle.isStopped(bus_id)):
                    #   traci.simulationStep()
                    #  current_time += 1
                    #while t raci.vehicle.isStopped(bus_id):
                    #    traci.simulationStep()
                    #    current_time += 1
                

                

        # Create a bus for the persons
        nbr_buses = 1
        buses_list = []
        pedestrians_list = []

        for i in range(nbr_buses):
            buses_list.append(Bus(4, "bus_"+str(i)))

        for pederasts in self.pedestrians:
            pedestrians_list.append(Pedestrian(pederasts.id, pederasts.edge_from,
                pederasts.edge_to, pederasts.position_from, pederasts.position_to,
                pederasts.depart)
            )

        torantino = Director(pedestrians_list, buses_list)
        
        step = 0
        while step <= self.simulation_steps:
            traci.simulationStep()
            torantino.step()

            if utils.DEBUG_MODE:
                code.interact(local=locals()) # Press CTR+Z + Enter to get back to the running
                if self.sleep_time > 0: 
                    sleep(self.sleep_time)

            step += 1
            #print(traci.vehicle.getSubscriptionResults('bus_0'))

        traci.close()
