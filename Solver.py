from Model import *
from SolutionDrawer import *

class Solution:
    def __init__(self):
        self.rt_duration = 0.0
        self.rt_profit = 0.0
        self.routes = []

class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9

class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9

class CustomerInsertion(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.rt_duration = 10 ** 8

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
        #self.searchTrajectory = []
        self.bestSolution = None

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.MinimumInsertions()
        self.ReportSolution(self.sol)
        self.LocalSearch(1)
        self.ReportSolution(self.sol)
        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False

    def MinimumInsertions(self):
        model_is_feasible = True
        self.sol = Solution()
        insertions = 0


        self.customers = sorted(self.customers, key=lambda x: x.pr_per_time,reverse=True)



        while insertions < len(self.customers):
            best_insertion = CustomerInsertionAllPositions()
            if len(self.sol.routes) < 5:
                self.Always_keep_an_empty_route()

            self.IdentifyMinimumCostInsertion(best_insertion)
            if best_insertion.customer is not None:
                self.ApplyCustomerInsertionAllPositions(best_insertion)
                insertions += 1
            else:
               print("Insertion : ", insertions)
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

                            if trialCost < best_insertion.rt_time and trialCost + rt.rt_time + candidateCust.service_time<=150:
                                best_insertion.customer = candidateCust
                                best_insertion.route = rt
                                best_insertion.insertionPosition = j
                                # best_insertion.rt_duration = trialCost
                                best_insertion.rt_time = trialCost + candidateCust.service_time

                                best_insertion.rt_profit = candidateCust.profit
                    else:
                        continue

    # def ReportSolution(self, sol):
    #     for i in range(0, len(sol.routes)):
    #         rt = sol.routes[i]
    #         for j in range(0, len(rt.sequenceOfNodes)):
    #             print(rt.sequenceOfNodes[j].ID, end=' ')
    #         print('\n Duration : ', rt.rt_time)
    #         print(' Profit : ', rt.rt_profit)
    #     SolDrawer.draw('MinIns', self.sol, self.allNodes)
    #     print('\n Total Duration MinIns :', self.sol.rt_duration)
    #     print('Total Profit MinIns:', self.sol.rt_profit)

    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range (0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print(rt.rt_time)
        print (self.sol.rt_duration)

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

    def ApplyCustomerInsertionAllPositions(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        insIndex = insertion.insertionPosition
        rt.sequenceOfNodes.insert(insIndex + 1, insCustomer)
        # rt.rt_time += insertion.rt_duration
        rt.rt_time += insertion.rt_time
        # self.sol.rt_duration += insertion.rt_duration
        self.sol.rt_duration += insertion.rt_time
        self.sol.rt_profit += insertion.rt_profit
        rt.rt_profit += insCustomer.profit
        insCustomer.isRouted = True

    def LocalSearch(self, operator):
        localSearchIterator = 0
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False

        rm = RelocationMove()
        sm = SwapMove()
        #self.searchTrajectory.append(self.sol.rt_duration)

        while terminationCondition is False:

            self.InitializeOperators(rm)
            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                       self.ApplyRelocationMove(rm)
                    else:
                        #self.iterations = localSearchIterator
                        terminationCondition = True
            # Swaps
            elif operator == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:
                    if sm.moveCost < 0:
                        self.ApplySwapMove(sm)
                    else:
                        terminationCondition = True
            else:
                print("wrong operator, try again with 0")

            self.TestSolution()

            if self.sol.rt_duration < self.bestSolution.duration:
                self.bestSolution = self.cloneSolution(self.sol)
            #self.searchTrajectory.append(self.sol.rt_duration)
            localSearchIterator = localSearchIterator + 1

        #SolDrawer.drawTrajectory(self.searchTrajectory)
        self.sol = self.bestSolution
        self.sol.rt_duration = self.bestSolution.duration

    def cloneRoute(self, rt: Route):
        cloned = Route(self.depot, self.duration)
        cloned.duration = rt.duration
        cloned.rt_time = rt.rt_time
        cloned.rt_profit = rt.rt_profit
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    def cloneSolution(self, sol: Solution):
        cloned = Solution()
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)
        cloned.duration = self.sol.rt_duration
        return cloned

    def FindBestRelocationMove(self, rm):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[originRouteIndex]
            for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                for targetRouteIndex in range(0, len(self.sol.routes)):
                    rt2: Route = self.sol.routes[targetRouteIndex]
                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                        if originRouteIndex == targetRouteIndex and (
                                targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        if rt1 != rt2:
                            if rt2.rt_time + B.service_time > 150:
                                continue


                        costAdded = self.timeMatrix[A.ID][C.ID] + self.timeMatrix[F.ID][B.ID] + self.timeMatrix[B.ID][G.ID] + B.service_time
                        costRemoved = self.timeMatrix[A.ID][B.ID] + self.timeMatrix[B.ID][C.ID] + self.timeMatrix[F.ID][G.ID] - B.service_time

                        originRtCostChange = self.timeMatrix[A.ID][C.ID] - self.timeMatrix[A.ID][B.ID] - self.timeMatrix[B.ID][C.ID] - B.service_time
                        targetRtCostChange = self.timeMatrix[F.ID][B.ID] + self.timeMatrix[B.ID][G.ID] - self.timeMatrix[F.ID][G.ID] + B.service_time

                        moveCost = costAdded - costRemoved

                        if ((moveCost < rm.moveCost) and (rt2.rt_time + targetRtCostChange <=150)  and (rt1.rt_time + originRtCostChange <=150)):
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange,
                                                         targetRtCostChange, rm)



    def ApplyRelocationMove(self, rm: RelocationMove):

        oldCost = self.CalculateTotalDuration(self.sol)

        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        B = originRt.sequenceOfNodes[rm.originNodePosition]


        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if rm.originNodePosition < rm.targetNodePosition:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.rt_time += rm.moveCost
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.rt_time += rm.costChangeOriginRt
            targetRt.rt_time += rm.costChangeTargetRt
            # originRt.rt_time -= B.service_time
            # targetRt.rt_time += B.service_time


        self.sol.rt_duration = self.CalculateTotalDuration(self.sol)

        newCost = self.CalculateTotalDuration(self.sol)

    def InitializeOperators(self, rm):
        rm.Initialize()

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex,targetNodeIndex, moveCost,
                                originRtCostChange, targetRtCostChange, rm: RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    def CalculateTotalDuration(self, sol):
        c = 0
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                c += self.timeMatrix[a.ID][b.ID] + b.service_time
        return c


    def FindBestSwapMove(self, sm):
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[firstRouteIndex]
            for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                rt2: Route = self.sol.routes[secondRouteIndex]
                for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1
                    for secondNodeIndex in range(startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                costRemoved = self.timeMatrix[a1.ID][b1.ID] + self.timeMatrix[b1.ID][b2.ID] + \
                                              self.timeMatrix[b2.ID][c2.ID]
                                costAdded = self.timeMatrix[a1.ID][b2.ID] + self.timeMatrix[b2.ID][b1.ID] + \
                                            self.timeMatrix[b1.ID][c2.ID]
                                moveCost = costAdded - costRemoved
                            else:

                                costRemoved1 = self.timeMatrix[a1.ID][b1.ID] + self.timeMatrix[b1.ID][c1.ID]
                                costAdded1 = self.timeMatrix[a1.ID][b2.ID] + self.timeMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.timeMatrix[a2.ID][b2.ID] + self.timeMatrix[b2.ID][c2.ID]
                                costAdded2 = self.timeMatrix[a2.ID][b1.ID] + self.timeMatrix[b1.ID][c2.ID]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        else:
                            if rt1.rt_time - b1.service_time + b2.service_time > 150:
                                continue
                            if rt2.rt_time - b2.service_time + b1.service_time > 150:
                                continue

                            costRemoved1 = self.timeMatrix[a1.ID][b1.ID] + self.timeMatrix[b1.ID][c1.ID]
                            costAdded1 = self.timeMatrix[a1.ID][b2.ID] + self.timeMatrix[b2.ID][c1.ID]
                            costRemoved2 = self.timeMatrix[a2.ID][b2.ID] + self.timeMatrix[b2.ID][c2.ID]
                            costAdded2 = self.timeMatrix[a2.ID][b1.ID] + self.timeMatrix[b1.ID][c2.ID]

                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2

                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                        if moveCost < sm.moveCost:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                   moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

    def ApplySwapMove(self, sm):
        oldCost = self.CalculateTotalDuration(self.sol)
        rt1 = self.sol.routes[sm.positionOfFirstRoute]
        rt2 = self.sol.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

        if (rt1 == rt2):
            rt1.rt_time += sm.moveCost
        else:
            rt1.rt_time += sm.costChangeFirstRt
            rt2.rt_time += sm.costChangeSecondRt
            # rt1.load = rt1.load - b1.demand + b2.demand
            # rt2.load = rt2.load + b1.demand - b2.demand

        self.sol.rt_duration = self.CalculateTotalDuration(self.sol)

        newCost = self.CalculateTotalDuration(self.sol)
        # debuggingOnly
        if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
            print('Cost Issue')

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost,
                          costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost