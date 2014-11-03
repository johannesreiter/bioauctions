__author__ = 'jreiter'

import logging
import random
import os
import numpy as np
import utils.output as output
import settings as sets


# get logger for biological auction simulation
logger = logging.getLogger('bioaucmult')


def initialize_population(population_size, no_strategies, max_strategy_value):
    """
    Creates and initializes all individuals with random strategies in [0,max]
    :param population_size: number of individuals in the population
    :param no_strategies: number of pure strategies
    :param max_strategy_value: highest strategy value (typically the highest reward)
    :return: pure strategies of the individuals
    """

    # normalize strategies by the maximal reward
    ind_strategies = np.random.randint(int((no_strategies-1)*max_strategy_value)+1,
                                       size=population_size) / (no_strategies-1.0)

    logger.debug('Population initialized: {}'.format(ind_strategies))

    return ind_strategies


def reset_initial_fitness(pop_fitnesses, initial_fitness):
    """
    Resets the initial fitness for all individuals in the population
    to a given value which should never become negative
    :param pop_fitnesses: fitness values of the individuals in the population
    :param initial_fitness: initial fitness values of all individuals before the auctions
    """

    for ind_idx in range(len(pop_fitnesses)):
        pop_fitnesses[ind_idx] = initial_fitness

    # logger.debug("Fitness values reset to: "+str(value))


def simulate_auctions(pop_strategies, pop_fitnesses, no_auctions, no_participants, rewards):
    """
    Simulates all auctions in a generation:
    :param pop_strategies: provides the strategy of each individual in the population
    :param pop_fitnesses: provides the fitness of each individual
    :param no_auctions: provides the number of auctions to be simulated in this generation
    :param no_participants: is the number of the randomly chosen individuals per auction
    :param rewards: is a list with the decreasing values of all rewards
    """

    # create array for the strategies of the auction participants
    participant_strategies = np.zeros(no_participants)

    for _ in range(no_auctions):

        # Choose participants from the whole population without replacement
        participants = random.sample(range(len(pop_fitnesses)), no_participants)

        # copy strategies of the participants
        for i in range(no_participants):
            participant_strategies[i] = pop_strategies[participants[i]]

        # idx_decr_participant_strats refers to the indices that would sort the
        # array "participant_strategies" in decreasing order
        idx_decr_participant_strats = np.argsort(participant_strategies)[::-1][:len(rewards)]
        # OPTIMIZATION option: if number of rewards is small just look for the highest (and second highest) bidder

        # make payment
        for participant in participants:
            pop_fitnesses[participant] -= pop_strategies[participant]
            assert pop_fitnesses[participant] > 0, "Fitness of an individual became negative: {}".format(
                pop_fitnesses[participant])

        # disburse rewards
        for idx, reward in enumerate(rewards):
            pop_fitnesses[participants[idx_decr_participant_strats[idx]]] += reward


def produce_new_generation(pop_strategies, pop_fitnesses, mutation_rate, max_strategy_value, no_strategies):
    """
    Create a new generation of individuals with strategies proportional to
    the fitnesses of the strategies in the last generation
    :param pop_strategies: strategies of the individuals in this generation
    :param pop_fitnesses: fitness values of the individuals in this generation
    :param mutation_rate: mutation rate when assigning the new strategies
    :param max_strategy_value: highest strategy value (typically the highest reward)
    :param no_strategies: number of pure strategies
    :return: strategies of the individuals in the newly created generation
    """

    # generate cumulative fitness array
    for idx in range(len(pop_fitnesses)-1):
        pop_fitnesses[idx + 1] = pop_fitnesses[idx] + pop_fitnesses[idx + 1]
    total = pop_fitnesses[len(pop_fitnesses) - 1]

    new_strategies = np.zeros(len(pop_fitnesses))

    # next mutation event is approximately exponentially distributed
    next_mut_event = random.expovariate(mutation_rate)

    # assign new strategy values to each member
    for ind in range(len(pop_fitnesses)):

        next_mut_event -= 1
        if next_mut_event <= 0:                  # mutation event
            next_mut_event += random.expovariate(mutation_rate)
            # generate random strategy
            new_strategies[ind] = (np.random.randint(int((no_strategies-1)*max_strategy_value)+1)
                                   / (no_strategies - 1.0))
        else:                                   # no mutation event
            # generate strategy proportional to the fitness of last generation
            new_strategies[ind] = pop_strategies[np.searchsorted(pop_fitnesses,
                                                                 random.random() * total, side='left')]

    return new_strategies


def run_simulation(no_generations, population_size, no_participants,
                   no_auctions, no_strategies, rewards, mutation_rate):
    """
    Simulates the evolution of bidding strategies in auctions with multiple rewards over many generations
    """

    logger.info("Simulation starts with these arguments: "+" generations="+str(no_generations)
                + ", population size="+str(population_size)+", number of participants="+str(no_participants)
                + ", number of auctions="+str(no_auctions)+", reward values="+str(rewards)
                + ", mutation rate="+str(mutation_rate)+", number of strategies="+str(no_strategies))

    fn_str_density = "strdensity_"+output.get_fn_suffix(no_generations, population_size,
                     no_participants, no_auctions, rewards, mutation_rate)+".tsv"

    # the strategy space is typically given by [0,v1]
    max_strategy_value = rewards[0]
    # in exceptional case one might want to change this maximal strategy value to a different value
    #max_strategy_value = 2.0

    # create directory for data files
    output_directory = output.init_output()

    # initialize fitness array
    pop_fitnesses = np.zeros(population_size, np.float64)
    # initialize strategy density array
    strategy_density = np.zeros(int(max_strategy_value * (no_strategies - 1.0)) + 1, np.float64)

    # initialize population with random strategies
    pop_strategies = initialize_population(population_size, no_strategies, max_strategy_value)

    # fixed initial value for each individual in the pop_size
    initial_fitness_value = min(no_auctions, 5*no_auctions*no_participants/population_size) * max_strategy_value
    logger.info("Initial fitness value: {}".format(initial_fitness_value))

    # simulating all the generations
    for gen in range(no_generations):

        # reset fitness values for each generation
        reset_initial_fitness(pop_fitnesses, initial_fitness_value)

        # track the strategy distribution over all generations
        for strategy in pop_strategies:
            strategy_density[int(round((strategy * (no_strategies - 1)), 0))] += 1

        # simulate all auctions per generations and update fitess values
        simulate_auctions(pop_strategies, pop_fitnesses, no_auctions, no_participants, rewards)

        # selection proportional to fitness values
        pop_strategies = produce_new_generation(pop_strategies, pop_fitnesses, mutation_rate,
                                                max_strategy_value, no_strategies)

        # snapshot of the population distribution for dynamics figure
        if sets.TRACK_DYNAMICS and sets.START_TRACKING <= gen <= sets.END_TRACKING and gen % sets.SAMPLING_RATE == 0:

            fn_dynamics = "dynamics_"+output.get_fn_suffix(no_generations, population_size,
                          no_participants, no_auctions, rewards, mutation_rate)+"_"+str(gen)+".dat"

            output.write_snapshot_file(os.path.join(output_directory, fn_dynamics), pop_strategies, gen,
                                       no_generations, population_size, no_strategies, no_participants,
                                       no_auctions, rewards, mutation_rate, max_strategy_value)

        # Provide status updates of the simulation and write them to the output file
        if no_generations > 100 and gen % (int(no_generations/100)) == (int(no_generations/100)-1):
            logger.debug(str(gen + 1)+" generations; current mean strategy in the population: {}".format(
                round(sum(pop_strategies)/len(pop_strategies), 3)))

            # write temporary results to file
            with open(os.path.join(output_directory, fn_str_density), "w") as f_str_density:
                output.write_settings_to_file(f_str_density, gen+1, population_size, no_participants, no_auctions,
                                              rewards, mutation_rate)
                output.write_strategy_density_file(f_str_density, strategy_density,
                                                   no_strategies, population_size, gen+1)

    logger.info("Simulation successfully finished.")

    # write final results to file
    with open(os.path.join(output_directory, fn_str_density), "w") as f_str_density:

        output.write_settings_to_file(f_str_density, no_generations, population_size, no_participants,
                                      no_auctions, rewards, mutation_rate)
        output.write_strategy_density_file(f_str_density, strategy_density,
                                           no_strategies, population_size, no_generations)

    # check if the individual strategy densities sum up to 1
    strategy_density /= float(no_generations)
    assert round(sum(strategy_density)/population_size, 5) == 1, \
        "Density sum: {}".format(sum(strategy_density)/population_size)