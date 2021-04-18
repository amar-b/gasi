#!/usr/bin/python

import argparse
import json
import math
import random
import sys
import os
from copy import deepcopy
from typing import Tuple, List

from vrp_data_reader import read_file
from vrp import VRP
from game import *
from utils import random_pairs, cut_points

class Individual:
    def __init__(self, main_chromosome: List[int], strategy_chromosome: float):
        self._main_chromosome = main_chromosome
        self._strategy_chromosome = strategy_chromosome or 0.0
        self._solution_fitness = 99999999
        self._social_fitness = 99999999
        self._total_fitness = 99999999

    def __str__(self):
        return f"{self.chromosomes()} || {self._solution_fitness} || {self._social_fitness}"
    
    def chromosomes(self):
        return (self._main_chromosome, self._strategy_chromosome)

    def fitness(self):
        return self._total_fitness

    def update_fitness_parts(self, solution_fitness, social_fitness):
        self._solution_fitness = solution_fitness
        self._social_fitness = social_fitness

    def update_total_fitness(self, max_solution_fitness, max_social_fitness, wgt_solution, wgt_social):
        if wgt_social > 0:
            self._total_fitness = wgt_solution*(self._solution_fitness/max_solution_fitness) - wgt_social*(self._social_fitness/max_social_fitness)
        else:
            self._total_fitness = self._solution_fitness


########## GENETIC OPERATORS ##########

def ox_operator(chromosomeA, chromosomeB, cp1, cp2):
    n =  len(chromosomeA)

    c1_mid = chromosomeA[cp1:cp2]
    c1_ends = [chromosomeB[i] for i in list(range(cp2, n)) + list(range(cp2)) if chromosomeB[i] not in c1_mid]
    c1 = c1_ends[n-cp2:] + c1_mid + c1_ends[:n-cp2]

    c2_mid = chromosomeB[cp1:cp2]
    c2_ends = [chromosomeA[i] for i in list(range(cp2, n)) + list(range(cp2)) if chromosomeA[i] not in c2_mid]
    c2 = c2_ends[n-cp2:] + c2_mid + c2_ends[:n-cp2]
    return (c1, c2)

def inversion_operator(chromosome, cp1, cp2):
    return chromosome[:cp1] + list(reversed(chromosome[cp1:cp2])) + chromosome[cp2:]

def gauss_operator(chromosome: float):
    return min(1.0, max(0.0, chromosome + random.gauss(mu=0, sigma=0.3)))


########## MAIN GA FUNCTIONS ##########

def random_population(vrp: VRP, game: Game, population_size: int) -> List[Individual]:
    # get location ids of non-depot locations
    destination_ids = list(i for i in vrp.locs_dictionary.keys() if i != vrp.depot_id)

    population: List[Individual] = []
    for _ in range(population_size):
        # create random order of location ids and select random strategy
        random.shuffle(destination_ids)
        main_chromosome = deepcopy(destination_ids)
        strategy_chromosome = random.random()
        
        # add random indivisual to population
        population.append(Individual(main_chromosome, strategy_chromosome))

    return population

def update_fitness(population: List[Individual], vrp: VRP, game: Game, wgt_solution: float, wgt_social: float):

    max_solution_fitness = -999999
    max_social_fitness = -999999

    for idv_1, idv_2 in random_pairs(population):
        main_chromosome_1, strategy_chromosome_1 = idv_1.chromosomes()
        main_chromosome_2, strategy_chromosome_2 = idv_2.chromosomes()
        
        # solution fitness (route costs)
        solution_fitness_1 = vrp.total_distance(main_chromosome_1)
        solution_fitness_2 = vrp.total_distance(main_chromosome_2)

        # social interaction fitness (payoffs from games)
        social_fitness_1, social_fitness_2 = game.play(strategy_chromosome_1, strategy_chromosome_2)

        # set solution and social fitness
        idv_1.update_fitness_parts(solution_fitness_1, social_fitness_1)
        idv_2.update_fitness_parts(solution_fitness_2, social_fitness_2)

        # update max solution and social fitness (used for normalization)
        max_solution_fitness = max(max_solution_fitness, max(solution_fitness_1, solution_fitness_2))
        max_social_fitness = max(max_social_fitness, max(social_fitness_1, social_fitness_2))

    # update total fitness using weights and max fitness terms
    for idv in population:
        idv.update_total_fitness(max_solution_fitness, max_social_fitness, wgt_solution, wgt_social)


def tournament_select(population: List[Individual]):
    participants = random.sample(range(len(population)), 4)

    return min([population[i] for i in participants], key=lambda idv: idv.fitness())

def reproduce(parent_1: Individual, parent_2: Individual) -> Tuple[Individual, Individual]:
    par_mc_1, par_sc_1 = parent_1.chromosomes()
    par_mc_2, par_sc_2 = parent_2.chromosomes()

    cp = cut_points(par_mc_1, 2)
    child_mc_1, child_mc_2 = ox_operator(par_mc_1, par_mc_2, *cp)
    child_sc_1, child_sc_2 = tuple(random.sample([par_sc_1, par_sc_2], 2))

    return ( Individual(child_mc_1, par_sc_1)
            , Individual(child_mc_2, child_sc_2))

def mutate(child: Individual, mutation_rate) -> Individual:
    child_mc, child_sc = child.chromosomes()

    if random.random() > mutation_rate:
        return child

    if random.random() > 0.5:
        mutated_child_mc = inversion_operator(child_mc, *cut_points(child_mc, 2))
        mutated_child_sc = child_sc
    else:
        mutated_child_mc = child_mc
        mutated_child_sc = gauss_operator(child_sc)

    return Individual(mutated_child_mc, mutated_child_sc)

def replace(population: List[Individual], offspring: List[Individual]):
    elite = int(0.1* len(population))
    population.sort(key=lambda idv: idv._solution_fitness)

    els = population[:elite]
    non_els = population[elite:]

    for c in offspring:
        i = random.choice(range(len(non_els)))
        if c.fitness() < non_els[i].fitness():
            non_els[i] = c

    return els + non_els

def fittest_solution(population: List[Individual]):
    return min(population, key=lambda idv: idv._solution_fitness)

def ga_social_interaction_vrp(vrp: VRP, game: Game
        , population_size: int, num_generations: int
        , mutation_rate=0.7, crossover_rate=0.7, wgt_solution=0.5, wgt_social=0
        , debug=False):

    population = random_population(vrp, game, population_size)

    for gen in range(num_generations):
        update_fitness(population, vrp, game, wgt_solution, wgt_social)

        offspring = []
        for i in range(population_size//2):
            p1 = tournament_select(population)
            p2 = tournament_select(population)

            if random.random() < crossover_rate and p1._main_chromosome != p2._main_chromosome:
                c1, c2 = reproduce(p1, p2)
                c1 = mutate(c1, mutation_rate)
                c2 = mutate(c2, mutation_rate)
                offspring.append(c1)
                offspring.append(c2)

        update_fitness(offspring, vrp, game, wgt_solution, wgt_social)
        population = replace(population, offspring)
        
        
        if debug and gen%100 == 0:
            print(fittest_solution(population))
            
    fittest_stn = fittest_solution(population)
    return (
        fittest_stn._solution_fitness,
        [route for route in vrp.decode_routes(fittest_stn._main_chromosome)], 
        list(map(lambda x: x._strategy_chromosome, population))
    )

def parse_args():
    def constrained_float(x):
        try:
            x = float(x)
            if x < 0.0 or x > 1.0:
                raise Exception()
            return x
        except Exception:
            raise argparse.ArgumentTypeError("Must be a number between 0 and 1")

    parser = argparse.ArgumentParser(description='Runs the Genetic Algorithm with Social Interaction (GASI) to solve the vehicle routing problem (VRP)')

    parser.add_argument('input',  help='The file path of the problem instance')
    
    parser.add_argument('-p', dest='pop_size', type=int, default=500,
        help='The size of the population (default: %(default)s)')

    parser.add_argument('-n', dest='num_gens', type=int, default=2000,
        help='The number of genrations (default: %(default)s)')

    parser.add_argument('-m', dest='mut_rate', type=constrained_float, default=0.8,
        help='The mutation rate [0-1] (default: %(default)s)')

    parser.add_argument('-c', dest='cro_rate', type=constrained_float, default=0.6,
        help='The crossover rate [0-1] (default: %(default)s)')

    parser.add_argument('-g', dest='game', type=str, default='PrisonersDilemma',
        choices=['None', 'PrisonersDilemma', 'HawkDove', 'StagHunt', 'Harmonic'],
        help='Type of game to use (default: %(default)s)')

    parser.add_argument('-w', dest='wgt_social', type=constrained_float, default=0.25,
        help='The weight of the social fitness (solution fitness weight is 1 - WGT_SOCIAL)')

    parser.add_argument('-o', '--output', help='Output file path')

    parser.add_argument('-d', '--debug', action="store_true")

    return parser.parse_args()

def echo_args(args):
    if args.debug == True:
        print('-'*30)
        print('Input file path: ', args.input)
        if args.output:
            print('Output file path: ', args.output)
        print('Population size: ', args.pop_size)
        print('Number of generations: ', args.num_gens)
        print('Mutation rate: ', args.mut_rate)
        print('Crossover rate: ', args.cro_rate)
        print('Weight of solution fitness: ', 1-args.wgt_social)
        print('Weight of social fitness: ', args.wgt_social)
        print('Game: ', args.game)
        print('-'*30)

def main():
    args = parse_args()
    echo_args(args)

    vrp = VRP(*read_file(os.path.abspath(args.input)))
    game = GameFactory.create_game(args.game)

    cost, routes, dist = ga_social_interaction_vrp(
        vrp,
        game,
        population_size=args.pop_size,
        num_generations=args.num_gens,
        mutation_rate=args.mut_rate, 
        crossover_rate=args.cro_rate, 
        wgt_solution=1-args.wgt_social, 
        wgt_social=args.wgt_social,
        debug=args.debug
    )

    solution = {
        'input': os.path.basename(args.input),
        'total distance': cost,
        'routes': [{f'route {i+1}': [l+1 for l in r]} for i, r in enumerate(routes)]
    }

    if args.debug:
        print(json.dumps(solution))
    if args.output:
        with open(args.output, 'w') as outfile:
            json.dump(solution, outfile)

if __name__ == "__main__":
    main()
