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

    def run(self):
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
