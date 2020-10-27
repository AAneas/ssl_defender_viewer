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
        self.opponents_and_shots = {}
        self.onTargetShots()
        self.defender_position_nodes = []
        self.everyGridPosition()
        self.computeDefending()
        self.sortByDefendingShots()
        self.defender_position_nodes_close_to_opponent = self.defender_position_nodes.copy()
        ###self.defending_edges = []
        #self.computeDefending()
        #self.deleteUnnecessaryDefenders()
        #print(self.isSolution()) #faire qqch de cette info
        #self.WriteSolution()

    def onTargetShots(self):
        #screen = pygame.display.set_mode(board.size) #numpy.array([1280, 960])
        for opp_id in range(self.board.problem.getNbOpponents()):
            nb_shots = 0
            kick_dir = 0
            opp_pos = self.board.problem.getOpponent(opp_id)
            while kick_dir < 2 * math.pi:
                for goal in self.board.problem.goals:
                    goal_pos = goal.kickResult(opp_pos, kick_dir)
                    if goal_pos is not None :
                        nb_shots = nb_shots + 1
                        s = Shot(opp_pos, kick_dir, goal_pos)
                        self.shot_on_target_nodes.append(s)
                    kick_dir += self.board.problem.theta_step
            self.opponents_and_shots[str(opp_pos)] = nb_shots

    def everyGridPosition(self): # faire fonction plus économique dans laquelle on ne vérifie que les points de la grille dans le range du tir
        #x = 0.0
        #y = 0.0
        ps = self.board.problem.pos_step
        w = self.board.problem.getFieldWidth()
        h = self.board.problem.getFieldHeight()
        #rr = self.board.problem.robot_radius
        for x in numpy.arange(0-w, w+ps, ps) :
            for y in numpy.arange(0-h, h+ps, ps) :
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

    #def verifySort(self):
        #print("Verify sort :")
        #for defender in self.defender_position_nodes :
            #print(len(defender.defending_shots))
            #if len(defender.defending_shots) == 11 :
            #    print(defender.pos)

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

    #def verifyShots(self):
    #    print("Verify shots :")
    #    for s in self.shot_on_target_nodes :
    #        print(str(len(s.defenders)))

    def deleteUnnecessaryDefenders(self):
        #self.verifyShots()
        # proposition : on commence par regarder les défenseurs qui défendent le moins de buts, pour chacun de ses buts, on regarde s'il est déjà défendu par qqn d'autre, si c'est le cas, on lui enlève cette défense, si une fois qu'on a tout regardé il n'a plus de buts défendus on l'enlève de la liste des noeuds
        #print("Deleting unnecessary defenders\n")
        defender_nb = 0
        #verbose = False
        while defender_nb < len(self.defender_position_nodes) :
            defender = self.defender_position_nodes[defender_nb]
            #if defender.pos == [4.199999999999953, -0.2000000000000206] :
            #    verbose = True
            #if verbose :
            #    print("defender_nb = "+str(defender_nb))
        #for defender in self.defender_position_nodes :
            #print("defends "+str(len(defender.defending_shots))+" shots")
            only_defender = False
            for shot in defender.defending_shots :
                #if verbose :
                #    print("len(shot.defenders) = "+str(len(shot.defenders)))
                if len(shot.defenders) < 2 :
                    only_defender = True
                    break
            #if verbose :
                #print("only_defender = "+str(only_defender))
            if only_defender :
                defender_nb = defender_nb + 1
                #if verbose :
                #    print("all good")
            else :
                #if verbose :
                #    print("wait a minute...")
                for shot in defender.defending_shots :
                    #if verbose :
                    #    print("shot removed")
                    shot.defenders.remove(defender)
                    #defender.defending_shots.remove(shot)
                self.defender_position_nodes.remove(defender)
            #verbose = False
        #self.verifyShots()            

    def closeToOpponent(self) :
        index = len(self.defender_position_nodes_close_to_opponent)-1
        while index >= 0 :
            if self.opponents_and_shots is None :
                break
            defending_opponent = {}
            for shot in self.defender_position_nodes_close_to_opponent[index].defending_shots :
                if str(shot.pos) not in defending_opponent :
                    defending_opponent[str(shot.pos)] = 1
                else :
                    defending_opponent[str(shot.pos)] = defending_opponent[str(shot.pos)] + 1
            defending = False
            for opponent in defending_opponent :
                if (opponent in self.opponents_and_shots) :
                    if (self.opponents_and_shots[opponent] == defending_opponent[opponent]) :
                        #print("c'est là")
                        #print(self.opponents_and_shots[opponent])
                        #print(defending_opponent[opponent])
                        #print("c'est fini\n")
                        self.opponents_and_shots.pop(opponent)
                        defending = True
            if defending == False :
                del self.defender_position_nodes_close_to_opponent[index]
            index = index - 1

    def chooseAnswer(self):
        #print("choosing")
        #print(self.areAllShotsDefended())
        #print(self.opponents_and_shots)
        #print(len(self.defender_position_nodes_close_to_opponent))
        #print(len(self.defender_position_nodes))
        #print("choice : ")
        if((self.areAllShotsDefended() and (not self.opponents_and_shots)) or ((not self.areAllShotsDefended()) and self.opponents_and_shots)) :
            if (len(self.defender_position_nodes_close_to_opponent) < len(self.defender_position_nodes)) :
                self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
                #print("choice 2")
        elif ((not self.areAllShotsDefended()) and (not self.opponents_and_shots)) :
            self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            #print("choice 2")

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

graph.deleteUnnecessaryDefenders()

graph.closeToOpponent()

graph.chooseAnswer()

print(graph.isSolution()) #faire qqch de cette info

graph.WriteSolution()

#graph.verifySort()

sys.exit()



#### Il faudra penser à gérer la détection de collision !!!!!!!