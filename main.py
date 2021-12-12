# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from Model import *
from Solver import *

m = Model()

m.BuildModel()
#m.print_nodes()
#m.print_time_matrix()
s = Solver(m)
sol = s.solve()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
