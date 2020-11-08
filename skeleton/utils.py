import traci


BUS_START_EDGE = '744377000#0'
BUS_STOP_EDGE = '521059831#0'

DEBUG_MODE = True

STOP_TIME = 50

BUS_TYPE_L = "BUS_L"
BUS_TYPE_M = "BUS_M"
BUS_TYPE_S = "BUS_S"

def getCapacityFromType(busType):
    if busType == BUS_TYPE_S:
        return 2
    elif busType == BUS_TYPE_M:
        return 4
    elif busType == BUS_TYPE_L:
        return 8

def getDist(edge_list):
        dist = 0
        for edge in edge_list:
            dist += traci.edge.getTraveltime(edge)
        return dist


