from random import randrange, uniform
import sys
from ast import literal_eval

field_limits = [[-4.5,4.5], [-3,3]]
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
name = None

def create_goal():
    dirs = [-1,0,1]
    dir1 = dirs[randrange(len(dirs))]
    dir2 = dirs[randrange(len(dirs))]
    g00 = randrange(20*field_limits[0][0], 20*field_limits[0][1]+1, 20*pos_step)/20
    if dir2 == 0 :
        g10 = g00
    else :
        g10 = randrange(20*field_limits[0][0], 20*field_limits[0][1]+1, 20*pos_step)/20
    g01 = randrange(20*field_limits[0][0], 20*field_limits[0][1]+1, 20*pos_step)/20
    if dir1 == 0 :
        g11 = g01
    else :
        g11 = randrange(20*field_limits[1][0], 20*field_limits[1][1]+1, 20*pos_step)/20
    return [[[g00, g01], [g10, g11]], [dir1, dir2]]

def create_point():
    return [randrange(20*field_limits[0][0], 20*field_limits[0][1]+1, 20*pos_step)/20, randrange(20*field_limits[1][0], 20*field_limits[1][1]+1, 20*pos_step)/20]

def create_point_minmax():
    p1 = randrange(20*field_limits[0][0], 20*field_limits[0][1]+1, 20*pos_step)/20
    p2 = randrange(20*field_limits[1][0], 20*field_limits[1][1]+1, 20*pos_step)/20
    return [min(p1,p2), max(p1,p2)]

for i in range(len(sys.argv)):
    if sys.argv[i] == "-h" :
        print("Crée un fichier de problème aléatoire.\nPar défaut les informations seront identiques à celles de configs/basic_problem_1.json\nAprès chaque argument, il est possible d'ajouter une valeur après afin de donner la valeur exacte à mettre dans le .json, s'il n'est pas précisé, il sera aléatoire.\n-ps : sans -ps, par défaut pos_step = 0.01, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-fl : sans -fl, par défaut field_limits = [[-4.5,4.5],[-3,3]], sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-g : sans -g, par défaut goals = [[[[4.5, -0.5], [4.5,0.5]], [-1,0]]], sinon un seul aléatoire si pas de valeur précisée, sinon cette valeur (peut avoir plusieurs goals)\n-mg : sans -mg, par défaut goals = [[[[4.5, -0.5], [4.5,0.5]], [-1,0]]], sinon un ou plusieurs aléatoires si pas de valeur précisée, sinon valeur buts aléatoires\n-o : sans -o, par défaut opponents = [[0.5, 0.0], [-2.0, -2.0], [2, 1.0]], sinon un seul aléatoire si pas de valeur précisée, sinon cette valeur (peut avoir plusieurs goals)\n-mo : sans -mo, par défaut opponents = [[0.5, 0.0], [-2.0, -2.0], [2, 1.0]], sinon un ou plusieurs aléatoires si pas de valeur précisée, sinon valeur buts aléatoires\n-rr : sans -rr, par défaut robot_radius = 0.09, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-ts : sans -ts, par défaut theta_step = 0.031416, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-ga : sans -ga, par défaut goalkeeper_area ne sera pas présent, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-d : sans -d, par défaut defenders ne sera pas présent, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-bs : sans -bs, par défaut ball_max_speed ne sera pas présent, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-rs : sans -rs, par défaut robot_max_speed ne sera pas présent, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-mi : sans -mi, par défaut min_dist ne sera pas présent, sinon aléatoire si pas de valeur précisée, sinon cette valeur\n-na : sans -na le fichier se nommera random.json, sinon valeur à mettre après\nUn exemple de commande est :\n\tpython3 ./randomProblem.py -mo 6 -na problem_with_6_opponents")
        sys.exit()
    if sys.argv[i] == "-ps" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                pos_step = sys.argv[i]
            else :
                pos_step = randrange(0, 20)/20
        else :
            pos_step = randrange(0, 20)/20
    
    elif sys.argv[i] == "-fl" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                field_limits = literal_eval(sys.argv[i])
            else :
                field_limits = [[randrange(-200, 0, 20*pos_step)/20,randrange((20*pos_step), 201, 20*pos_step)/20], [randrange(-200, 0, 20*pos_step)/20,randrange((20*pos_step), 201, 20*pos_step)/20]]
        else :
            field_limits = [[randrange(-200, 0, 20*pos_step)/20,randrange((20*pos_step), 201, 20*pos_step)/20], [randrange(-200, 0, 20*pos_step)/20,randrange((20*pos_step), 201, 20*pos_step)/20]]
    
    elif sys.argv[i] == "-g" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                goals = literal_eval(sys.argv[i])
            else :
                goals = [create_goal()]
        else :
            goals = [create_goal()]
    elif sys.argv[i] == "-mg" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                nb_goals = sys.argv[i]
            else :
                nb_goals = randrange(10)
        else :
            nb_goals = randrange(10)
        goals = [create_goal()]
        for j in range(int(nb_goals)-1) :
            goals.append(create_goal())
    
    elif sys.argv[i] == "-o" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                opponents = literal_eval(sys.argv[i])
            else :
                opponents = [create_point()]
        else :
            opponents = [create_point()]
    elif sys.argv[i] == "-mo" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                nb = sys.argv[i]
            else :
                nb = randrange(10)
        else :
            nb = randrange(10)
        opponents = [create_point()]
        for j in range(int(nb)-1) :
            opponents.append(create_point())

    elif sys.argv[i] == "-rr" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                robot_radius = sys.argv[i]
            else :
                robot_radius = randrange(0, 20)/100
        else :
            robot_radius = randrange(0, 20)/100

    elif sys.argv[i] == "-ts" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                theta_step = sys.argv[i]
            else :
                theta_step = uniform(0, 0.1)
        else :
            theta_step = uniform(0, 0.1)

    elif sys.argv[i] == "-ga" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                goalkeeper_area = literal_eval(sys.argv[i])
            else :
               goalkeeper_area = [create_point_minmax(), create_point_minmax()] 
        else :
            goalkeeper_area = [create_point_minmax(), create_point_minmax()]

    elif sys.argv[i] == "-d" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                defenders = literal_eval(sys.argv[i])
            else :
                defenders = [create_point()]
        else :
            defenders = [create_point()]
    elif sys.argv[i] == "-md" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                nb = sys.argv[i]
            else :
                nb = randrange(10)
        else :
            nb = randrange(10)
        defenders = [create_point()]
        for j in range(nb) :
            defenders.append(create_point())

    elif sys.argv[i] == "-bs" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                ball_max_speed = sys.argv[i]
            else :
                ball_max_speed = randrange(15)+1
        else :
            ball_max_speed = randrange(15)+1

    elif sys.argv[i] == "-rs" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                robot_max_speed = sys.argv[i]
            else :
                robot_max_speed = randrange(5)+1
        else :
            robot_max_speed = randrange(5)+1

    elif sys.argv[i] == "-di" :
        if (i < len(sys.argv)-1) :
            if (sys.argv[i+1][0] != '-') :
                i = i+1
                min_dist = sys.argv[i]
            else :
                min_dist = randrange(10)/10
        else :
            min_dist = randrange(10)/10

    elif sys.argv[i] == "-na" and (i < len(sys.argv)-1) :
        if (sys.argv[i+1][0] != '-') :
            i = i+1
            name = sys.argv[i]


for i in goals :
    for j in i[0] :
        if j[0] < field_limits[0][0] or j[0] > field_limits[0][1] or j[1] < field_limits[1][0] or j[1] > field_limits[1][1] :
            #print(j)
            j = create_point()
            #print(j)
            #print("\n")

def changePoint(points) :
    for i in points :
        if i[0] < field_limits[0][0] or i[0] > field_limits[0][1] or i[1] < field_limits[1][0] or i[1] > field_limits[1][1] :
            #print(i)
            i = create_point()
            #print(i)
            #print("\n")

if opponents != None :
    changePoint(opponents)
if defenders != None :
    changePoint(defenders)
if goalkeeper_area != None :
    if (goalkeeper_area[0][0] < field_limits[0][0]) or (goalkeeper_area[0][1] > field_limits[0][1]) or (goalkeeper_area[1][0] < field_limits[1][0]) or (goalkeeper_area[1][1] > field_limits[1][1]) :
        #print(str(goalkeeper_area))
        goalkeeper_area = [create_point_minmax(), create_point_minmax()]
        #print(str(goalkeeper_area))

if name == None :
    name = "./configs/random.json"
else :
    name = "./configs/"+name+".json"

f = open(name, "w") # à voir si on met un nom modifiable par l'utilisateur
f.write("{\n\t\"field_limits\" : "+str(field_limits)+",\n\t\"goals\" : [\n\t\t")
comma = False
for goal in goals :
    if comma == True :
        f.write(",\n\t\t")
    comma = True
    f.write("{\n\t\t\t\"posts\" : "+str(goal[0])+",\n\t\t\t\"direction\" : "+str(goal[1])+"\n\t\t}")
f.write("\n\t],\n\t\"opponents\" : \n\t\t"+str(opponents)+",\n\t\"robot_radius\" : "+str(robot_radius)+",\n\t\"theta_step\" : "+str(theta_step)+",\n\t\"pos_step\" : "+str(pos_step))
if goalkeeper_area != None :
    f.write(",\n\t\"goalkeeper_area\" : "+str(goalkeeper_area))
if defenders != None :
    f.write(",\n\t\"defenders\" : "+str(defenders))
if ball_max_speed != None :
    f.write(",\n\t\"ball_max_speed\" : "+str(ball_max_speed))
if robot_max_speed != None :
    f.write(",\n\t\"robot_max_speed\" : "+str(robot_max_speed))
if min_dist != None :
    f.write(",\n\t\"min_dist\" : "+str(min_dist))
f.write("\n}")