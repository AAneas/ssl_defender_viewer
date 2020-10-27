# pour lancer le programme : python3 ./buildGraph.py ./configs/basic_problem_1.json
# puis regarder computed_solution.json
# finalement vérifier avec : python3 ./main.py ./configs/basic_problem_1.json ./configs/computed_solution.json

import goal
from geometry import segmentCircleIntersection
#import board.py
import math
import sys
import json
from board import *

class Graph:
    def __init__(self, board):#, tirs cadrés, ):
        self.board = board
        self.shot_on_target_nodes = []
        self.onTargetShots()
        self.defender_position_nodes = []
        self.everyGridPosition()
        ###self.defending_edges = []
        #self.computeDefending()
        #self.deleteUnnecessaryDefenders()
        #print(self.isSolution()) #faire qqch de cette info
        #self.WriteSolution()

    def onTargetShots(self):
        #screen = pygame.display.set_mode(board.size) #numpy.array([1280, 960])
        for opp_id in range(self.board.problem.getNbOpponents()):
            kick_dir = 0
            opp_pos = self.board.problem.getOpponent(opp_id)
            while kick_dir < 2 * math.pi:
                for goal in self.board.problem.goals:
                    goal_pos = goal.kickResult(opp_pos, kick_dir)
                    if goal_pos is not None :
                        s = Shot(opp_pos, kick_dir, goal_pos)
                        self.shot_on_target_nodes.append(s)
                    kick_dir += self.board.problem.theta_step

    def everyGridPosition(self): # faire fonction plus économique dans laquelle on ne vérifie que les points de la grille dans le range du tir
        #x = 0.0
        #y = 0.0
        ps = self.board.problem.pos_step
        w = self.board.problem.getFieldWidth()
        h = self.board.problem.getFieldHeight()
        for x in numpy.arange(0-w, w+ps, ps):
            for y in numpy.arange(0-h, h+ps, ps):
                d = Defender([x,y])
                self.defender_position_nodes.append(d)

    def isDefending(self, defender, shot):
        if segmentCircleIntersection(shot.pos, shot.intersection_with_goal, defender.pos, self.board.problem.robot_radius) is not None :
            return True
        return False

    def computeDefending(self):
        for shot in self.shot_on_target_nodes :
            for defender in self.defender_position_nodes :
                if self.isDefending(defender, shot) :
                    defender.append_shot(shot)
                    shot.append_defender(defender)
                    #defending_edges.append(Defense(defender, shot))

    """def partition(self, arr, low, high):
        i = (low-1)
        pivot = len(arr[high].defending_shots)
        for j in range(low, high):
            if len(arr[j].defending_shots) <= pivot:
                i = i+1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i+1], arr[high] = arr[high], arr[i+1]
        return (i+1)
    
    def quickSort(self, arr, low, high):
        if len(arr) == 1:
            return arr
        if low < high:
            p_i = self.partition(arr, low, high)
            self.quickSort(arr, low, p_i-1)
            self.quickSort(arr, p_i+1, high)

    def verifySort(self):
        for defender in self.defender_position_nodes :
            print(defender.defending_shots)"""

    def sortByDefendingShots(self):
        #print("test 1\n")
        #self.quickSort(self.defender_position_nodes, 0, len(self.defender_position_nodes)-1)
        self.defender_position_nodes.sort(key=lambda defender: len(defender.defending_shots))
        #print("test 3\n")
        #self.verifySort()
        #print("test 4\n")

    #def deleteNonDefenders():
    #    for defender in defender_position_nodes :
    #        if not defender.defending_shots:
    #            defender_position_nodes.remove(defender)

    def verifyShots(self):
        for s in self.shot_on_target_nodes :
            print(str(len(s.defenders)))

    def deleteUnnecessaryDefenders(self):
        self.verifyShots()
        # proposition : on commence par regarder les défenseurs qui défendent le moins de buts, pour chacun de ses buts, on regarde s'il est déjà défendu par qqn d'autre, si c'est le cas, on lui enlève cette défense, si une fois qu'on a tout regardé il n'a plus de buts défendus on l'enlève de la liste des noeuds
        print("Deleting unnecessary defenders\n")
        defender_nb = 0
        verbose = False
        while defender_nb < len(self.defender_position_nodes) :
            defender = self.defender_position_nodes[defender_nb]
            if defender.pos == [4.199999999999953, -0.2000000000000206] :
                verbose = True
            if verbose :
                print("defender_nb = "+str(defender_nb))
        #for defender in self.defender_position_nodes :
            #print("defends "+str(len(defender.defending_shots))+" shots")
            only_defender = False
            for shot in defender.defending_shots :
                if verbose :
                    print("len(shot.defenders) = "+str(len(shot.defenders)))
                if len(shot.defenders) < 2 :
                    only_defender = True
                    break
            if verbose :
                print("only_defender = "+str(only_defender))
            if only_defender :
                defender_nb = defender_nb + 1
                if verbose :
                    print("all good")
            else :
                if verbose :
                    print("wait a minute...")
                for shot in defender.defending_shots :
                    if verbose :
                        print("shot removed")
                    shot.defenders.remove(defender)
                    #defender.defending_shots.remove(shot)
                self.defender_position_nodes.remove(defender)
            verbose = False
            
            
            
            
            
            
            
            
            
            
            
            #shot_nb = 0
            #while shot_nb < len(defender.defending_shots) :
            #for shot_nb in range(len(defender.defending_shots)) :
            #for shot in defender.defending_shots :
                #print("attention shot_nb = "+str(shot_nb)+" et range = "+str(range(len(defender.defending_shots))))
                #print("before "+str(len(shot.defenders)))
            #    if len(defender.defending_shots[shot_nb].defenders) > 1 : #il faudra vérifier qu'avec notre implémentation un shot ne peut pas contenir plusieurs fois le même defender
            #        defender.defending_shots[shot_nb].defenders.remove(defender)
            #        defender.defending_shots.remove(defender.defending_shots[shot_nb])
            #    else :
            #        shot_nb = shot_nb + 1


            #    if len(defender.defending_shots[shot_nb].defenders) < 2 : #il faudra vérifier qu'avec notre implémentation un shot ne peut pas contenir plusieurs fois le même defender
                    #defender.defending_shots[shot_nb].defenders.remove(defender)
                    #defender.defending_shots.remove(defender.defending_shots[shot_nb])
            #    else :
                    #shot_nb = shot_nb + 1


                    # si on finit par utiliser defending_edges[] alors il faudra lui remove aussi la denfese qui contient defender et shot, sauf si on ne la crée qu'après avoir supprimé les unnecessary defenders
                #print("after "+str(len(shot.defenders)))
            #print("before s "+str(len(defender.defending_shots))+" "+str(len(self.defender_position_nodes)))
            #print("still defends "+str(len(defender.defending_shots))+" shots")
            #if len(defender.defending_shots) < 1 :
            #    self.defender_position_nodes.remove(defender)
            #else :
            #    defender_nb = defender_nb + 1
            #print("after s "+str(len(defender.defending_shots))+" "+str(len(self.defender_position_nodes)))
        self.verifyShots()            

    def areAllShotsDefended(self):
        for shot in self.shot_on_target_nodes :
            if not shot.defenders :
                print("shot at"+str(shot.pos)+" is not defended") # en faire qqch
                return False
        return True
        
    def isSolution(self):
        if not self.areAllShotsDefended():
            return False 
        if len(self.defender_position_nodes) > self.board.problem.getNbOpponents():
            print("Too many defenders")
            return False
        return True

    def WriteSolution(self):
        f = open("./configs/computed_solution.json", "w") # à voir si on met un nom modifiable par l'utilisateur
        f.write("{\n\t\"defenders\" : [\n\t\t")
        comma = False
        for defender in self.defender_position_nodes :
            if comma == True :
                f.write(",\n\t\t")
            comma = True
            f.write(str(defender.pos))
        f.write("\n\t]\n}")
        f.close()

#class Point:
#    def __init__(self,x,y):
#        self.x = x
#        self.y = y

class Defender:
    def __init__(self, pos):#, defending_shots):
        self.pos = pos
        self.defending_shots = []

    def append_shot(self, shot):
        self.defending_shots.append(shot)

class Shot:
    def __init__(self, pos, angle, goal_pos):#, defenders):
        self.pos = pos
        self.angle = angle
        self.defenders = []
        self.intersection_with_goal = goal_pos
    
    def append_defender(self, defender):
        self.defenders.append(defender)

#class Defense:
#    def __init__(self, defender, shot):
#        self.defender = defender
#        self.shot = shot




#if (len(sys.argv) < 3):
#    sys.exit("Usage: " + sys.argv[0] + " <problem.json> <solution.json>")

if (len(sys.argv) != 2):
    sys.exit("Usage: " + sys.argv[0] + " <problem.json>")

problem_path = sys.argv[1]
#mettre un solution_name

with open(problem_path) as problem_file:
    problem = Problem(json.load(problem_file))

#with open(solution_path) as solution_file:
#    solution = Solution(json.load(solution_file))

graph = Graph(Board(problem, None))

graph.computeDefending()

graph.sortByDefendingShots()

graph.deleteUnnecessaryDefenders()

print(graph.isSolution()) #faire qqch de cette info

graph.WriteSolution()

sys.exit()



#### Il faudra penser à gérer la détection de collision !!!!!!!