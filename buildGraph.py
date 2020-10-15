#import goal.py
#import board.py

class Graph:
    def __init__(self):#, tirs cadrés, ):
        shot_on_target_nodes = []
        onTargetShots()
        defender_position_nodes = []
        everyGridPosition()
        defending_edges = []
        computeDefending()




    def onTargetShots():
        screen = pygame.display.set_mode(board.size) #numpy.array([1280, 960])
        for opp_id in range(board.problem.getNbOpponents()):
            kick_dir = 0
            opp_pos = board.problem.getOpponent(opp_id)
            while kick_dir < 2 * math.pi:
                if goal.kickResult(opp_pos, kick_dir) is not None :
                    s = Shot(opp_pos, kick_dir)
                    shot_on_target_nodes.append(s)
                kick_dir += board.problem.theta_step


    def everyGridPosition():
        x = 0
        y = 0
        ps = board.problem.pos_step
        w = board.problem.getFieldWidth
        h = board.problem.getFieldHeight
        for x in range(0-w, w+ps, ps):
            for y in range(0-h, h+ps, ps):
                d = Defender([x,y])
                defender_position_nodes.append(d)

    def computeDefending():
        # calculer pour chaque tir cadré, pour chaque défenseur, si le défenseur intercepte  le tir
        # defender.append_shot(shot)
        # shot.append_defender(defender)
        # defending_edges.append(Defense(defender, shot))
        

#class Point:
#    def __init__(self,x,y):
#        self.x = x
#        self.y = y

class Defender:
    def __init__(self, pos):#, defending_shots):
        self.pois = pos
        defending_shots = []

    def append_shot(shot):
        defending_shots.append(shot)

class Shot:
    def __init__(self, pos, angle):#, defenders):
        self.pos = pos
        self.angle = angle
        defenders = []
    
    def append_defender(defender):
        defending_shots.append(defender)

class Defense:
    def __init__(self, defender, shot):
        self.defender = defender
        self.shot = shot