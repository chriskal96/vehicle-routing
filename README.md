# Exploring Scotch Whiskies

This repository includes an assignment assigned for the cource "Analytics Practicum 1" offered by the Master of Science in Business Analytics of the Athens University of Economics and Business. 

## Problem

Consider a central warehouse (Node with id: 0) and a set of 𝑛 = 300 customers (Nodes with id: 1,…, 𝑛 = 300).
All nodes are in a side square of 100. Consider the transition time from node to node
is equal to the Euclidean distance between the two nodes.
Every customer 𝑖 has a required service time 𝑠𝑡
 and a profit 𝑝
.
A fleet of 𝑘 = 5 trucks is located in the central warehouse.
The vehicles start at the warehouse, serve customers and then return to the main warehouse.
Each vehicle performs one route.
Each customer can be covered (it does not have to be covered) by a single vehicle visit.
In this case, the customer returns his profit.
The total time of each route (transfer time and customer service time) can not exceed
a time limit 𝑇 = 150.

The purpose of the problem is to design 𝑘 routes that will maximize the overall profit. Obviously,
due to the limitations of the maximum time limit it is not necessary that all customers will be covered.
Instead, the selected customers must be selected and routed.

## Implementation

We created a constructive algorith for a greedy initial solution. We then created 4 operators for Local Search :

* **Relocate**: Relocate each covered customer to any different point
solution.
* **Swap**: Swap service positions of any pair of covered customers.
* **Insertion**: Insert any uncovered client anywhere in the solution.
* **Profitable Swap**: Replace any covered customer with any not
covered customer.

Finally, a VND method was created that using the previous operators optimizes the initial solution.

## Authors

<a href="https://github.com/konstantinagewrg">Konstantina Georgiopoulou</a><br/>
<a href="https://github.com/antheodorou">Anastasios Theodorou</a><br/>
<a href="https://github.com/chriskal96">Christos Kallaras</a><br/>
<a href="https://github.com/stavroskas">Stavros Kasiaris</a><br/>

