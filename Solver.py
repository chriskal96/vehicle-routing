from model import *
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
        self.movecost1 = 0
        self.movecost2 = 0

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9
        self.movecost1 = 0
        self.movecost2 = 0

class InsertionMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.moveCost = None
        self.uncovered = []

    def Initialize(self):
        self.originRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.moveCost = 10 ** 9
        self.uncovered = []

class UncoveredSwap(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9
        self.profit = 0
        self.uncoveredNodes = []

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9
        self.profit = 0
        self.uncoveredNodes = []

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
        self.bestSolution = None

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.MinimumInsertions()
        self.ReportSolution(self.sol)
        SolDrawer.draw('MinIns', self.sol, self.allNodes)
        #self.LocalSearch(1)
        self.VND()
        self.ReportSolution(self.sol)
        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False

    def MinimumInsertions(self):
        model_is_feasible = True
        self.sol = Solution()
        insertions = 0

        self.customers = sorted(self.customers, key=lambda x: x.pr_per_time, reverse=True)

        while insertions < len(self.customers):
            best_insertion = CustomerInsertionAllPositions()
            if len(self.sol.routes) < 5:
                self.Always_keep_an_empty_route()

            self.IdentifyMinimumCostInsertion(best_insertion)
            if best_insertion.customer is not None:
                self.ApplyCustomerInsertionAllPositions(best_insertion)
                insertions += 1
            else:
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
                                best_insertion.rt_time = trialCost + candidateCust.service_time
                                best_insertion.rt_profit = candidateCust.profit
                    else:
                        continue

    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print("| Route Duration:", rt.rt_time, " | Route Profit:", rt.rt_profit)
        print("Total Duration:", self.sol.rt_duration)
        print("Total Profit:", self.sol.rt_profit)

    def TestSolution(self):
        for r in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtTime = 0
            rtProfit = 0
            for n in range(0, len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtTime += self.timeMatrix[A.ID][B.ID] + A.service_time
                rtProfit += A.profit
            if abs(rtTime - rt.rt_time) > 0.0001:
                print('Route Time problem')

    def ApplyCustomerInsertionAllPositions(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        insIndex = insertion.insertionPosition
        rt.sequenceOfNodes.insert(insIndex + 1, insCustomer)
        rt.rt_time += insertion.rt_time
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
        ins = InsertionMove()
        usm = UncoveredSwap()
        self.searchTrajectory.append(self.sol.rt_duration)

        while terminationCondition is False:

            self.InitializeOperators(rm)
            self.InitializeOperators(sm)
            self.InitializeOperators(ins)
            self.InitializeOperators(usm)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        terminationCondition = True
                else:
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
                    terminationCondition = True
            elif operator == 2:
                self.FindBestInsertionMove(ins)
                if ins.originRoutePosition is not None:
                    self.ApplyInsertionMove(ins)
                else:
                    terminationCondition = True
            elif operator == 3:
                self.FindBestUncoveredSwapMove(usm)
                if usm.positionOfFirstRoute is not None:
                    self.ApplyUncoveredSwapMove(usm)
                else:
                    terminationCondition = True
            else:
                print("Wrong operator, try again with 0")

            self.TestSolution()

            self.bestSolution = self.cloneSolution(self.sol)
            self.searchTrajectory.append(self.sol.rt_duration)
            localSearchIterator = localSearchIterator + 1

        SolDrawer.drawTrajectory(self.searchTrajectory)
        SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)
        self.sol = self.bestSolution
        self.sol.rt_duration = self.bestSolution.duration
        self.sol.rt_profit = self.bestSolution.profit

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
        cloned.profit = self.sol.rt_profit
        return cloned

    def FindBestRelocationMove(self, rm):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[originRouteIndex]
            for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                for targetRouteIndex in range(0, len(self.sol.routes)):
                    rt2: Route = self.sol.routes[targetRouteIndex]
                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                        if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
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

                        if ((moveCost < rm.moveCost) and (rt2.rt_time + targetRtCostChange <= 150)  and (rt1.rt_time + originRtCostChange <= 150)):
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm)

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

        self.sol.rt_duration = self.CalculateTotalDuration(self.sol)

    def InitializeOperators(self, rm):
        rm.Initialize()

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex,targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm: RelocationMove):
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

    def CalculateTotalProfit(self, sol):
        c = 0
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                c = a.profit + c
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

                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                costRemoved = self.timeMatrix[a1.ID][b1.ID] + self.timeMatrix[b1.ID][b2.ID] + self.timeMatrix[b2.ID][c2.ID]
                                costAdded = self.timeMatrix[a1.ID][b2.ID] + self.timeMatrix[b2.ID][b1.ID] + self.timeMatrix[b1.ID][c2.ID]
                                moveCost = costAdded - costRemoved
                                movecost1 = moveCost
                                movecost2 = moveCost
                            else:
                                costRemoved1 = self.timeMatrix[a1.ID][b1.ID] + self.timeMatrix[b1.ID][c1.ID]
                                costAdded1 = self.timeMatrix[a1.ID][b2.ID] + self.timeMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.timeMatrix[a2.ID][b2.ID] + self.timeMatrix[b2.ID][c2.ID]
                                costAdded2 = self.timeMatrix[a2.ID][b1.ID] + self.timeMatrix[b1.ID][c2.ID]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                                movecost1 = moveCost
                                movecost2 = moveCost
                        else:
                            costRemoved1 = self.timeMatrix[a1.ID][b1.ID] + self.timeMatrix[b1.ID][c1.ID]
                            costAdded1 = self.timeMatrix[a1.ID][b2.ID] + self.timeMatrix[b2.ID][c1.ID]
                            costRemoved2 = self.timeMatrix[a2.ID][b2.ID] + self.timeMatrix[b2.ID][c2.ID]
                            costAdded2 = self.timeMatrix[a2.ID][b1.ID] + self.timeMatrix[b1.ID][c2.ID]

                            costChangeFirstRoute = costAdded1 - costRemoved1 - b1.service_time + b2.service_time
                            costChangeSecondRoute = costAdded2 - costRemoved2 - b2.service_time + b1.service_time

                            moveCost = costAdded1 - costRemoved1 - b1.service_time + b2.service_time + costAdded2 - costRemoved2 - b2.service_time + b1.service_time
                            movecost1 = costAdded1 - costRemoved1 - b1.service_time + b2.service_time
                            movecost2 = costAdded2 - costRemoved2 - b2.service_time + b1.service_time


                        if moveCost < sm.moveCost and movecost1 + rt1.rt_time <= 150 and movecost2 + rt2.rt_time <= 150:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

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

        self.sol.rt_duration = self.CalculateTotalDuration(self.sol)
        self.sol.rt_profit = self.CalculateTotalProfit(self.sol)

        newCost = self.CalculateTotalDuration(self.sol)
        # debuggingOnly
        if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
            print('Cost Issue')

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost

    def Uncovered(self):
        uncoveredNodes = []
        coveredNodes = []
        for i in range(0, len(self.sol.routes)):
            rt = self.sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes)):
                coveredNodes.append(rt.sequenceOfNodes[j].ID)

        coveredNodes = list(dict.fromkeys(coveredNodes))
        coveredNodes.sort()

        for i in coveredNodes:
            for j in range(0, len(self.allNodes)):
                if self.allNodes[j].ID in coveredNodes:
                    continue
                else:
                    uncoveredNodes.append(self.allNodes[j])

        uncoveredNodes = list(dict.fromkeys(uncoveredNodes))
        return uncoveredNodes

    def FindBestInsertionMove(self, ins):
        uncovered = self.Uncovered()
        ins.uncovered = uncovered
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[originRouteIndex]
            for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                for uncoveredNode in range(0, len(uncovered)):
                    A = rt1.sequenceOfNodes[originNodeIndex - 1]
                    B = rt1.sequenceOfNodes[originNodeIndex]
                    C = uncovered[uncoveredNode]

                    costAdded = self.timeMatrix[A.ID][C.ID] + self.timeMatrix[C.ID][B.ID] + C.service_time
                    costRemoved = self.timeMatrix[A.ID][B.ID]

                    moveCost = costAdded - costRemoved

                    if (rt1.rt_time + moveCost <= 150):
                        self.StoreBestInsertionMove(originRouteIndex, originNodeIndex,uncoveredNode, moveCost, ins)

    def StoreBestInsertionMove(self, originRouteIndex, originNodeIndex, uncoveredNode, moveCost, ins: InsertionMove):
        ins.originRoutePosition = originRouteIndex
        ins.originNodePosition = originNodeIndex
        ins.targetNodePosition = uncoveredNode
        ins.moveCost = moveCost

    def ApplyInsertionMove(self, ins: InsertionMove):

        originRt = self.sol.routes[ins.originRoutePosition]

        A = originRt.sequenceOfNodes[ins.originNodePosition - 1]
        B = originRt.sequenceOfNodes[ins.originNodePosition]
        C = ins.uncovered[ins.targetNodePosition]

        originRt.sequenceOfNodes.insert(ins.originNodePosition, C)

        originRt.rt_time += ins.moveCost
        originRt.rt_profit += C.profit
        C.isRouted = True
        self.sol.rt_duration = self.CalculateTotalDuration(self.sol)
        self.sol.rt_profit = self.CalculateTotalProfit(self.sol)

    def FindBestUncoveredSwapMove(self, usm):
        uncoveredNodes = self.Uncovered()
        usm.uncoveredNodes = uncoveredNodes
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[firstRouteIndex]
            for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                b1 = rt1.sequenceOfNodes[firstNodeIndex]
                c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]
                for i in range(0, len(uncoveredNodes)):
                    uncoveredNode = uncoveredNodes[i]

                    costRemoved = self.timeMatrix[a1.ID][b1.ID] + self.timeMatrix[b1.ID][c1.ID] + b1.service_time
                    costAdded = self.timeMatrix[a1.ID][uncoveredNode.ID] + self.timeMatrix[uncoveredNode.ID][c1.ID] + uncoveredNode.service_time
                    moveCost = costAdded - costRemoved

                    newprofit  = rt1.rt_profit + uncoveredNode.profit - b1.profit

                    if newprofit > rt1.rt_profit and moveCost + rt1.rt_time <= 150:
                        self.StoreBestUncoveredSwapMove(firstRouteIndex, firstNodeIndex, i, moveCost, newprofit, usm)

    def ApplyUncoveredSwapMove(self, usm):
        oldCost = self.CalculateTotalDuration(self.sol)
        rt1 = self.sol.routes[usm.positionOfFirstRoute]

        b1 = rt1.sequenceOfNodes[usm.positionOfFirstNode]
        b2 = usm.uncoveredNodes[usm.positionOfSecondNode]
        rt1.sequenceOfNodes[usm.positionOfFirstNode] = b2

        rt1.rt_time += usm.costChangeFirstRt
        rt1.rt_profit = usm.profit
        self.sol.rt_duration = self.CalculateTotalDuration(self.sol)
        self.sol.rt_profit = self.CalculateTotalProfit(self.sol)

        newCost = self.CalculateTotalDuration(self.sol)

        # debuggingOnly
        if abs((newCost - oldCost) - usm.moveCost) > 0.0001:
            print('Cost Issue')

    def StoreBestUncoveredSwapMove(self, firstRouteIndex, firstNodeIndex, i, moveCost,newprofit, usm):
        usm.positionOfFirstRoute = firstRouteIndex
        usm.positionOfFirstNode = firstNodeIndex
        usm.positionOfSecondNode = i
        usm.costChangeFirstRt = moveCost
        usm.moveCost = moveCost
        usm.profit = newprofit

    def VND(self):
        self.bestSolution = self.cloneSolution(self.sol)
        VNDIterator = 0
        kmax = 4
        rm = RelocationMove()
        sm = SwapMove()
        ins = InsertionMove()
        usm = UncoveredSwap()
        k = 0
        draw = True

        while k < kmax:
            self.InitializeOperators(rm)
            self.InitializeOperators(sm)
            self.InitializeOperators(ins)
            self.InitializeOperators(usm)
            if k == 3:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    if draw:
                        SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.rt_duration)
                    k = 0
                else:
                    k += 1
            elif k == 2:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    if draw:
                        SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.rt_duration)
                    k = 0
                else:
                    k += 1
            elif k == 1:
                self.FindBestInsertionMove(ins)
                if ins.originRoutePosition is not None:
                    self.ApplyInsertionMove(ins)
                    if draw:
                        SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.rt_duration)
                    k = 0
                else:
                    k += 1
            elif k == 0:
                self.FindBestUncoveredSwapMove(usm)
                if usm.positionOfFirstRoute is not None:
                    self.ApplyUncoveredSwapMove(usm)
                    if draw:
                        SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
                    VNDIterator = VNDIterator + 1
                    self.searchTrajectory.append(self.sol.rt_duration)
                    k = 0
                else:
                    k += 1

            self.bestSolution = self.cloneSolution(self.sol)

        print()
        print("Total Iterations:", VNDIterator)
        print()
        SolDrawer.draw('final_vnd', self.bestSolution, self.allNodes)
        SolDrawer.drawTrajectory(self.searchTrajectory)
