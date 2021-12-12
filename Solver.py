from Model import *
from SolutionDrawer import *


class Solution:
    def __init__(self):
        self.rt_duration = 0.0
        self.routes = []


# class CustomerInsertion(object):
#     def __init__(self):
#         self.customer = None
#         self.route = None
#         self.rt_duration = 10 ** 8


class CustomerInsertionAllPositions(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.insertionPosition = None
        self.rt_time = 10 ** 8
        # self.rt_duration = 10 ** 8
        self.rt_profit = 0



class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.timeMatrix = m.time_matrix
        self.duration = m.duration
        self.sol = None
        # self.bestSolution = None

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.MinimumInsertions()
        self.ReportSolution(self.sol)
        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False

    def MinimumInsertions(self):
        model_is_feasible = True
        self.sol = Solution()
        insertions = 0

        def pr_per_time(x):
            if x.service_time == 0:
                return 0
            else:
                return x.profit / x.service_time

        self.allNodes = sorted(self.allNodes, key=pr_per_time)


        while insertions < len(self.customers):
            best_insertion = CustomerInsertionAllPositions()
            if len(self.sol.routes) < 5:
                self.Always_keep_an_empty_route()

            self.IdentifyMinimumCostInsertion(best_insertion)
            if best_insertion.customer is not None:
                self.ApplyCustomerInsertionAllPositions(best_insertion)
                insertions += 1
            else:
                print('FeasibilityIssue')
                model_is_feasible = False
                break

        if model_is_feasible:
            self.TestSolution()


    def Always_keep_an_empty_route(self):
        if len(self.sol.routes) == 0:
            rt = Route(self.depot, self.duration)
            self.sol.routes.append(rt)
        else:
            rt = self.sol.routes[-1]
            if len(rt.sequenceOfNodes) > 2:
                rt = Route(self.depot, self.duration)
                self.sol.routes.append(rt)

    def IdentifyMinimumCostInsertion(self, best_insertion):
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                for rt in self.sol.routes:
                    if rt.rt_time + candidateCust.service_time <= rt.duration:
                        for j in range(0, len(rt.sequenceOfNodes) - 1):
                            A = rt.sequenceOfNodes[j]
                            B = rt.sequenceOfNodes[j + 1]
                            costAdded = self.timeMatrix[A.ID][candidateCust.ID] + self.timeMatrix[candidateCust.ID][B.ID]
                            costRemoved = self.timeMatrix[A.ID][B.ID]
                            trialCost = costAdded - costRemoved


                            if trialCost < best_insertion.rt_time and trialCost + rt.rt_time <=150:
                                best_insertion.customer = candidateCust
                                best_insertion.route = rt
                                best_insertion.insertionPosition = j
                                # best_insertion.rt_duration = trialCost
                                best_insertion.rt_time = trialCost

                                best_insertion.rt_profit = candidateCust.profit
                    else:
                        continue

    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print ('\n Duration : ', rt.rt_time)
        SolDrawer.draw('MinIns', self.sol, self.allNodes)
        print(self.sol.rt_duration)


    def GetLastOpenRoute(self):
        if len(self.sol.routes) == 0:
            return None
        else:
            return self.sol.routes[-1]

    def CalculateTotalCost(self, sol):
        c = 0
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                c += self.distanceMatrix[a.ID][b.ID]
        return c

    def UpdateRouteCostAndLoad(self, rt: Route):
        tc = 0
        tl = 0
        for i in range(0, len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[i]
            B = rt.sequenceOfNodes[i + 1]
            tc += self.distanceMatrix[A.ID][B.ID]
            tl += A.demand
        rt.load = tl
        rt.cost = tc

    def TestSolution(self):
        totalSolCost = 0
        for r in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost = 0
            rtLoad = 0
            for n in range(0, len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += self.timeMatrix[A.ID][B.ID]
                rtLoad += A.service_time
            # if abs(rtCost - rt.duration) > 0.0001:
            #     print('Route Cost problem')
            # if rtLoad != rt.rt_time:
            #     print('Route Load problem')

            totalSolCost += rt.duration

        # if abs(totalSolCost - self.sol.rt_duration) > 0.0001:
        #     print('Solution Cost problem')

    def IdentifyBestInsertionAllPositions(self, best_insertion, rt):
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    for j in range(0, len(rt.sequenceOfNodes) - 1):
                        A = rt.sequenceOfNodes[j]
                        B = rt.sequenceOfNodes[j + 1]
                        costAdded = self.distanceMatrix[A.ID][candidateCust.ID] + self.distanceMatrix[candidateCust.ID][
                            B.ID]
                        costRemoved = self.distanceMatrix[A.ID][B.ID]
                        trialCost = costAdded - costRemoved

                        if trialCost < best_insertion.cost:
                            best_insertion.customer = candidateCust
                            best_insertion.route = rt
                            best_insertion.cost = trialCost
                            best_insertion.insertionPosition = j

    def ApplyCustomerInsertionAllPositions(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        insIndex = insertion.insertionPosition
        rt.sequenceOfNodes.insert(insIndex + 1, insCustomer)
        # rt.rt_time += insertion.rt_duration
        rt.rt_time += insertion.rt_time
        # self.sol.rt_duration += insertion.rt_duration
        self.sol.rt_duration += insertion.rt_time
        rt.rt_profit += insCustomer.profit
        insCustomer.isRouted = True

