# How to use the GASI program to solve the capacitated VRP problem
1. In the root directorym install using pip
`$ pip install .`

2. Run the script `gasi-vrp` to use the program to solve an instance of the vehicle routing problem serialized in an xml file
`$ gasi-vrp path/to/input_file.xml -o path/to/output_file.json`

3. For help with overriding default algorithm parameters use the help option
    ```
    $ gasi-vrp --help
    usage: gasi-vrp [-h] [-p POP_SIZE] [-n NUM_GENS] [-m MUT_RATE] [-c CRO_RATE]
                    [-g {None,PrisonersDilemma,HawkDove,StagHunt,Harmonic}] [-w WGT_SOCIAL] [-o OUTPUT] [-d]
                    input

    Runs the Genetic Algorithm with Social Interaction (GASI) to solve the vehicle routing problem (VRP)

    positional arguments:
    input                 The file path of the problem instance

    optional arguments:
    -h, --help            show this help message and exit
    -p POP_SIZE           The size of the population (default: 500)
    -n NUM_GENS           The number of genrations (default: 2000)
    -m MUT_RATE           The mutation rate [0-1] (default: 0.8)
    -c CRO_RATE           The crossover rate [0-1] (default: 0.6)
    -g {None,PrisonersDilemma,HawkDove,StagHunt,Harmonic}
                            Type of game to use (default: PrisonersDilemma)
    -w WGT_SOCIAL         The weight of the social fitness (solution fitness weight is 1 - WGT_SOCIAL)
    -o OUTPUT, --output OUTPUT
                            Output file path
    -d, --debug

    ```