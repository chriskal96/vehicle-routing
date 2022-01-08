from Model import *
from SolutionDrawer import *


class Solution:
    def __init__(self):
        self.rt_duration = 0.0
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
        self.moveCost = None
    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9
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
        self.searchTrajectory = []
        # self.bestSolution = None

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.MinimumInsertions()
        self.ReportSolution(self.sol)
        self.LocalSearch(0)
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

    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print ('\n Duration : ', rt.rt_time)
        SolDrawer.draw('MinIns', self.sol, self.allNodes)
        print(self.sol.rt_duration)


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
        rt.rt_profit += insCustomer.profit
        insCustomer.isRouted = True



    def LocalSearch(self, operator):
        localSearchIterator = 0
        self.bestSolution = self.cloneSolution(self.sol)

        terminationCondition = False

        rm = RelocationMove()

        self.searchTrajectory.append(self.sol.rt_duration)

        while terminationCondition is False:

            self.InitializeOperators(rm, )
            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        self.iterations = localSearchIterator
                        terminationCondition = True
            else:
                print("wrong operator, try again with 0")

            self.TestSolution()

            if self.sol.rt_duration < self.bestSolution.rt_duration:
                self.bestSolution = self.cloneSolution(self.sol)
            self.searchTrajectory.append(self.sol.rt_duration)
            localSearchIterator = localSearchIterator + 1

        SolDrawer.drawTrajectory(self.searchTrajectory)
        self.sol = self.bestSolution

    def cloneRoute(self, rt: Route):
        cloned = Route(self.depot, self.duration)
        cloned.duration = rt.duration
        #cloned.load = rt.load
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
            for targetRouteIndex in range(0, len(self.sol.routes)):
                rt2: Route = self.sol.routes[targetRouteIndex]
                for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                        if originRouteIndex == targetRouteIndex and (
                                targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]


                        costAdded = self.timeMatrix[A.ID][C.ID] + self.timeMatrix[F.ID][B.ID] + \
                                    self.timeMatrix[B.ID][G.ID]
                        costRemoved = self.timeMatrix[A.ID][B.ID] + self.timeMatrix[B.ID][C.ID] + \
                                      self.timeMatrix[F.ID][G.ID]

                        originRtCostChange = self.timeMatrix[A.ID][C.ID] - self.timeMatrix[A.ID][B.ID] - \
                                             self.timeMatrix[B.ID][C.ID]
                        targetRtCostChange = self.timeMatrix[F.ID][B.ID] + self.timeMatrix[B.ID][G.ID] - \
                                             self.timeMatrix[F.ID][G.ID]

                        moveCost = costAdded - costRemoved - (10**6)*(rt2.rt_profit - rt1.rt_profit)

                        if (moveCost < rm.moveCost) and abs(moveCost) \
                                and originRtCostChange + rt1.rt_time < self.sol.rt_duration and targetRtCostChange + rt2.rt_time < \
                                self.sol.rt_duration:
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                         targetNodeIndex, moveCost, originRtCostChange,
                                                         targetRtCostChange, rm)

    def ApplyRelocationMove(self, rm: RelocationMove):

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


        self.sol.rt_duration = self.CalculateTotalCost(self.sol)

    def InitializeOperators(self, rm):
        rm.Initialize()

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex,
                                targetNodeIndex, moveCost,
                                originRtCostChange, targetRtCostChange, rm: RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    def CalculateTotalCost(self, sol):
        c = []
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            r = []
            for j in range(0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                r.append(self.timeMatrix[a.ID][b.ID])
            c.append(sum(r))
        cst = max(c)
        return cst