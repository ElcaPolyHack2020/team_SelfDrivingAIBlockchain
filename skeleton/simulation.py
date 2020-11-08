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

    def run1(self):
        current_time = 0
        bus_id = "bus1"
        for i in range(1800): traci.simulationStep()
        current_time += 1800
        
        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=2)
        traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])

        ped = self.pedestrians[0]
        traci.vehicle.changeTarget(vehID=bus_id, edgeID=ped.edge_from)
        traci.vehicle.setStop(vehID=bus_id, edgeID=ped.edge_from, pos=ped.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

        #wait for driving
        while not (traci.vehicle.isStopped(bus_id)):
            traci.simulationStep()
            current_time += 1

        traci.vehicle.changeTarget(vehID=bus_id, edgeID=ped.edge_to)
        traci.vehicle.setStop(vehID=bus_id, edgeID=ped.edge_to, pos=102.30, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

        #wait for waiting
        while traci.vehicle.isStopped(bus_id):
            traci.simulationStep()
            current_time += 1

        

        #wait for driving
        while not (traci.vehicle.isStopped(bus_id)):
            traci.simulationStep()
            current_time += 1

        traci.vehicle.changeTarget(vehID=bus_id, edgeID=self.bus_depot_end_edge)

        #wait for waiting
        while traci.vehicle.isStopped(bus_id):
            traci.simulationStep()
            current_time += 1

        
        #wait for driving
        while not (traci.vehicle.isStopped(bus_id)):
            traci.simulationStep()
            current_time += 1






    def run(self):
        # Create a bus for the persons
        nbr_buses = 1
        buses_list = []
        pedestrians_list = []

        for i in range(nbr_buses):
            buses_list.append(Bus(utils.BUS_TYPE_L, "bus_"+str(i)))

        for pederasts in self.pedestrians:
            pedestrians_list.append(Pedestrian(pederasts.id, pederasts.edge_from,
                pederasts.edge_to, pederasts.position_from, pederasts.position_to,
                int(pederasts.depart))
            )

        tarantino = Director(pedestrians_list, buses_list)
        
        step = 0
        interact_period = 400

        #code.interact(local=locals()) # Press CTR+Z + Enter to get back to the running
        
        while step <= self.simulation_steps:
            
            step += tarantino.step()
            traci.simulationStep()

            if utils.DEBUG_MODE:
                if not step % interact_period:
                    pass
                    #code.interact(local=locals()) # Press CTR+Z + Enter to get back to the running
                if self.sleep_time > 0: 
                    pass
                    #sleep(self.sleep_time)

            #step += 1
            #print(traci.vehicle.getSubscriptionResults('bus_0'))

        traci.close()
