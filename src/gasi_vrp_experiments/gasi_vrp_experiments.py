import argparse
import csv
import json
import os
import matplotlib.pyplot as plt

from itertools import product 
from statistics import mean

from gasi_vrp.game import *
from gasi_vrp.gasi_vrp import ga_social_interaction_vrp
from gasi_vrp.vrp import VRP
from gasi_vrp.vrp_data_reader import read_file

""" Data sources
+ Networks obtained from CRVLIB http://vrp.galgos.inf.puc-rio.br/index.php/en/
+ Optimal solutions tabulated here: http://vrp.galgos.inf.puc-rio.br/index.php/en/ 
+ Original source used in CRVLIB
    * set A of CVRP instances from Augerat (1995): 
        - https://scholar.google.com/scholar_lookup?title=Approche%20poly%C3%A8drale%20du%20probl%C3%A8me%20de%20tourn%C3%A9es%20de%20v%C3%A9hicules&publication_year=1995&author=P.%20Augerat
+ Other solutions https://scholar.google.com/scholar?cluster=4830514486682362781&hl=en&as_sdt=0,23
"""


TEST_SET_1 = [
    ("data/augerat-1995-set-a/A-n32-k05.xml", 784),
    ("data/augerat-1995-set-a/A-n36-k05.xml", 799),
    ("data/augerat-1995-set-a/A-n44-k06.xml", 937),
    ("data/augerat-1995-set-a/A-n60-k09.xml", 1354),
    ("data/augerat-1995-set-a/A-n69-k09.xml", 1159),
]
GAMES_CODES = ["PrisonersDilemma", "HawkDove", "StagHunt", "Harmonic"]

def gap_percentage(actual, best):
    return (actual-best)/best

def instance_name(path):
    return path.split('/')[-1].replace('.xml', '')

def gameClassFactory(code):
    if code == "PrisonersDilemma":
        return PrisonersDilemmaGame()
    elif code == "HawkDove":
        return HawkDoveGame()
    elif code == "StagHunt":
        return StagHuntGame()
    elif code == "Harmonic":
        return HarmonicGame()
    else:
        return Game()

def basic_params_exp(f_path):
    runs = 10
    data = {}

    pop_size = 500
    num_gens = 2000
    
    all_data = []
    header = ['mutation rate', 'crossover rate'] + list(map(lambda x: "% Gap in "  + instance_name(x[0]), TEST_SET_1)) + ['Avg % Gap']
    all_data.append(header)
    print(header)
    for mr, cr in product([0.2, 0.4, 0.6, 0.8], [0.2, 0.4, 0.6, 0.8]):
        print(f'\n\n mutation rate = {mr}; crossover rate = {cr}')
        row = [mr, cr]
        for pth, best in TEST_SET_1:
            print('>> Instance', instance_name(pth))
            instance_results = []
            for run in range(runs):
                print(f'>> Run{run+1}/{runs}')
                vrp = VRP(*read_file(os.path.abspath(pth)))
                game = Game()
                result, routes, strategy_dist = ga_social_interaction_vrp(vrp, game, pop_size, num_gens
                    , mutation_rate=mr, crossover_rate=cr, wgt_solution=1, wgt_social=0)
                instance_results.append(result)
            row.append(gap_percentage(mean(instance_results), best))
        row.append(mean(row[2:]))
        print(row)
        all_data.append(row)
    with open('results/basic_params_exp.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)

def games_exp(f_path, mutation_rate, crossover_rate):
    runs = 10
    data = {}

    pop_size = 500
    num_gens = 2000
    
    all_data = []
    header = ['game'] + list(map(lambda x: "% Gap in "  + instance_name(x[0]), TEST_SET_1)) + ['Avg % Gap']
    all_data.append(header)
    print(header)
    for gc in GAMES_CODES:
        print(f'\n\n Game code = {gc}')
        row = [gc]
        for pth, best in TEST_SET_1:
            print('>> Instance', instance_name(pth))
            instance_results = []
            for run in range(runs):
                print(f'>> Run{run+1}/{runs}')
                vrp = VRP(*read_file(os.path.abspath(pth)))
                game = gameClassFactory(gc)
                result, routes, strategy_dist = ga_social_interaction_vrp(vrp, game, pop_size, num_gens
                    , mutation_rate=mutation_rate, crossover_rate=crossover_rate, wgt_solution=0.9, wgt_social=0.1)
                instance_results.append(result)
            row.append(gap_percentage(mean(instance_results), best))
        row.append(mean(row[2:]))
        print(row)
        all_data.append(row)
    with open('results/games_exp.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)

def weights_exp(f_path, mutation_rate, crossover_rate, game_code):
    runs = 10
    data = {}

    pop_size = 500
    num_gens = 2000
    
    all_data = []
    header = ['solution fitness weight', 'social fitness weight'] + list(map(lambda x: "% Gap in "  + instance_name(x[0]), TEST_SET_1)) + ['Avg % Gap']
    all_data.append(header)
    print(header)
    for n in range(1, 12):
        w_social = n * 0.05
        w_solution =  1 - w_social
        print(f'\n\n solution wgt = {w_solution}; social wgt = {w_social}')
        row = [w_solution, w_social]
        for pth, best in TEST_SET_1:
            print('>> Instance', instance_name(pth))
            instance_results = []
            for run in range(runs):
                print(f'>> Run{run+1}/{runs}')
                vrp = VRP(*read_file(os.path.abspath(pth)))
                game = gameClassFactory(game_code)
                result, routes, strategy_dist = ga_social_interaction_vrp(vrp, game, pop_size, num_gens
                    , mutation_rate=mutation_rate, crossover_rate=crossover_rate, wgt_solution=w_solution, wgt_social=w_social)
                instance_results.append(result)
            row.append(gap_percentage(mean(instance_results), best))
        row.append(mean(row[2:]))
        print(row)
        all_data.append(row)
    with open('results/weights_exp.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)

def comp_exp(f_path, mutation_rate, crossover_rate, game_code, w_social):
    runs = 10
    data = {}

    pop_size = 500
    num_gens = 2000
    
    all_data = []
    header = ['Algorithm'] + list(map(lambda x: "% Gap in "  + instance_name(x[0]), TEST_SET_1)) + ['Avg % Gap']
    all_data.append(header)
    print(header)

    row = ['GASI']
    for pth, best in TEST_SET_1:
        print('>> Instance', instance_name(pth))
        instance_results = []
        for run in range(runs):
            print(f'>> Run{run+1}/{runs}')
            vrp = VRP(*read_file(os.path.abspath(pth)))
            game = gameClassFactory(game_code)
            result, routes, strategy_dist = ga_social_interaction_vrp(vrp, game, pop_size, num_gens
                , mutation_rate=mutation_rate, crossover_rate=crossover_rate, wgt_solution=1-w_social, wgt_social=w_social)
            instance_results.append(result)
        row.append(gap_percentage(mean(instance_results), best))
    row.append(mean(row[2:]))
    all_data.append(row)
    print(row)

    row = ['GA']
    for pth, best in TEST_SET_1:
        print('>> Instance', instance_name(pth))
        instance_results = []
        for run in range(runs):
            print(f'>> Run{run+1}/{runs}')
            vrp = VRP(*read_file(os.path.abspath(pth)))
            game = gameClassFactory(game_code)
            result, routes, strategy_dist = ga_social_interaction_vrp(vrp, Game(), pop_size, num_gens
                , mutation_rate=mutation_rate, crossover_rate=crossover_rate, wgt_solution=1, wgt_social=0)
            instance_results.append(result)
        row.append(gap_percentage(mean(instance_results), best))
    row.append(mean(row[2:]))
    all_data.append(row)
    print(row)

    with open('results/comp_exp.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)

def parse_args():
    parser = argparse.ArgumentParser(description='Run experiments on GASI implementation')

    return parser.parse_args()


def dist_exp(f_path, mutation_rate, crossover_rate, w_social):
    runs = 5
    data = {}

    pop_size = 500
    num_gens = 2000

    for gc in GAMES_CODES:
        print(f'\n\n Game code = {gc}')
        allrows = []
        for pth, best in TEST_SET_1[:2]:
            row = []
            print('>> Instance', instance_name(pth))
            for run in range(runs):
                print(f'>> Run{run+1}/{runs}')
                vrp = VRP(*read_file(os.path.abspath(pth)))
                game = gameClassFactory(gc)
                result, routes, strategy_dist = ga_social_interaction_vrp(vrp, game, pop_size, num_gens
                    , mutation_rate=mutation_rate, crossover_rate=crossover_rate, wgt_solution=1-w_social, wgt_social=w_social)
                row = row + strategy_dist
            allrows.append(row)
        with open(f'results/dists/{gc}_dist_exp.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerows(allrows)


def plot_dist():
    base = 'results/dists/'
    filespaths = list(map(lambda x: base + x ,os.listdir('results/dists')))
    n_bins = 25
    fig, axs = plt.subplots(4, 2, sharey=True, tight_layout=True)

    dists = []
    for f in filespaths:
        if ".csv" not in f:
            continue
        with open(f) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                dists.append((f, [float(i) for i in row]))

    i = 0
    for row in axs:
        for coli_, col in enumerate(row):
            col.set_title(dists[i][0].split('_')[-1].replace('.csv', '') + f' {coli_+1}')
            col.hist(dists[i][1], n_bins, range=(0,1), density=True)
            col.set_yticks([])
            i +=1
    
    plt.savefig(base+'plots/dists.png')


def main():
    parser = argparse.ArgumentParser()    
    f_path = ""

    # basic_params_exp(f_path)
    # games_exp(f_path, mutation_rate=0.8, crossover_rate=0.6)
    # weights_exp(f_path, mutation_rate=0.8, crossover_rate=0.6, game_code="PrisonersDilemma")
    # comp_exp(f_path, mutation_rate=0.8, crossover_rate=0.6, game_code="PrisonersDilemma", w_social=0.25)
    # dist_exp(f_path, mutation_rate=0.8, crossover_rate=0.6, w_social=0.25)
    plot_dist()

if __name__ == "__main__":
    main()