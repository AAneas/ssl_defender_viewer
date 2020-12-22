# pour lancer le programme : python3 ./buildGraph.py ./configs/basic_problem_1.json
# puis regarder computed_solution.json
# finalement vérifier avec : python3 ./main.py ./configs/basic_problem_1.json ./configs/computed_solution.json

"""
sh runAll.sh

ou

python3 ./buildGraph.py ./configs/basic_problem_1.json
python3 ./main.py ./configs/basic_problem_1.json ./configs/sol_to_basic_problem_1.json

python3 ./buildGraph.py ./configs/basic_problem_2.json
python3 ./main.py ./configs/basic_problem_2.json ./configs/sol_to_basic_problem_2.json

python3 ./buildGraph.py ./configs/goal_keeper_problem_1.json
python3 ./main.py ./configs/goal_keeper_problem_1.json ./configs/sol_to_goal_keeper_problem_1.json

python3 ./buildGraph.py ./configs/initial_defenders_problem_1.json
python3 ./main.py ./configs/initial_defenders_problem_1.json ./configs/sol_to_initial_defenders_problem_1.json

python3 ./buildGraph.py ./configs/min_dist_problem_1.json
python3 ./main.py ./configs/min_dist_problem_1.json ./configs/sol_to_min_dist_problem_1.json

python3 ./buildGraph.py ./configs/multigoal_problem_1.json
python3 ./main.py ./configs/multigoal_problem_1.json ./configs/sol_to_multigoal_problem_1.json

python3 ./buildGraph.py ./configs/max_speed_problem_1.json
python3 ./main.py ./configs/max_speed_problem_1.json ./configs/sol_to_max_speed_problem_1.json

"""

import goal
from geometry import segmentCircleIntersection
import itertools
#import board.py
import math
import sys
import json
from board import *

"""field_limits = [[-4.5,4.5], [-3,3]]
goals = [[[[4.5, -0.5], [4.5,0.5]], [-1,0]]]
opponents = [[0.5, 0.0], [-2.0, -2.0], [2, 1.0]]
robot_radius = 0.09
theta_step = 0.031416
pos_step = 0.1
goalkeeper_area = None
defenders = None
ball_max_speed = None
robot_max_speed = None
min_dist = None
name = None"""

opt_ga = True
opt_d = True
opt_ms = True
opt_mi = True

opt_kd = True
opt_co = True
opt_bf = False
opt_re = True

def computeStart(lower_limit, ps):
        s = 0
        while s >= lower_limit :
            s = s - ps
        return s + ps

def calculateDistance(x1, y1, x2, y2): #  taken from https://community.esri.com/thread/158038
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
    return dist

def cutList(node_list, index, cond):
    #print(cond)
    if (cond) or (len(node_list[index].defending_shots) == 0) :
        #print(str(cond))
        #print(str(len(node_list[index].defending_shots)))
        #print(str(index))
        #print(str(len(node_list)))
        node_list[:] = node_list[:index]
        #print(str(len(node_list)))
        return True
    return False

def permutations(iterable): # taken then modified from https://docs.python.org/3/library/itertools.html#itertools.permutations # vérifier que ça fonctionne avec les modifications
    pool = tuple(iterable)
    n = len(pool)
    indices = list(range(n))
    cycles = list(range(n, 0, -1))
    yield tuple(pool[i] for i in indices[:n])
    while n:
        for i in reversed(range(n)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                #if(pool[indices[i]] != pool[indices[-j]]):
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:n])
                break
        else:
            return

"""def listFillWithDefenders(final_list, length, start) :
    for i in range(length-len(final_list)) :
        final_list.append(start[i+len(final_list)])"""

def listFillWithMinusOnes(final_list, length) :
    for i in range(length-len(final_list)) :
        final_list.append(-1)

def changeMinusOnesToDefenders(start, end):
    for index in range(len(end)) :
        if end[index] == -1 :
            end[index] = start[index]
    
def totalDistance(start, end):
    total = 0
    #print(str(start))
    #print(str(len(start)))
    #print(str(end))
    #print(str(len(end)))
    for defender_nb in range(len(end)) : #il faut qu'il n'y ait pas plus dans end que dans start
        #print(str(defender_nb))
        #print(str(start[defender_nb]))
        if end[defender_nb] != -1 :
            total = total + calculateDistance(start[defender_nb].pos[0], start[defender_nb].pos[1], end[defender_nb].pos[0], end[defender_nb].pos[1])
    return total

def orderedByDistance(final_list, starting_pos, total_distance, current_list):
    #sub_list = []
    #print(current_list)
    listFillWithMinusOnes(current_list, len(starting_pos))
    #print(current_list)
    perms = permutations(current_list)
    prev_perm = []
    for trying_current in perms :
        #print(trying_current)
        #print(prev_perm)
        if trying_current != prev_perm :
            prev_perm = trying_current[:]
            #print(trying_current)
            new_dist = totalDistance(starting_pos, trying_current)
            #if (trying_current[1] != -1) and (trying_current[7] != -1) and (trying_current[9] != -1) :
            #    print("before "+str(total_distance)+" now "+str(new_dist))
            #    print(str(trying_current))
            if new_dist < total_distance :
                #print("from "+str(total_distance)+" to "+str(new_dist))
                total_distance = new_dist
                final_list[:] = trying_current[:]
    return total_distance

    #orderedByDistance(self.defender_position_nodes, self.starting_pos, total_distance, self.defender_position_nodes_close_to_opponent)

def isBetween(start, end, pos) :
    if (pos >= min(start,end)) and ((pos <= max(start,end))) :
        return True
    return False

def deleteUselessDefenders(node_list, index):
    deleting = 0
    for i in range(index-1-deleting):
        defended_shots = node_list[i].defending_shots[:]
        for j in range(index-deleting):
            if i != j :
                for s in node_list[j].defending_shots :
                    if s in defended_shots :
                        defended_shots.remove(s)
                        if defended_shots == [] :
                            #print("Deleting"+str(node_list[i].pos))
                            deleting = deleting + 1
                            node_list.pop(i)
                            i = i - 1
                            break
            if defended_shots == [] :
                break
    return deleting






























class Graph:
    def __init__(self, board, solution_name):#, tirs cadrés, ):
        self.board = board
        self.checkArguments()
        self.dist = 0.0
        self.alreadyOneGoalKeeper = False
        self.computeDist()
        self.starting_pos = []
        self.nb_def = 8
        self.nbDefenders()
        self.shot_on_target_nodes = []
        self.opponents_and_shots = {}
        self.onTargetShots()
        self.defender_position_nodes = []
        self.everyGridPosition()
        self.bf_worked = False
        if opt_bf :
            self.defender_position_nodes_bruteforce = self.defender_position_nodes.copy()
        self.computeDefending()
        self.sortByDefendingShots()
        self.defender_position_nodes_close_to_opponent = self.defender_position_nodes[:]
        self.sol_name = solution_name
        ###self.defending_edges = []
        #self.computeDefending()
        #self.deleteUnnecessaryDefenders()
        #print(self.isSolution()) #faire qqch de cette info
        #self.WriteSolution()

    def checkArguments(self):
        #print("CHECKING ARGUMENTS")
        if self.board.problem.pos_step == 0 :
            print("\"pos_step\" must be greater than 0. Resuming calculus with \"pos_step\" equal to 0.1, instead of 0")
            self.board.problem.pos_step = 0.1
        elif self.board.problem.pos_step < 0 :
            print("\"pos_step\" must be greater than 0. Resuming calculus with \"pos_step\" equal to "+str(abs(self.board.problem.pos_step))+", instead of "+str(self.board.problem.pos_step))
            self.board.problem.pos_step = abs(self.board.problem.pos_step)
        if self.board.problem.theta_step == 0 :
            print("\"theta_step\" must be greater than 0. Resuming calculus with \"theta_step\" equal to 0.031416, instead of 0")
            self.board.problem.theta_step = 0.031416
        elif self.board.problem.theta_step < 0 :
            print("\"theta_step\" must be greater than 0. Resuming calculus with \"theta_step\" equal to "+str(abs(self.board.problem.theta_step))+", instead of "+str(self.board.problem.theta_step))
            self.board.problem.theta_step = abs(self.board.problem.theta_step)
        if self.board.problem.robot_radius == 0 :
            print("If \"robot_radius\" is set as 0, no shot can be defended.")
        elif self.board.problem.theta_step < 0 :
            print("\"robot_radius\" must be greater than 0. Resuming calculus with \"robot_radius\" equal to "+str(abs(self.board.problem.robot_radius))+", instead of "+str(self.board.problem.robot_radius))
            self.board.problem.robot_radius = abs(self.board.problem.robot_radius)
        if (self.board.problem.min_dist is not None) and (self.board.problem.min_dist < 0) :
            print("\"min_dist\" is not supposed to be lower than 0. You can erase the line containing \"min_dist\" if it is not necessary. Resuming calculus with \"robot_radius\" equal to "+str(abs(self.board.problem.min_dist))+", instead of "+str(self.board.problem.min_dist))
            self.board.problem.min_dist = abs(self.board.problem.min_dist)
       

    def isInsideSquare(self, square, pos) :
        if square is None :
            return False
        if isBetween(square[0][0], square[0][1], pos[0]) and isBetween(square[1][0], square[1][1], pos[1]) :
            return True
        p_hg = numpy.array([square[0][0], square[1][0]])
        p_hd = numpy.array([square[0][1], square[1][0]])
        p_bg = numpy.array([square[0][0], square[1][1]])
        p_bd = numpy.array([square[0][1], square[1][1]])
        if (segmentCircleIntersection(p_hg, p_hd, pos, self.board.problem.robot_radius) is not None) or (segmentCircleIntersection(p_hg, p_bg, pos, self.board.problem.robot_radius) is not None) or (segmentCircleIntersection(p_bd, p_bg, pos, self.board.problem.robot_radius) is not None) or (segmentCircleIntersection(p_bd, p_hd, pos, self.board.problem.robot_radius) is not None) : # prend en compte la hitbox du robot, demander si besoin de faire ça
            return True
        return False

    def canBePlaced(self,pos) :
        #print("can be placed?")
        #print(str(pos))
        if opt_ga == False :
            return True
        if self.isInsideSquare(self.board.problem.goalkeeper_area, pos) :
            #print("inside square")
            if self.alreadyOneGoalKeeper :
                #print("but already keeper")
                return False
        #print("can be placed!")
        return True

    def newGoalKeeper(self,pos) :
        #print("new gp?")
        #print(str(pos))
        if self.isInsideSquare(self.board.problem.goalkeeper_area, pos)  :
            #print("yes")
            self.alreadyOneGoalKeeper = True

    def nbDefenders(self):
        #print(opt_d)
        #print(self.board.problem.defenders)
        if (self.board.problem.defenders is not None) and (opt_d) :
            #print(self.board.problem.defenders.any())
            if self.board.problem.defenders.any() :
                #print(self.board.problem.defenders[0])
                if self.board.problem.defenders[0].any() :
                    self.nb_def = len(self.board.problem.defenders[0])
                    #print(self.nb_def)
                    for index in range(self.nb_def) :
                        self.starting_pos.append(Defender([self.board.problem.defenders[0][index],self.board.problem.defenders[1][index]]))
                    #print(len(self.starting_pos))
                else :
                    self.nb_def = 0
                    #print("Either 0 defenders are allowed, or bad read")

    def onTargetShots(self):
        #screen = pygame.display.set_mode(board.size) #numpy.array([1280, 960])
        # for opp_id in range(self.board.problem.getNbOpponents()) :
        #     nb_shots = 0
        #     kick_dir = 0
        #     opp_pos = self.board.problem.getOpponent(opp_id)
        #     while kick_dir < 2 * math.pi:
        #         for goal in self.board.problem.goals:
        #             goal_pos = goal.kickResult(opp_pos, kick_dir)
        #             if not goal_pos is None :
        #                 nb_shots = nb_shots + 1
        #                 s = OpponentShot(opp_pos, kick_dir)
        #                 self.shot_on_target_nodes.append(s)
        #             kick_dir += self.board.problem.theta_step
        #     self.opponents_and_shots[str(opp_pos)] = nb_shots

        mock_defender = numpy.array([[self.board.problem.field_limits[0, 0], self.board.problem.field_limits[1, 0]]]).transpose()
        #print(mock_defender)
        for opp_id in range(self.board.problem.getNbOpponents()):
            nb_shots = 0
            kick_dir = 0
            opp_pos = self.board.problem.getOpponent(opp_id)
            while kick_dir < 2 * math.pi:
                s = self.board.problem.computeShotResult(self.board.problem.getOpponent(opp_id), kick_dir,
                                           mock_defender)
                if s.result != ShotResult.OUT :
                    nb_shots = nb_shots + 1
                    shot_to_add = OpponentShot(opp_pos, kick_dir)
                    self.shot_on_target_nodes.append(shot_to_add)
                kick_dir += self.board.problem.theta_step
            self.opponents_and_shots[str(opp_pos)] = nb_shots
        #print(len(self.shot_on_target_nodes))

    def isTooCloseToADefender(self, nb_defs, def_list) :
        if self.dist == 0.0 :
            return False
        x = def_list[nb_defs].pos[0]
        y = def_list[nb_defs].pos[1]
        for nb_def in range(nb_defs) :
            def_pos = def_list[nb_def].pos
            if calculateDistance(x,y,def_pos[0],def_pos[1]) < self.dist :
                return True
        return False

    def isTooCloseToAnOpponent(self, x, y) :
        if self.dist == 0.0 :
            return False
        for opponent in range(self.board.problem.getNbOpponents()) :
            opp_pos = self.board.problem.getOpponent(opponent)
            if calculateDistance(x,y,opp_pos[0],opp_pos[1]) < self.dist :
                return True
        return False
            
    def computeDist(self):
        if self.board.problem.robot_radius :
            self.dist = self.board.problem.robot_radius * 2
            if self.board.problem.min_dist and opt_mi :
                if self.board.problem.min_dist > self.dist :
                    self.dist = self.board.problem.min_dist + self.board.problem.robot_radius
                    #self.dist = self.board.problem.min_dist / 2 + self.board.problem.robot_radius
        elif self.board.problem.min_dist and opt_mi :
            self.dist = self.board.problem.min_dist + self.board.problem.robot_radius
            # self.dist = self.board.problem.min_dist / 2 + self.board.problem.robot_radius

    def everyGridPosition(self): # faire fonction plus économique dans laquelle on ne vérifie que les points de la grille dans le range du tir
        self.defender_position_nodes.clear()
        ps = self.board.problem.pos_step
        #while ps < dist :
        #    ps = ps + self.board.problem.pos_step # afin de faire un grille G' où l'on est sûr d'être assez espacé, peut-être à enlever pour vérifier à chaque fois qu'on place un défenseur qu'il n'en touche pas un autre
        #rr = self.board.problem.robot_radius
        width_start = computeStart(self.board.problem.field_limits[0, 0], ps)
        height_start = computeStart(self.board.problem.field_limits[1, 0], ps)
        for x in numpy.arange(width_start, self.board.problem.field_limits[0, 1]+ps, ps) :
            for y in numpy.arange(height_start, self.board.problem.field_limits[1, 1]+ps, ps) :
                if self.isTooCloseToAnOpponent(x, y) == False :
                    d = Defender([x,y])
                    self.defender_position_nodes.append(d)

    def isDefending(self, defender, shot):
        #print("shot.pos")
        #print(shot.pos)
        defender_arr = np.array([[defender.pos[0]], [defender.pos[1]]])
        kick_result = self.board.problem.computeShotResult(shot.pos, shot.angle, defender_arr)
        if kick_result.result == ShotResult.INTERCEPTED :
            return True
        return False
        #if segmentCircleIntersection(shot.pos, shot.intersection_with_goal, defender.pos, self.board.problem.robot_radius) is not None :
        #    return True
        #return False

    def computeDefending(self):
        for shot in self.shot_on_target_nodes :
            for defender in self.defender_position_nodes :
                if self.isDefending(defender, shot) :
                    defender.append_shot(shot)
                    #shot.append_defender(defender)
                    #defending_edges.append(Defense(defender, shot))

    """def verifySort(self):
        #print("Verify sort :")
        for defender in self.defender_position_nodes :
            #if len(defender.defending_shots) == 0 :
            #    sys.exit()
            print(str(defender.pos))
            #print(len(defender.defending_shots))
            #print(str(self.closestOpponentDistance(defender)))
            #if len(defender.defending_shots) == 11 :
            #    print(defender.pos)
        #for i in self.defender_position_nodes :
        #    if len(i.defending_shots) != 0 :
        #        print(str(len(i.defending_shots)))
        #    else : sys.exit()"""

    def closestOpponentDistance(self, defender):
        opp_pos = self.board.problem.getOpponent(0)
        dist = calculateDistance(opp_pos[0], opp_pos[1], defender.pos[0], defender.pos[1])
        for opp_id in range(1,self.board.problem.getNbOpponents()) :
            opp_pos = self.board.problem.getOpponent(opp_id)
            new_dist = calculateDistance(opp_pos[0], opp_pos[1], defender.pos[0], defender.pos[1])
            if new_dist < dist :
                dist = new_dist
        return dist


    def sortByDefendingShots(self):
        #print("test 1\n")
        #self.quickSort(self.defender_position_nodes, 0, len(self.defender_position_nodes)-1)
        self.defender_position_nodes.sort(key=lambda defender: self.closestOpponentDistance(defender))
        self.defender_position_nodes.sort(key=lambda defender: len(defender.defending_shots), reverse=True)
        #self.defender_position_nodes = self.defender_position_nodes[1:]
        #print(str(self.defender_position_nodes[0].pos))
        #print(str(self.closestOpponentDistance(self.defender_position_nodes[0])))
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
    
    def notDefendedList(self, defender_nb, all, node_list) :
        shots = None
        if all :
            shots = self.shot_on_target_nodes[:]
        else :
            shots = node_list[defender_nb].defending_shots[:]
        for index in range(defender_nb) :
            #print(node_list[index].pos)
            if shots is None :
                break
            #print(node_list)
            #print(index)
            #print(node_list[index])
            for shot in node_list[index].defending_shots :
                if shot in shots :
                    #print(shot.pos)
                    shots.remove(shot)
            #index = index + 1
        #print("all = "+str(all))
        #print(shots)
        return shots

    def notDefended(self, defender_nb, all) :
        return self.notDefendedList(defender_nb, all, self.defender_position_nodes)

    def keepMostDefending(self) :
        defender_nb = 0
        while (defender_nb < len(self.defender_position_nodes)) and (defender_nb < self.nb_def) :
            cond = self.notDefended(defender_nb, True) == []
            cond2 = cutList(self.defender_position_nodes, defender_nb, cond)
            #print(cond)
            if cond2 :
                #print("cond2 est True")
                break
            defender = self.defender_position_nodes[defender_nb]
            if (self.notDefended(defender_nb, False) is None) or (any(self.notDefended(defender_nb, False)) == False) or (self.isTooCloseToAnOpponent(defender.pos[0], defender.pos[1])) or (self.isTooCloseToADefender(defender_nb, self.defender_position_nodes)) or (not self.canBePlaced(defender.pos)) :
                #for shot in defender.defending_shots : # à vérifier mais je crois que je n'en ai plus besoin
                #    shot.defenders.remove(defender)
                self.defender_position_nodes.remove(defender)
            else :
                self.newGoalKeeper(defender.pos)
                defender_nb = defender_nb + 1
                #print(defender.pos)
                defender_nb = defender_nb - deleteUselessDefenders(self.defender_position_nodes, defender_nb)
    
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
        self.alreadyOneGoalKeeper = False
        index = 0
        while (index < len(self.defender_position_nodes_close_to_opponent)) and (index < self.nb_def) :
            #print(self.defender_position_nodes_close_to_opponent[index].pos)
            #print(self.opponents_and_shots)
            if (self.opponents_and_shots is None) or (cutList(self.defender_position_nodes_close_to_opponent, index, not self.opponents_and_shots)) :
                break
            defender = self.defender_position_nodes_close_to_opponent[index]
            if (self.isTooCloseToAnOpponent(defender.pos[0], defender.pos[1]) == False) and (self.isTooCloseToADefender(index, self.defender_position_nodes_close_to_opponent) == False) and (self.canBePlaced(defender.pos)) :
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
                    self.newGoalKeeper(defender.pos)
                    index = index + 1
                    index = index - deleteUselessDefenders(self.defender_position_nodes_close_to_opponent, index)
            else :
                #del defender
                self.defender_position_nodes_close_to_opponent.pop(index)







    def bruteForce(self):
        self.defender_position_nodes_bruteforce
        start = 1
        end = len(self.defender_position_nodes_bruteforce)
        if opt_d :
            start = self.nb_def
            end = start
            total_dist = None
        for nb in range(start, end+1) :
            if opt_d :
                all_permutations = itertools.combinations(self.defender_position_nodes_bruteforce, nb)
            else :
                all_permutations = itertools.permutations(self.defender_position_nodes_bruteforce, nb)
            for permutation in all_permutations :
                for defender in permutation :
                    if not self.canBePlaced(defender.pos) :
                        break
                    self.newGoalKeeper(defender.pos)
                if self.notDefendedList(len(permutation), True, permutation) == [] :
                    if opt_d :
                        this_dist = totalDistance(self.starting_pos, permutation)
                        if total_dist == None :
                            total_dist = this_dist
                            self.defender_position_nodes_bruteforce = permutation[:]
                        else :
                            if this_dist < total_dist :
                                total_dist = this_dist
                                self.defender_position_nodes_bruteforce = permutation[:]
                    else :
                        self.defender_position_nodes_bruteforce = permutation[:]
                        return True
        if opt_d and (total_dist != None) :
            return True
        return False
        










    def resetShotsDefenders(self):
        for s in self.shot_on_target_nodes :
            s.defenders = []
    
    def retryWithoutExtensions(self):
        #print(self.areAllShotsDefended())
        #print(self.opponents_and_shots)
        #print("retrying?")
        if opt_re and (not self.solutionOneWorked()) and (not self.solutionTwoWorked()) and (not self.bf_worked) :
            #print("Retrying without extensions")
            #print(len(self.defender_position_nodes_close_to_opponent))
            #print(len(self.defender_position_nodes))
            opt_ga = False
            opt_d = False
            opt_ms = False
            opt_mi = False
            #opt_re = False
            self.dist = 0.0
            self.computeDist()
            self.starting_pos = []
            self.resetShotsDefenders()
            self.everyGridPosition()
            self.computeDefending()
            self.sortByDefendingShots()
            self.defender_position_nodes_close_to_opponent = self.defender_position_nodes.copy()
            self.defender_position_nodes_bruteforce = self.defender_position_nodes.copy()
            if opt_kd :
                self.keepMostDefending()
            if opt_co :
                self.closeToOpponent()
            if opt_bf :
                self.bruteForce()
            #print(str(len(self.defender_position_nodes)))
            #print(str(len(self.defender_position_nodes_close_to_opponent)))
        
    def orderingTwoMethods(self):
        #print("Two")
        #listFillWithDefenders(self.defender_position_nodes, len(self.starting_pos), self.starting_pos)
        if opt_d :
            self.defender_position_nodes = self.defender_position_nodes[:self.nb_def]
            self.defender_position_nodes_close_to_opponent = self.defender_position_nodes_close_to_opponent[:self.nb_def]
            listFillWithMinusOnes(self.defender_position_nodes, len(self.starting_pos))
            total_distance = totalDistance(self.starting_pos, self.defender_position_nodes)
            total_distance = orderedByDistance(self.defender_position_nodes, self.starting_pos, total_distance, self.defender_position_nodes[:])
            #listFillWithDefenders(self.defender_position_nodes_close_to_opponent, len(self.starting_pos), self.starting_pos)
            #print("ORDERING METHOD 2")
            orderedByDistance(self.defender_position_nodes, self.starting_pos, total_distance, self.defender_position_nodes_close_to_opponent)

    def orderingOneMethod(self):
        #print("One")
        #listFillWithDefenders(self.defender_position_nodes, len(self.starting_pos), self.starting_pos)
        if opt_d :
            listFillWithMinusOnes(self.defender_position_nodes, len(self.starting_pos))
            total_distance = totalDistance(self.starting_pos, self.defender_position_nodes)
            orderedByDistance(self.defender_position_nodes, self.starting_pos, total_distance, self.defender_position_nodes[:])
    
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
        #if (len(self.defender_position_nodes) == 0) : # si on n'a pas trouvé de défenseurs avec la méthode de défendre le plus de tirs possibles mais qu'on en a trouvé avec la méthode de couvrir tous les tirs d'un attaquant, alors on prend le résultat de la deuxième méthode
            #self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            #self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            #if self.starting_pos != [] :
            #    self.orderingOneMethod()
        if self.bf_worked :
            self.defender_position_nodes = self.defender_position_nodes_bruteforce
            return
        #print(self.solutionOneWorked())
        #print(self.solutionTwoWorked())
        sol_one = self.solutionOneWorked()
        sol_two = self.solutionTwoWorked()
        if((sol_one and sol_two) or ((not sol_one) and (not sol_two))) : # si on a trouvé une solution avec les deux méthodes, ou qu'on n'a trouvé aucune solution avec les deux méthodes, alors on prend la solution qui demande le moins de défenseurs si pas de start pos sinon celle qui demande le moins de déplacement
            if self.starting_pos == [] :
                if (len(self.defender_position_nodes_close_to_opponent) < len(self.defender_position_nodes)) and (len(self.defender_position_nodes_close_to_opponent) > 0) :
                    self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            else :
                self.orderingTwoMethods()
            #if (len(self.defender_position_nodes_close_to_opponent) < len(self.defender_position_nodes)) :
            #    self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
                #print("choice 2")
        elif ((not sol_one) and (sol_two)) : # si la méthode 1 ne défend pas tous les tirs alors que la méthode 2 si, alors on garde la méthode 2
            #self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            if self.starting_pos != [] :
                self.orderingOneMethod()
        else :
            if self.starting_pos != [] :
                self.orderingOneMethod()
            #print("choice 2")
        # dans tous les autres cas, on garde la méthode 1 (donc pas besoin de remplacer le résultat 1 par le 2)
        #print(len(self.defender_position_nodes))
        #print(len(self.defender_position_nodes_close_to_opponent))

    """def areAllShotsDefended(self):
        #print(str(len(self.shot_on_target_nodes)))
        for shot in self.shot_on_target_nodes :
            #print(str(len(shot.defenders)))
            if not shot.defenders :
                print("shot at"+str(shot.pos)+" is not defended") # en faire qqch
                return False
        return True"""
        
    def solutionOneWorked(self):
        if (len(self.defender_position_nodes) <= 0) :
            #print("len(self.defender_position_nodes) <= 0")
            return False
        #print(self.starting_pos)
        #print(len(self.defender_position_nodes))
        if (opt_d) and (self.starting_pos != []) and (len(self.defender_position_nodes) > len(self.starting_pos)) :
            #print("(self.starting_pos != []) and (len(self.defender_position_nodes) > len(self.starting_pos))")
            return False
        #return (self.notDefended(len(self.defender_position_nodes), True) is not None)
        return (self.notDefended(len(self.defender_position_nodes), True) == [])

    def solutionTwoWorked(self):
        if not opt_co :
            return False
        if (len(self.defender_position_nodes_close_to_opponent) <= 0) :
            return False
        if (opt_d) and (self.starting_pos != []) and (len(self.defender_position_nodes_close_to_opponent) > len(self.starting_pos)) :
            return False
        return (not self.opponents_and_shots)

    def isSolution(self):
        if len(self.defender_position_nodes) == 0 :
            print("No defender found")
        if not self.solutionOneWorked() :
            return False 
        #if len(self.defender_position_nodes) > self.board.problem.getNbOpponents():
        #print(str(len(self.defender_position_nodes))+" > "+str(self.nb_def))
        if len(self.defender_position_nodes) > self.nb_def :
            print("Too many defenders")
            return False
        return True

    def writeSolution(self):
        #print("./configs/"+self.sol_name)
        f = open("./configs/"+self.sol_name, "w")
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

class OpponentShot:
    def __init__(self, pos, angle):#, goal_pos):#, defenders):
        self.pos = pos
        self.angle = angle
        self.defenders = []
        #self.intersection_with_goal = goal_pos
    
    def append_defender(self, defender):
        self.defenders.append(defender)

#class Defense:
#    def __init__(self, defender, shot):
#        self.defender = defender
#        self.shot = shot




































#if (len(sys.argv) < 3):
#    sys.exit("Usage: " + sys.argv[0] + " <problem.json> <solution.json>")

#if (len(sys.argv) != 2):
#    sys.exit("Usage: " + sys.argv[0] + " <problem.json>")

how_to = "Par défaut, le programme lance avec toutes les extensions possibles l'algo \"KeepMostDefending\" puis \"CloseToOpponent\" et compare le résultat des deux pour sélectionner la solution la plus optimale (demandant le moins de distance si extention défenseurs initiaux, ou demandant le moins de défenseurs sinon), si aucune solution n'est trouvée en prenant en compte les extensions, le programme est lancé à nouveau sans les extensions.\nSi vous voulez choisir uniquement certaines options vous pouvez les préciser.\n-kd : lance l'algo \"KeepMostDefending\"\n-co : lance l'algo \"CloseToOpponent\"\n-bf : lance l'algo \"Bruteforce\"\n-re : Recommence sans les extensions dans le cas où aucune solution n'est trouvée avec\n-ga : prend on compte l'extension \"GoalkeeperArea\"\n-d : prend on compte l'extension \"InitialDefenders\"\n-ms : prend on compte l'extension \"MaximalSpeed\"\n-mi : prend on compte l'extension \"MinDist\"\nIl n'y a pas d'option pour activer l'option \"MultiGoal\" car elle sera toujours active.\n-na : sans -na le nom de la solution sera sol_to_<problem>.json, avec il prendra la nom écrit juste après.\n\nPar exemple si vous voulez donner un nom au fichier de solution et garder le fait d'utiliser les deux algorithmes sur toutes les extensions et recommencer si besoin, vous pouvez écrire\n\tpython3 ./buildGraph.py ./configs/every_extension_problem.json -na ma_solution -kd -co -re -ga -d -ms -mi"

if len(sys.argv) < 2 :
    print("Pensez à ajouter un fichier de problème .json en entrée")
    sys.exit()

if sys.argv[-1] == "-h" :
    print(how_to)
    sys.exit()

solution_name = "sol_to_"+sys.argv[1].split("/")[-1]

if (len(sys.argv) != 2):
    opt_ga = False
    opt_d = False
    opt_ms = False
    opt_mi = False
    opt_kd = False
    opt_co = False
    opt_re = False

    #solution_name = "computed_solution.json"

    for opt in range(len(sys.argv)):
        if sys.argv[opt] == "-h" :
            print(how_to)
        if sys.argv[opt] == "-ga" :
            opt_ga = True
        elif sys.argv[opt] == "-d" :
            opt_d = True
        elif sys.argv[opt] == "-ms" :
            opt_ms = True
        elif sys.argv[opt] == "-mi" :
            opt_mi = True
        elif sys.argv[opt] == "-kd" :
            opt_kd = True
        elif sys.argv[opt] == "-co" :
            opt_co = True
        elif sys.argv[opt] == "-bf" :
            opt_bf = True
        elif sys.argv[opt] == "-re" :
            opt_re = True
        elif (sys.argv[opt] == "-na") and (opt < len(sys.argv)) and (sys.argv[opt+1][0] != '-') :
            solution_name = sys.argv[opt+1]+".json"

    if (not opt_kd) and (not opt_co) and (not opt_bf) :
        raise ValueError("Si vous donnez des arguments, il faut préciser les algorithmes que vous voulez utiliser, -kd, -co et/ou -bf")
        sys.exit()


problem_path = sys.argv[1]
#mettre un solution_name

def checkData(data):
    if data["opponents"] == [] :
        raise ValueError("No \"opponents\" found.")
        sys.exit()
    if data["theta_step"] <= 0 :
        raise ValueError("\"theta_step\" must be greater than 0. Try with a different value, 0.031416 for example.")
        sys.exit()
    if data.get("ball_max_speed") is not None and data.get("ball_max_speed") <= 0 :
        raise ValueError("\"ball_max_speed\" must be greater than 0. Try with a different value, 8.0 for example; or remove the line containing \"ball_max_speed\".")
        sys.exit()
    if data.get("robot_max_speed") is not None and data.get("robot_max_speed") <= 0 :
        raise ValueError("\"robot_max_speed\" must be greater than 0. Try with a different value, 8.0 for example; or remove the line containing \"robot_max_speed\".")
        sys.exit()


with open(problem_path) as problem_file:
    data = json.load(problem_file)
    checkData(data)
    problem = Problem(data)
    if not opt_ms :
        problem.ball_max_speed = None
        problem.robot_max_speed = None
solution_path = "./configs/no_defenders.json"
if problem.defenders is not None :
    solution_path = problem_path
with open(solution_path) as solution_file:
    solution = Solution(json.load(solution_file))

graph = Graph(Board(problem, solution),solution_name)

#graph.deleteUnnecessaryDefenders()

if opt_kd :
    graph.keepMostDefending()

#print(str(len(graph.defender_position_nodes)))
#print("METHODE 2 COMMENCE ICI !!!")

if opt_co :
    graph.closeToOpponent()

#print(str(len(graph.defender_position_nodes_close_to_opponent)))

if opt_bf :
    graph.bf_worked = graph.bruteForce()

#print(len(graph.defender_position_nodes_close_to_opponent))

graph.chooseAnswer()

#print(graph.solutionOneWorked())

changeMinusOnesToDefenders(graph.starting_pos, graph.defender_position_nodes)

#print(graph.solutionOneWorked())

print(">"+str(graph.isSolution())) #faire qqch de cette info

#graph.verifySort()

graph.writeSolution()

#graph.verifySort()

sys.exit()








# *Note concernant l'algorithme :
# Pour l'instant on essaye deux méthodes en y appliquant des contraintes (extensions), si aucune ne donne de bon résultat on retente sans contrainte, à la fin on renvoit le meilleur résultat trouvé
# Il est possible que dans le futur en changeant nos algorithmes on n'ait plus besoin de réessayer sans contrainte mais je pense qu'on devrait les laisser dans le doute et le préciser dans le rapport et la présentation
# -Méthode 1 (keepMostDefending) : On garde parmi toutes les positions défendues, celles qui défendent le plus de tirs (s'il y a au moins un tir qui n'est pas déjà défendu par une autre position que l'on a décidé de garder)
# -Méthode 2 (closeToOpponent) : On parcourt les positions défendues pour essayer de trouver des positions qui défendent tous les tirs d'un attaquant (se placer proche d'un attaquant permet souvent de couvrir beaucoup de tirs avec peu de défenseurs)
# -Eventuelle méthode 3 (closeToGoal) : Parcourir les positions défendues pour essayer de trouver des positions qui défendent tous les tirs menant à une cage de but (mais je pense que finalement, cela ferait un peu doublon avec la méthode 1, et lorsqu'on devra implémenter la zone de gardien de but elle ne servira plus trop)

# *Améliorations possibles concernant les algorithmes utilisés :
# -Avant les méthodes : pour l'instant nous générons toutes les positions de la grille possibles, il faudrait ne générer que celles qui se trouvent sur les trajectoires de tirs (parcourir la trajectoire puis faire un if x % qqch = sur la grille, en utilisant pos_step ou ps par exemple)
# -Pendant (vers la fin) les méthodes : pour l'instant nous prenons les premiers défenseurs qui nous parraissent pertinent selon les critères de l'algorithmes, mais nous ne revenons pas en arrière pour les échanger avec d'autres défenseurs si la méthode n'a pas fonctionné (par exemple en prenant les deux première positions alors il n'y a plus de position sans collision permettant de couvrir un tir, alors enlever le premier défenseur pris et en ajouter deux autres à des positions ne causant pas de collisions) (problème : compléxité à coder, mais surtout explosion en temps de l'algorithme et peut-être en mémoire selon comment c'est codé)
# -Dès le début du programme : éventuellement pouvoir prendre des -options afin de préciser si on veut utiliser toutes les extensions, aucunes ou certaines
# -Attention, j'ai considéré qu'un résultat qui demandait plus de défenseurs que précisés dans le fichier de problem.json s'ils sont précisés, ou plus de 8 sinon (nombre dans Small-Size League division A), était un résultat invalide, on pourra en discuter si vous voulez, par exemple pour ajouter un paramètre permettant de passer en division B avec seulement 6 défenseurs (ou d'entrer le nombre de défenseurs voulus)

# *Extensions réalisées :
# -Distance minimale entre les robots : gérée avec isTooCloseToADefender() et isTooCloseToAnOpponent(), que j'ai préféré utiliser plutôt que d'aggrandir les mailles de la grille parce que je trouvais que ça enlevait beaucoup trop de possibilités de placement des défenseurs, mais cela réduirait le nombre de positions à vérifier (pour l'instant gain de précision plutôt que de temps)
# -Position initiale des joueurs : c'est bon, attention à partir de 10 défenseurs l'algo devient vraiment long
# -Gardien : c'est fait, on considère toute sa hitbox, si le milieu suffit alors on peut commenter un morceau de isInsideSquare et c'est bon
# -Plusieurs buts : elle s'est réglée d'elle-même avec l'algortihme implanté, éventuellement faire attention si on modifie l'implémentation (par exemple avec l'extention zone du gardien)

# *Extentions à réaliser :
# -Trajectoires courbées : il faudra coder ça dans les fichiers donnés ? si c'est le cas, peut-être qu'une fois que ce sera fait, notre algortihme fonctionnera déjà pour les trajectoires courbes sans avoir à le modifier, à voir

# *Tests : pour l'instant j'ai juste lancé les fichiers d'exemple et vérifié que ça fonctionnait pour eux, mais on devrait automatiser les tests









# *Questions à poser au professeur :
# -Concernant l'extension du gardien de but :
# --Peut-il y avoir plusieurs zones de gardiens de but (par exemple avec l'entension de plusieurs cages de but),
# --si oui, est-ce que chaque zone a un gardien ou est-ce qu'il n'y a qu'un seul gardien par équipe.
# --Le gardien peut-il sortir de sa zone de gardien ?
# --Est-ce qu'avec l'extension de la position initiale des joueurs, est-ce qu'il faut juste que dans le fichier de solution on n'ait qu'un seul défenseur maximum dans la zone de gardien, ou est-ce qu'on doit faire attention à ce qu'aucun non-gardien n'entre dans la zone lors de son déplacement et qu'il n'y a pas un défenseur qui devient gardien et gardien qui devient défenseur
# -Concernant l'implémentation de la méthode gloutonne, est-ce qu'on doit parcourir toutes les possibilités de placement de défenseurs jusqu'à en trouver une qui répond à tous les critères (arrêter tous les buts + entensions) ?