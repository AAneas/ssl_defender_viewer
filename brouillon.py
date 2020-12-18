import random
import sys

class Defender:
    def __init__(self, pos):#, defending_shots):
        self.pos = pos
        self.defending_shots = []

    def append_shot(self, shot):
        self.defending_shots.append(shot)

"""def partition(arr, low, high):
    i = (low-1)
    pivot = len(arr[high].defending_shots)
    for j in range(low, high):
        if len(arr[j].defending_shots) <= pivot:
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return (i+1)
    
def quickSort(arr, low, high):
    if len(arr) == 1:
        return arr
    if low < high:
        p_i = partition(arr, low, high)
        quickSort(arr, low, p_i-1)
        quickSort(arr, p_i+1, high)

def verifySort(defenders):
    for defender in defenders :
        print(defender.defending_shots)

def sortByDefendingShots(defenders):
    quickSort(defenders, 0, len(defenders)-1)
    verifySort(defenders)"""

def closeToOpponent() :
    index = len(self.defender_position_nodes_close_to_opponent)-1
    while index > 0 :
        if opponents_and_shots is None :
            break
        defending_opponent = {}
        for shot in self.defender_position_nodes_close_to_opponent[index].defending_shots :
            if shot.pos is not in defending_opponent :
                defending_opponent[shot.pos] = 1
            else :
                defending_opponent[shot.pos] = defending_opponent[shot.pos] + 1
        defending = False 
        for opponent in opponents_and_shots :
            if opponent in defending_opponent :
                opponents_and_shots.remove(opponent)
                defending = True
        if defending == False :
            del self.defender_position_nodes_close_to_opponent[index]
        index = index - 1


defenders = []
for i in range(10000) :
    d = Defender([0,0])
    for j in range(random.randint(0,3)) :
        d.append_shot(random.randint(0,33))
    defenders.append(d)

#defenders = sorted(defenders, key=lambda defender: len(defender.defending_shots))
#defenders.sort(key=lambda defender: len(defender.defending_shots))
#verifySort(defenders)
#sortByDefendingShots(defenders)