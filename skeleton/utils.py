import traci


BUS_START_EDGE = '744377000#0'
BUS_STOP_EDGE = '521059831#0'

DEBUG_MODE = True


def getDist(edge_list):
        dist = 0
        for edge in edge_list:
            dist += traci.edge.getTraveltime(edge)
        return dist


