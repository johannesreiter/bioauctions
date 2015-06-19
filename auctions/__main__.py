"""
Created on Jan 30, 2014

@author: Johannes REITER (IST Austria)
"""

import logging
import sys

from bioauctions import run_simulation


# create logger for biological auction simulation
logger = logging.getLogger('bioaucmult')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('bioaucmult.log')
fh.setLevel(logging.INFO)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def usage():
    logger.warn("Usage: python __main__.py [<generations> <pop_size> <#participants> <#auctions> "
                "<#rewards> <value_difference> <mutation_rate>] -O")
    logger.warn("Example: python __main__.py 1000000 100 5 100 3 0.25 0.005 -O")
    sys.exit(2)


if __name__ == '__main__':
    
    # set default parameter values
    no_gens = 100000
    pop_size = 100
    no_parts = 3
    no_aucts = 100
    mut_rate = 0.01
    rewardMax = 1.0
    rewardDifference = 0.5
    no_rewards = 2
 
    no_strats = 101
    
    selection_intensity_delta = 1   # ignored for now
    
    rews = [rewardMax]   # set V1
    
    args = len(sys.argv)
    if sys.argv[args-1] == '-O':
        args -= 1
    
    # read in the arguments
    if 5 <= args <= 8:
        logger.info('Argument List:'+str(sys.argv))
        no_gens = int(sys.argv[1])
        pop_size = int(sys.argv[2])
        no_parts = int(sys.argv[3])
        no_aucts = int(sys.argv[4])
        
        if args >= 7 and float(sys.argv[5]) != 0 and float(sys.argv[6]) >= 0.0:
            no_rewards = int(sys.argv[5])
            rewardDifference = float(sys.argv[6])
            #rewards.append(float(sys.argv[5]))
            
        if args >= 8 and float(sys.argv[7]) != 0.0:
            mut_rate = float(sys.argv[7])
        
    elif args == 1:
        
        no_gens = int(input("Please enter the number of generations: "))
        pop_size = int(input("Please enter the population size: "))
        no_parts = int(input("Please enter the number of participants in an auction: "))
        no_aucts = int(input("Please enter the number of auctions per generation: "))
        mut_rate = float(input("Please enter the mutation rate: "))
        #reward = int(input("Please enter the highest reward on winning an auction: "))
        no_rewards = int(input("Please enter the number of rewards: "))
        if no_rewards > 1:
            rewardDifference = float(input("Please enter the difference in successive rewards on winning auctions: "))
        else:
            rewardDifference = 0.0
        
    else:    
        logger.warn("Wrong number of arguments: "+str(args))
        usage()
    
    # check arguments
    try:    
        if no_gens < 1:
            raise ValueError("Please provide a positive number for the number of generations.")
        if no_parts < 2:
            raise ValueError("At least two participants have to compete in an auction.")
        if pop_size < no_parts:
            raise ValueError("Population needs to be larger or equal than the number of participants per auction.")
        if no_aucts < 1:
            raise ValueError("Please provide a positive number for the number of auctions per generation.")
        if mut_rate < 0.0 or mut_rate > 1:
            raise ValueError("Mutation rate needs to be in [0,1].")
        
        # calculate reward values   
        for rew in range(1, no_rewards):
            if rews[rew-1]-rewardDifference < 0:
                raise ValueError("Values for rewards need to be positive:"+str(rews[rew-1]-rewardDifference))
            rews.append(rews[rew-1]-rewardDifference)
            
        assert len(rews) == no_rewards
        assert rews[len(rews)-1] >= 0
        
    except ValueError as err:
        print("Error occurred: "+str(err))
        logger.exception("Arguments not in range!")
        usage()

    # start the simulation of the evolution of bidding strategies in auctions over many generations
    run_simulation(no_gens, pop_size, no_parts, no_aucts, no_strats, rews, mut_rate)
