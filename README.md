## Multiple rewards in Biological Auctions


### The easiest way to run the computer simulation:
1. Open a terminal and clone the repository from GitHub with ```git clone https://github.com/johannesreiter/bioauctions.git```
2. Go into the new folder with ```cd bioauctions```
3. Type the following command to run the simulation: ```python auctions -O```

##### Running the simulation with given parameter values:

Usage: ```python auctions [<generations> <population_size> <#participants> <#auctions> <#rewards> <value_difference> <mutation_rate>] -O```

Example: ```python auctions -O 1000000 1000 5 1000 3 0.25 0.005```  
Simulates 1000000 generations of a population with 1000 individuals, 1000 auctions per generation, 5 participants per auction,
rewards with values 1.0, 0.75, 0.5 and a mutation rate of 0.5%.


Author: Johannes Reiter, IST Austria, [http://pub.ist.ac.at/~jreiter](http://pub.ist.ac.at/~jreiter)  
Latest version can be found here: [https://github.com/johannesreiter/bioauctions](https://github.com/johannesreiter/bioauctions)
