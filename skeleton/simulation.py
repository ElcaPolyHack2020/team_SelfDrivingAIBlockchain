import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import sys
import traci
import traci.constants as tc
import code

class Simulation:
    def __init__(self, simulation_steps, sleep_time, pedestrians, bus_depot_start_edge, bus_depot_end_edge):
        self.simulation_steps = simulation_steps
        self.sleep_time = sleep_time
        self.pedestrians = pedestrians
        self.bus_depot_start_edge = bus_depot_start_edge
        self.bus_depot_end_edge = bus_depot_end_edge

    def getDist(self, start_edge, end_edge, edge_list):
        dist = 0
        for edge in edge_list:
            dist += traci.edge.getTraveltime(edge)
        return dist


    def run(self):
        traci.simulationStep()
        bus_id = 'bus1'
        person = self.pedestrians[0]
        traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
        traci.vehicle.setRoute(bus_id,[self.bus_depot_start_edge])
        traci.vehicle.changeTarget(bus_id,self.bus_depot_end_edge)
        print(self.getDist(123,123, traci.vehicle.getRoute(bus_id)))
       
        # traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge, person.edge_from,person.edge_to])
        # print(traci.vehicle.getRoute(bus_id))
        # traci.vehicle.changeTarget(bus_id, person.edge_from)
        # print(traci.vehicle.getRoute(bus_id))
        # traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=500, flags=tc.STOP_DEFAULT)
        # print(traci.vehicle.getRoute(bus_id))

        #traci.vehicle.setRoute(bus_id, [person.edge_from])
        #traci.vehicle.changeTarget(bus_id, person.edge_to)
        #traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)


        dist = []
        drivingDist2D = []
        drivingDist = []

        step = 0
        self.simulation_steps = 400
        while step <= self.simulation_steps:
            step += 1
            traci.simulationStep()
            #dist.append(traci.vehicle.getDistance(bus_id))
            #drivingDist2D.append(traci.vehicle.getDrivingDistance2D(bus_id,person.edge_from,person.position_from))
            code.interact(local=locals()) # Press CTR+Z + Enter to get back to the running
            try:
                print('{} - {}'.format(step, traci.vehicle.getDrivingDistance(bus_id,person.edge_from,person.position_from)))
            except :
                pass
            if self.sleep_time > 0: 
                sleep(self.sleep_time)

        traci.close()

        dist = np.array(dist)
        drivingDist2D = np.array(drivingDist2D)
        drivingDist = np.array(drivingDist)

        plt.figure()
        plt.plot(np.arange(dist.shape[0]), dist)
        
        plt.figure()
        plt.plot(np.arange(drivingDist2D.shape[0]), drivingDist2D)

        plt.figure()
        plt.plot(np.array(drivingDist.shape[0]),drivingDist)

    # def run(self):
    #     # Create a bus for the persons
    #     bus_index = 0
    #     for person in self.pedestrians:
    #         bus_id = f'bus_{bus_index}'
    #         bus_index += 1

    #         try:
    #             traci.vehicle.add(vehID=bus_id, typeID="BUS_S", routeID="", depart=person.depart + 240.0, departPos=0, departSpeed=0, departLane=0, personCapacity=4)
    #             traci.vehicle.setRoute(bus_id, [self.bus_depot_start_edge])
                
    #             traci.vehicle.changeTarget(bus_id, person.edge_from)
    #             traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_from, pos=person.position_from, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)
                

    #             traci.vehicle.setRoute(bus_id, [person.edge_from])
    #             traci.vehicle.changeTarget(bus_id, person.edge_to)
    #             traci.vehicle.setStop(vehID=bus_id, edgeID=person.edge_to, pos=person.position_to, laneIndex=0, duration=50, flags=tc.STOP_DEFAULT)

    #         except traci.exceptions.TraCIException as err:
    #             print("TraCIException: {0}".format(err))
    #         except:
    #             print("Unexpected error:", sys.exc_info()[0])
    #         break

    #     traci.vehicle.subscribe('bus_0', (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_POSITION , tc.VAR_NEXT_STOPS ))

    #     step = 0
    #     while step <= self.simulation_steps:
    #         #my_step()
    #         traci.simulationStep()
    #         if self.sleep_time > 0: 
    #             sleep(self.sleep_time)
    #         step += 1
    #         #print(traci.vehicle.getSubscriptionResults('bus_0'))

    #     traci.close()


# def my_step():
#     # running parameter: unassigned people
    
#     if new_people_arrived is p:
#         closest_bus = None

#         for b in buses:
#             if not b.full:
#                 if b.dist(p) < closest_bus and b.would_be_ext(p):
#                     closest_bus = b


    
