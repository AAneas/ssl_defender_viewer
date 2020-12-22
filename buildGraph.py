# pour lancer le programme : python3 ./buildGraph.py ./configs/basic_problem_1.json
# puis regarder computed_solution.json
# finalement vérifier avec : python3 ./main.py ./configs/basic_problem_1.json ./configs/computed_solution.json


import goal
from geometry import segmentCircleIntersection
import itertools
import math
import sys
import json
from board import *

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
    if (cond) or (len(node_list[index].defending_shots) == 0) :
        node_list[:] = node_list[:index]
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
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:n])
                break
        else:
            return

def listFillWithMinusOnes(final_list, length) :
    for i in range(length-len(final_list)) :
        final_list.append(-1)

def changeMinusOnesToDefenders(start, end):
    for index in range(len(end)) :
        if end[index] == -1 :
            end[index] = start[index]
    
def totalDistance(start, end):
    total = 0
    for defender_nb in range(len(end)) : #il faut qu'il n'y ait pas plus dans end que dans start
        if end[defender_nb] != -1 :
            total = total + calculateDistance(start[defender_nb].pos[0], start[defender_nb].pos[1], end[defender_nb].pos[0], end[defender_nb].pos[1])
    return total

def orderedByDistance(final_list, starting_pos, total_distance, current_list):
    listFillWithMinusOnes(current_list, len(starting_pos))
    perms = permutations(current_list)
    prev_perm = []
    for trying_current in perms :
        if trying_current != prev_perm :
            prev_perm = trying_current[:]
            new_dist = totalDistance(starting_pos, trying_current)
            if new_dist < total_distance :
                total_distance = new_dist
                final_list[:] = trying_current[:]
    return total_distance

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
                            deleting = deleting + 1
                            node_list.pop(i)
                            i = i - 1
                            break
            if defended_shots == [] :
                break
    return deleting






























class Graph:
    def __init__(self, board, solution_name):
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

    def checkArguments(self):
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
        if (segmentCircleIntersection(p_hg, p_hd, pos, self.board.problem.robot_radius) is not None) or (segmentCircleIntersection(p_hg, p_bg, pos, self.board.problem.robot_radius) is not None) or (segmentCircleIntersection(p_bd, p_bg, pos, self.board.problem.robot_radius) is not None) or (segmentCircleIntersection(p_bd, p_hd, pos, self.board.problem.robot_radius) is not None) :
            return True
        return False

    def canBePlaced(self,pos) :
        if opt_ga == False :
            return True
        if self.isInsideSquare(self.board.problem.goalkeeper_area, pos) :
            if self.alreadyOneGoalKeeper :
                return False
        return True

    def newGoalKeeper(self,pos) :
        if self.isInsideSquare(self.board.problem.goalkeeper_area, pos)  :
            self.alreadyOneGoalKeeper = True

    def nbDefenders(self):
        if (self.board.problem.defenders is not None) and (opt_d) :
            if self.board.problem.defenders.any() :
                if self.board.problem.defenders[0].any() :
                    self.nb_def = len(self.board.problem.defenders[0])
                    for index in range(self.nb_def) :
                        self.starting_pos.append(Defender([self.board.problem.defenders[0][index],self.board.problem.defenders[1][index]]))
                else :
                    self.nb_def = 0

    def onTargetShots(self):
        mock_defender = numpy.array([[self.board.problem.field_limits[0, 0], self.board.problem.field_limits[1, 0]]]).transpose()
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
        elif self.board.problem.min_dist and opt_mi :
            self.dist = self.board.problem.min_dist + self.board.problem.robot_radius

    def everyGridPosition(self): # faire fonction plus économique dans laquelle on ne vérifie que les points de la grille dans la trajactoire du tir
        self.defender_position_nodes.clear()
        ps = self.board.problem.pos_step
        width_start = computeStart(self.board.problem.field_limits[0, 0], ps)
        height_start = computeStart(self.board.problem.field_limits[1, 0], ps)
        for x in numpy.arange(width_start, self.board.problem.field_limits[0, 1]+ps, ps) :
            for y in numpy.arange(height_start, self.board.problem.field_limits[1, 1]+ps, ps) :
                if self.isTooCloseToAnOpponent(x, y) == False :
                    d = Defender([x,y])
                    self.defender_position_nodes.append(d)

    def isDefending(self, defender, shot):
        defender_arr = np.array([[defender.pos[0]], [defender.pos[1]]])
        kick_result = self.board.problem.computeShotResult(shot.pos, shot.angle, defender_arr)
        if kick_result.result == ShotResult.INTERCEPTED :
            return True
        return False

    def computeDefending(self):
        for shot in self.shot_on_target_nodes :
            for defender in self.defender_position_nodes :
                if self.isDefending(defender, shot) :
                    defender.append_shot(shot)

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
        self.defender_position_nodes.sort(key=lambda defender: self.closestOpponentDistance(defender))
        self.defender_position_nodes.sort(key=lambda defender: len(defender.defending_shots), reverse=True)

    def notDefendedList(self, defender_nb, all, node_list) :
        shots = None
        if all :
            shots = self.shot_on_target_nodes[:]
        else :
            shots = node_list[defender_nb].defending_shots[:]
        for index in range(defender_nb) :
            if shots is None :
                break
            for shot in node_list[index].defending_shots :
                if shot in shots :
                    shots.remove(shot)
        return shots

    def notDefended(self, defender_nb, all) :
        return self.notDefendedList(defender_nb, all, self.defender_position_nodes)

    def keepMostDefending(self) :
        defender_nb = 0
        while (defender_nb < len(self.defender_position_nodes)) and (defender_nb < self.nb_def) :
            cond = self.notDefended(defender_nb, True) == []
            cond2 = cutList(self.defender_position_nodes, defender_nb, cond)
            if cond2 :
                break
            defender = self.defender_position_nodes[defender_nb]
            if (self.notDefended(defender_nb, False) is None) or (any(self.notDefended(defender_nb, False)) == False) or (self.isTooCloseToAnOpponent(defender.pos[0], defender.pos[1])) or (self.isTooCloseToADefender(defender_nb, self.defender_position_nodes)) or (not self.canBePlaced(defender.pos)) :
                self.defender_position_nodes.remove(defender)
            else :
                self.newGoalKeeper(defender.pos)
                defender_nb = defender_nb + 1
                defender_nb = defender_nb - deleteUselessDefenders(self.defender_position_nodes, defender_nb)
    
    def closeToOpponent(self) :
        self.alreadyOneGoalKeeper = False
        index = 0
        while (index < len(self.defender_position_nodes_close_to_opponent)) and (index < self.nb_def) :
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
                            self.opponents_and_shots.pop(opponent)
                            defending = True
                if defending == False :
                    self.defender_position_nodes_close_to_opponent.pop(index)
                else :
                    self.newGoalKeeper(defender.pos)
                    index = index + 1
                    index = index - deleteUselessDefenders(self.defender_position_nodes_close_to_opponent, index)
            else :
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
        if opt_re and (not self.solutionOneWorked()) and (not self.solutionTwoWorked()) and (not self.bf_worked) :
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
        
    def orderingTwoMethods(self):
        if opt_d :
            self.defender_position_nodes = self.defender_position_nodes[:self.nb_def]
            self.defender_position_nodes_close_to_opponent = self.defender_position_nodes_close_to_opponent[:self.nb_def]
            listFillWithMinusOnes(self.defender_position_nodes, len(self.starting_pos))
            total_distance = totalDistance(self.starting_pos, self.defender_position_nodes)
            total_distance = orderedByDistance(self.defender_position_nodes, self.starting_pos, total_distance, self.defender_position_nodes[:])
            orderedByDistance(self.defender_position_nodes, self.starting_pos, total_distance, self.defender_position_nodes_close_to_opponent)

    def orderingOneMethod(self):
        if opt_d :
            listFillWithMinusOnes(self.defender_position_nodes, len(self.starting_pos))
            total_distance = totalDistance(self.starting_pos, self.defender_position_nodes)
            orderedByDistance(self.defender_position_nodes, self.starting_pos, total_distance, self.defender_position_nodes[:])
    
    def chooseAnswer(self):
        self.retryWithoutExtensions()
        if self.bf_worked :
            self.defender_position_nodes = self.defender_position_nodes_bruteforce
            return
        sol_one = self.solutionOneWorked()
        sol_two = self.solutionTwoWorked()
        if((sol_one and sol_two) or ((not sol_one) and (not sol_two))) :
            if self.starting_pos == [] :
                if (len(self.defender_position_nodes_close_to_opponent) < len(self.defender_position_nodes)) and (len(self.defender_position_nodes_close_to_opponent) > 0) :
                    self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            else :
                self.orderingTwoMethods()
        elif ((not sol_one) and (sol_two)) :
            self.defender_position_nodes = self.defender_position_nodes_close_to_opponent
            if self.starting_pos != [] :
                self.orderingOneMethod()
        else :
            if self.starting_pos != [] :
                self.orderingOneMethod()
        
    def solutionOneWorked(self):
        if (len(self.defender_position_nodes) <= 0) :
            return False
        if (opt_d) and (self.starting_pos != []) and (len(self.defender_position_nodes) > len(self.starting_pos)) :
            return False
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
        if len(self.defender_position_nodes) > self.nb_def :
            print("Too many defenders")
            return False
        return True

    def writeSolution(self):
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

class Defender:
    def __init__(self, pos):
        self.pos = pos
        self.defending_shots = []

    def append_shot(self, shot):
        self.defending_shots.append(shot)

class OpponentShot:
    def __init__(self, pos, angle):
        self.pos = pos
        self.angle = angle
        self.defenders = []
    
    def append_defender(self, defender):
        self.defenders.append(defender)




































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

if opt_kd :
    graph.keepMostDefending()

if opt_co :
    graph.closeToOpponent()

if opt_bf :
    graph.bf_worked = graph.bruteForce()

graph.chooseAnswer()

changeMinusOnesToDefenders(graph.starting_pos, graph.defender_position_nodes)

print(">"+str(graph.isSolution()))

graph.writeSolution()

sys.exit()