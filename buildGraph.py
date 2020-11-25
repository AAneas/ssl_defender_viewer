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
        self.dist = 0.0
        self.computeDist()
        self.nb_def = 8
        self.nbDefenders()
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

    def nbDefenders(self):
        if self.board.problem.defenders is not None :
            if self.board.problem.defenders.any() :
                if self.board.problem.defenders[0].any() :
                    self.nb_def = len(self.board.problem.defenders[0])
                else :
                    self.nb_def = 0
                    print("Either 0 defenders are allowed, or bad read")

    def onTargetShots(self):
        #screen = pygame.display.set_mode(board.size) #numpy.array([1280, 960])
        for opp_id in range(self.board.problem.getNbOpponents()) :
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

    def calculateDistance(self, x1, y1, x2, y2): #  taken from https://community.esri.com/thread/158038
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
        return dist

    def isTooCloseToADefender(self, nb_defs, def_list) :
        if self.dist == 0.0 :
            return False
        x = def_list[nb_defs].pos[0]
        y = def_list[nb_defs].pos[1]
        for nb_def in range(nb_defs) :
            def_pos = def_list[nb_def].pos
            if self.calculateDistance(x,y,def_pos[0],def_pos[1]) < self.dist :
                return True
        return False

    def isTooCloseToAnOpponent(self, x, y) :
        if self.dist == 0.0 :
            return False
        for opponent in range(self.board.problem.getNbOpponents()) :
            opp_pos = self.board.problem.getOpponent(opponent)
            if self.calculateDistance(x,y,opp_pos[0],opp_pos[1]) < self.dist :
                return True
        return False
            
    def computeDist(self):
        if self.board.problem.robot_radius :
            self.dist = self.board.problem.robot_radius * 2
            if self.board.problem.min_dist :
                if self.board.problem.min_dist > self.dist :
                    self.dist = self.board.problem.min_dist
        elif self.board.problem.min_dist :
            self.dist = self.board.problem.min_dist

    def everyGridPosition(self): # faire fonction plus économique dans laquelle on ne vérifie que les points de la grille dans le range du tir
        self.defender_position_nodes.clear()
        ps = self.board.problem.pos_step
            #while ps < dist :
            #    ps = ps + self.board.problem.pos_step # afin de faire un grille G' où l'on est sûr d'être assez espacé, peut-être à enlever pour vérifier à chaque fois qu'on place un défenseur qu'il n'en touche pas un autre
        w = self.board.problem.getFieldWidth()
        h = self.board.problem.getFieldHeight()
        #rr = self.board.problem.robot_radius
        for x in numpy.arange(0-w, w+ps, ps) :
            for y in numpy.arange(0-h, h+ps, ps) :
                if self.isTooCloseToAnOpponent(x, y) == False :
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
        self.defender_position_nodes.sort(key=lambda defender: len(defender.defending_shots), reverse=True)
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

    
    
    
    
    # tester une version où on prend dans l'ordre des défenseurs avec le plus de buts, on retient ceux qui défendent un but qu'on a encore jamais couvert
    # et dans le cas où on fait attention à la distance : on ne l'ajoute pas s'il est trop proche d'un déjà pris ; et si jamais on a le temps on pourrait essayer de coder un programme qui une fois qu'on a fini cette fonction, vérifie pour tous les buts non protégés si on ne peut pas ajouter un défenseur qui le défend et remplacer les défenseurs qui entrent en collision avec le nouveau par d'autres défenseurs qui couvrent les mêmes buts mais sont suffisamment espacés 
    
    def notDefended(self, defender_nb) :
        shots = self.defender_position_nodes[defender_nb].defending_shots[:]
        for index in range(defender_nb) :
            if shots is None :
                break
            for shot in self.defender_position_nodes[index].defending_shots :
                if shot in shots :
                    shots.remove(shot)
            index = index + 1
        return shots
    
    def keepMostDefending(self) :
        defender_nb = 0
        while defender_nb < len(self.defender_position_nodes) :
            defender = self.defender_position_nodes[defender_nb]
            if (self.notDefended(defender_nb) is None) or (any(self.notDefended(defender_nb)) == False) or (self.isTooCloseToAnOpponent(defender.pos[0], defender.pos[1])) or (self.isTooCloseToADefender(defender_nb, self.defender_position_nodes)) :
                #for shot in defender.defending_shots : # à vérifier mais je crois que je n'en ai plus besoin
                #    shot.defenders.remove(defender)
                self.defender_position_nodes.remove(defender)
            else :
                defender_nb = defender_nb + 1    
    
    """def deleteUnnecessaryDefenders(self):
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
        #self.verifyShots()  """          

    def closeToOpponent(self) :
        #index = len(self.defender_position_nodes_close_to_opponent)-1
        #while index >= 0 :
        #for index in range(len(self.defender_position_nodes_close_to_opponent))
        #for def_pos in self.defender_position_nodes_close_to_opponent
        index = 0
        while index < len(self.defender_position_nodes_close_to_opponent) :
            if self.opponents_and_shots is None :
                break
            defender = self.defender_position_nodes_close_to_opponent[index]
            if (self.isTooCloseToAnOpponent(defender.pos[0], defender.pos[1]) == False) and (self.isTooCloseToADefender(index, self.defender_position_nodes_close_to_opponent) == False) :
                defending_opponent = {}
                for shot in defender.defending_shots :
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
                    #del defender
                    self.defender_position_nodes_close_to_opponent.pop(index)
                else :
                    index = index + 1
            else :
                #del defender
                self.defender_position_nodes_close_to_opponent.pop(index)

    def resetShotsDefenders(self):
        for s in self.shot_on_target_nodes :
            s.defenders = []

    def retryWithoutExtensions(self):
        if (not self.areAllShotsDefended()) and self.opponents_and_shots :
            self.dist = 0.0
            self.resetShotsDefenders()
            self.everyGridPosition()
            self.computeDefending()
            self.sortByDefendingShots()
            self.defender_position_nodes_close_to_opponent = self.defender_position_nodes.copy()
            self.keepMostDefending()
            self.closeToOpponent()
    
    def chooseAnswer(self):
        #print("choosing")
        #print(self.areAllShotsDefended())
        #print(self.opponents_and_shots)
        #print(len(self.defender_position_nodes))
        #print(len(self.defender_position_nodes_close_to_opponent))
        #print("choice : ")
        #print(len(self.defender_position_nodes))
        #print(len(self.defender_position_nodes_close_to_opponent))
        self.retryWithoutExtensions()
        if (len(self.defender_position_nodes) == 0) : # si on n'a pas trouvé de défenseurs avec la méthode de défendre le plus de tirs possibles mais qu'on en a trouvé avec la méthode de couvrir tous les tirs d'un attaquant, alors on prend le résultat de la deuxième méthode
            self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
        elif((self.areAllShotsDefended() and (not self.opponents_and_shots)) or ((not self.areAllShotsDefended()) and self.opponents_and_shots)) : # si on a trouvé une solution avec les deux méthodes, ou qu'on n'a trouvé aucune solution avec les deux méthodes, alors on prend la solution qui demande le moins de défenseurs ; il faudra peut-être changer ça quand on gèrera l'extension avec le fait que les défenseurs ne se téléportent pas pour réduire la distance à parcourir 
            if (len(self.defender_position_nodes_close_to_opponent) < len(self.defender_position_nodes)) :
                self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
                #print("choice 2")
        elif ((not self.areAllShotsDefended()) and (not self.opponents_and_shots)) : # si la méthode 1 ne défend pas tous les tirs alors que la méthode 2 si, alors on garde la méthode 2
            self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            #print("choice 2")
        # dans tous les autres cas, on garde la méthode 1 (donc pas besoin de remplacer le résultat 1 par le 2)
        #print(len(self.defender_position_nodes))
        #print(len(self.defender_position_nodes_close_to_opponent))

    def areAllShotsDefended(self):
        for shot in self.shot_on_target_nodes :
            if not shot.defenders :
                print("shot at"+str(shot.pos)+" is not defended") # en faire qqch
                return False
        return True
        
    def isSolution(self):
        if len(self.defender_position_nodes) == 0 :
            print("No defender found")
        if not self.areAllShotsDefended():
            return False 
        #if len(self.defender_position_nodes) > self.board.problem.getNbOpponents():
        #print(str(len(self.defender_position_nodes))+" > "+str(self.nb_def))
        if len(self.defender_position_nodes) > self.nb_def :
            print("Too many defenders")
            return False
        return True

    def writeSolution(self):
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

if problem.defenders is not None :
    with open(problem_path) as problem_file:
        solution = Solution(json.load(problem_file))
    graph = Graph(Board(problem, solution))
    #with open(solution_path) as solution_file:
    #    solution = Solution(json.load(solution_file))
else :
    graph = Graph(Board(problem, None))

#graph.deleteUnnecessaryDefenders()

graph.keepMostDefending()

graph.closeToOpponent()

graph.chooseAnswer()

print(graph.isSolution()) #faire qqch de cette info

graph.writeSolution()

#graph.verifySort()

sys.exit()