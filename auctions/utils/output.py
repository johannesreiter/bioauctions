__author__ = 'jreiter'

import logging
import os
import csv
import numpy as np
import settings


# get logger for biological auction simulation
logger = logging.getLogger('bioaucmult')


def init_output():
    """
    Create and return path to the output directory
    (directory can be set in the settings.py file)
    """

    # derive correct output directory
    if os.getcwd().endswith('bioaucmult'):
        # application has been started from this directory
        # set output directory to the parent
        output_directory = os.path.join('..', settings.OUTPUT_FOLDER, '')
    else:
        output_directory = os.path.join(settings.OUTPUT_FOLDER, '')

    # create directory for data files
    try:
        if not os.path.exists(os.path.dirname(output_directory)):
            os.makedirs(os.path.dirname(output_directory))
        logger.info('Output directory: {}'.format(os.path.abspath(output_directory)))
    except OSError:
        logger.exception("Could not create output folder {} ".format(output_directory))

    return output_directory


def write_settings_to_file(file, no_generations, population_size, no_participants, no_auctions,
                           rewards, mutation_rate, max_strategy_value=0):
    """
    Write simulation settings to a file
    """

    file.write("# Number of generations: g=" + str(no_generations) + "\n")
    file.write("# Population size: N=" + str(population_size) + "\n")
    file.write("# Participants per auction: n=" + str(no_participants) + "\n")
    file.write("# Number of auctions per generations: K="+str(no_auctions)+"\n")
    file.write("# Number of rewards: m=" + str(len(rewards)) + "\n")
    file.write("# Values of rewards: ")
    for idx, reward in enumerate(rewards):
        file.write("v" + str(idx+1) + "=" + str(reward) + ", ")
    file.write("\n# Mutation rate: u="+str(mutation_rate))
    file.write("\n# Strategy space: [{},{}]".format(0, rewards[0] if max_strategy_value == 0 else max_strategy_value))
    file.write("\n\n")


def write_strategy_density_file(file, strategy_density, no_strategies, population_size, generations):
    """
    Calculate strategy density from a given array and write it to a file
    """
    file.write("Strategy\tDensity\n")
    for i in range(len(strategy_density)):
        file.write(str(i/(no_strategies-1.0))+"\t"
                   + str(round(strategy_density[i]/generations/population_size*no_strategies, 5))+"\n")


def write_snapshot_file(filename, pop_strategies, generation, no_generations, population_size,
                        no_strategies, no_participants, no_auctions, rewards, mutation_rate,
                        max_strategy_value=0):
    """
    Take a list of density values and write it to a given file
    :param filename: path to the output file
    :param pop_strategies: current strategy distribution
    :param generation: current generation
    :param no_generations: number of generations to simulate
    :param population_size: number of individuals per generation
    :param no_strategies: number of strategies in the interval [0,1]
    :param no_participants: number of participants per auction
    :param no_auctions: number of auctions per generation
    :param rewards: list with reward values (decreasing)
    :param mutation_rate: mutation rate
    :param max_strategy_value: highest strategy value in the strategy space
    """

    if max_strategy_value == 0:
        max_strategy_value = rewards[0]

    with open(filename, 'w') as dyn_file:

        write_settings_to_file(dyn_file, no_generations, population_size, no_participants,
                               no_auctions, rewards, mutation_rate, max_strategy_value=max_strategy_value)

        # initialize strategy density array
        strategy_density = np.zeros(int(max_strategy_value * (no_strategies - 1.0)) + 1, np.int)
        for strategy in pop_strategies:
            strategy_density[int(round((strategy * (no_strategies - 1)), 0))] += 1

        logger.debug("Strategy density after {} generations: {}".format(generation, strategy_density))

        tsvwriter = csv.writer(dyn_file, delimiter='\t')
        tsvwriter.writerow(['Strategy', 'Density'])
        for str_idx in range(len(strategy_density)):
            tsvwriter.writerow([str(round((str_idx / (no_strategies - 1)), 4)),
                                str(round(strategy_density[str_idx] / float(population_size),4))])


def get_fn_suffix(no_generations, population_size, no_participants, no_auctions, rewards, mutation_rate):
    """
    Returns suffix with parameter values for output-file-names
    """

    fn_suffix = "g="+str(no_generations)+"_N="+str(population_size)+"_n="+str(no_participants)+"_K="+str(no_auctions)

    for idx, reward in enumerate(rewards):

        if idx > 0 and reward == rewards[idx-1]:
            fn_suffix += "=v"+str(idx + 1)
        else:
            fn_suffix += "_v"+str(idx + 1)

        if idx + 1 >= len(rewards) or reward != rewards[idx+1]:
            fn_suffix += "="+str(reward)

    fn_suffix += "_u="+str(mutation_rate)

    return fn_suffix