import goal
from geometry import segmentCircleIntersection
#import board.py
import math

class Graph:
    def __init__(self, board):#, tirs cadrés, ):
        self.board = board
        self.shot_on_target_nodes = []
        self.onTargetShots()
        self.defender_position_nodes = []
        self.everyGridPosition()
        #self.defending_edges = []
        self.computeDefending()

    def onTargetShots(self):
        #screen = pygame.display.set_mode(board.size) #numpy.array([1280, 960])
        for opp_id in range(self.board.problem.getNbOpponents()):
            kick_dir = 0
            opp_pos = self.board.problem.getOpponent(opp_id)
            while kick_dir < 2 * math.pi:
                for goal in self.board.goals:
                    goal_pos = goal.kickResult(opp_pos, kick_dir)
                    if goal_pos is not None :
                        s = Shot(opp_pos, kick_dir, goal_pos)
                        self.shot_on_target_nodes.append(s)
                    kick_dir += self.board.problem.theta_step

    def everyGridPosition(self): # faire fonction plus économique dans laquelle on ne vérifie que les points de la grille dans le range du tir
        x = 0
        y = 0
        ps = self.board.problem.pos_step
        w = self.board.problem.getFieldWidth
        h = self.board.problem.getFieldHeight
        for x in range(0-w, w+ps, ps):
            for y in range(0-h, h+ps, ps):
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

    def partition(self, arr, low, high):
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

    def sortByDefendingShots(self):
        self.quickSort(self.defender_position_nodes, 0, len(self.defender_position_nodes)-1)

    #def deleteNonDefenders():
    #    for defender in defender_position_nodes :
    #        if not defender.defending_shots:
    #            defender_position_nodes.remove(defender)

    def deleteUnnecessaryDefenders(self):
        # proposition : on commence par regarder les défenseurs qui défendent le moins de buts, pour chacun de ses buts, on regarde s'il est déjà défendu par qqn d'autre, si c'est le cas, on lui enlève cette défense, si une fois qu'on a tout regardé il n'a plus de buts défendus on l'enlève de la liste des noeuds
        for defender in self.defender_position_nodes :
            for shot in defender.defending_shots :
                if len(shot.defenders) > 1 : #il faudra vérifier qu'avec notre implémentation un shot ne peut pas contenir plusieurs fois le même defender
                    shot.defenders.remove(defender)
                    defender.defending_shots.remove(shot)
                    # si on finit par utiliser defending_edges[] alors il faudra lui remove aussi la denfese qui contient defender et shot, sauf si on ne la crée qu'après avoir supprimé les unnecessary defenders
            if len(defender.defending_shots) < 1 :
                self.defender_position_nodes.remove(defender)            

    def areAllShotsDefended(self):
        for shot in self.shot_on_target_nodes :
            if not shot.defenders :
                print("shot at"+shot.pos+" is not defended") # en faire qqch
                return False
        return True
        
    def isSolution(self):
        if not self.areAllShotsDefended():
            return False 
        if len(self.defender_position_nodes) > self.board.problem.getNbOpponents():
            return False
        return True

    def WriteSolution(self):
        f = open("computed_solution.json", "w")
        f.write("{\n\t\"defenders\" : [\n")
        f.write(self.defender_position_nodes)
        #for defender in self.defender_position_nodes :
        #    f.write(defender+",\n\t\t")
        #f.write("\t]\n}")
        f.write("\n}")
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