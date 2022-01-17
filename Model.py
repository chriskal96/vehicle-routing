import random
import math

class Model:

# instance variables
    def __init__(self) :
        self.allNodes = []
        self.customers = []
        self.time_matrix = []
        self.duration = -1

    def BuildModel(self):
        self.duration = 150
        totalCustomers = 300

        d = Node(0, 50, 50, 0, 0)
        self.allNodes.append(d)
        birthday = 3051996
        random.seed(birthday)
        for i in range(0, totalCustomers):
            xx = random.randint(0, 100)
            yy = random.randint(0, 100)
            service_time = random.randint(5, 10)
            profit = random.randint(5, 20)
            cust = Node(i + 1, xx, yy, service_time, profit)
            self.allNodes.append(cust)
            self.customers.append(cust)

        rows = len(self.allNodes)
        self.time_matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.time_matrix[i][j] = dist

class Node:
    def __init__(self, idd, xx, yy, st, p):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.service_time = st
        self.profit = p
        self.isRouted = False
        self.pr_per_time = p/st if st > 0 else 0

class Route:
    def __init__(self, dp, dur):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.rt_profit = 0
        self.duration = dur
        self.rt_time = 0
