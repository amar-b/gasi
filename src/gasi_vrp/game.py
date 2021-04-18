import random

class Game:
    _T, _R, _P, _S = [0, 0, 0, 0]

    def __init__(self):
        self.payoff_matrix = [
            #    Cooperate              Defect
            [ (self._R, self._R), (self._S, self._T) ],  # Cooperate
            [ (self._T, self._S), (self._P, self._P) ]   # Defect
        ]

    def payoffs(self):
        return deepcopy(self._PAYOFF_MATRIX)
        
    def play(self, p1_prob_coop, p2_prob_coop):
        row = 0 if random.random() < p1_prob_coop else 1
        col = 0 if random.random() < p2_prob_coop else 1

        return self.payoff_matrix[row][col]

class PrisonersDilemmaGame(Game):
    _T, _R, _P, _S = [5, 3, 1, 0]

class HawkDoveGame(Game):
    _T, _R, _P, _S = [5, 3, 0, 1]

class StagHuntGame(Game):
    _T, _R, _P, _S = [3, 5, 1, 0]

class HarmonicGame(Game):
    _T, _R, _P, _S = [1, 5, 0, 3]

class GameFactory:
    @staticmethod
    def create_game(code):
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