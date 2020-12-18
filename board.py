import numpy
import pygame

from problem import *
from solution import *


def maxDist(src, dst):
    """
    Src and dst are both matrices of the same size with each column representing a
    different position
    """
    diff = dst - src
    max_dist = 0
    for entry in range(diff.shape[1]):
        dist = numpy.linalg.norm(diff[:, entry])
        if dist > max_dist:
            max_dist = dist
    return max_dist


def interpolateSimplePos(src, dst, dist):
    D = np.linalg.norm(dst-src)
    if dist >= D:
        return dst
    return src + (dst-src) * dist / D

def interpolatePos(src, dst, dist):
    """
    Return the position of a robot traveling from 'src' to 'dst' with a budget of 'dist'
    """
    diff = dst - src
    pos = numpy.copy(src)
    for entry in range(diff.shape[1]):
        entry_dist = numpy.linalg.norm(diff[:, entry])
        if dist >= entry_dist:
            pos[:, entry] = numpy.copy(dst[:, entry])
        else:
            pos[:, entry] = src[:, entry] + diff[:, entry] * dist / entry_dist
    return pos


class Board:
    def __init__(self, problem, solution):
        self.problem = problem
        self.solution = solution
        self.size = numpy.array([1280, 960])
        self.goal_thickness = 5
        # colors
        self.background_color = (0, 0, 0)
        self.opponent_color = (255, 0, 255)
        self.defender_color = (255, 255, 0)
        self.goal_color = (255, 255, 255)
        self.success_color = (0, 255, 0)
        self.failure_color = (255, 0, 0)
        self.max_dist = None
        # checking that number of defenders in solution is consistent with problem
        if (not self.problem.defenders is None):
            if (self.problem.getNbDefenders() != self.solution.getNbDefenders()):
                print("Inconsistent number of defenders "
                      "(Problem: {:d}, Solution: {:d})".format(
                          self.problem.getNbDefenders(), self.solution.getNbDefenders()))
                sys.exit(1)
            self.dist = 0
            self.max_dist = maxDist(
                self.problem.defenders, self.solution.defenders)
            print("Max dist: {:f}".format(self.max_dist))
        # Compute results of shots
        self.updateShotsResults()
        # Handling dynamic case
        self.time = None
        if self.problem.ball_max_speed is not None:
            max_shot_dist = 0
            for shot in self.shots:
                shot_dist = np.linalg.norm(shot.end - shot.src)
                if shot_dist > max_shot_dist:
                    max_shot_dist = shot_dist
            self.time = 0
            self.max_time = max_shot_dist / self.problem.ball_max_speed

    def getDefenders(self):
        """
        Retrieve the defenders position corresponding to current state
        """
        if (self.problem.defenders is None):
            return self.solution.defenders
        return interpolatePos(self.problem.defenders, self.solution.defenders, self.dist)

    def getImgCenter(self):
        """ Return the position of the center of the image """
        return self.size / 2

    def getRatio(self):
        """ Return the ratio between image and field size [px/m]"""
        return 0.95 * min(self.size[0] / self.problem.getFieldWidth(),
                          self.size[1] / self.problem.getFieldHeight())

    def getPixelFromField(self, pos_in_field):
        """ From field referential to img position """
        ratio = self.getRatio()
        offset_field = pos_in_field - self.problem.getFieldCenter()
        offset_pixel = self.getRatio() * offset_field
        # Y axis is inverted to get the Z-axis pointing outside of the screen
        offset_pixel[1] *= -1
        pixel = self.getImgCenter() + offset_pixel
        return [int(pixel[0]), int(pixel[1])]

    def updateShotsResults(self):
        """
        Analyze the results of shots according to current defenders positions
        """
        self.shots = self.problem.computeShotsResults(self.getDefenders())

    def drawSegmentInField(self, screen, color, pos1, pos2, thickness):
        start = self.getPixelFromField(pos1)
        end = self.getPixelFromField(pos2)
        pygame.draw.line(screen, color, start, end, thickness)

    def drawShot(self, screen, shot):
        """
        Also updates self.opponent_can_score if kick reaches a goal and is not intercepted
        """
        color = self.failure_color
        if shot.result != ShotResult.GOAL:
            color = self.success_color
        else:
            self.opponent_can_score = True
        end = shot.end
        if self.time is not None:
            ball_dist = self.problem.ball_max_speed * min(self.time, self.max_time)
            end = interpolateSimplePos(shot.src, shot.end, ball_dist)
        self.drawSegmentInField(screen, color, shot.src, end, 1)

    def drawShots(self, screen):
        for shot in self.shots:
            self.drawShot(screen, shot)

    def drawGoals(self, screen):
        for goal in self.problem.goals:
            self.drawSegmentInField(screen, self.goal_color,
                                    goal.posts[:, 0], goal.posts[:, 1],
                                    self.goal_thickness)

    def drawDefendersZones(self, screen):
        if self.time is None:
            return
        D = self.getDefenders()
        t = min(self.time, self.max_time)
        intercept_dist = t * self.problem.robot_max_speed
        for robot_id in range(D.shape[1]):
            pygame.draw.circle(screen, np.array(self.defender_color) * 0.2,
                               self.getPixelFromField(D[:, robot_id]),
                               int(intercept_dist * self.getRatio()))

    def drawRobots(self, screen, robots, color):
        for robot_id in range(robots.shape[1]):
            # Drawing robot
            pygame.draw.circle(screen, color,
                               self.getPixelFromField(robots[:, robot_id]),
                               int(self.problem.robot_radius * self.getRatio()))
            # Drawing minimal distance
            if (self.problem.min_dist != None):
                pygame.draw.circle(screen, color,
                                   self.getPixelFromField(robots[:, robot_id]),
                                   int(self.problem.min_dist * self.getRatio() / 2), 1)

    def drawOpponents(self, screen):
        self.drawRobots(screen, self.problem.opponents, self.opponent_color)

    def drawDefenders(self, screen):
        self.drawRobots(screen, self.getDefenders(), self.defender_color)

    def step(self):
        """
        Updates variables when dynamic display is required
        """
        frame_freeze = 50
        if (not self.max_dist is None):
            dist_step = 0.01
            self.dist += dist_step
            # Adding a sleep dist to freeze once situation is reached
            if (self.dist > self.max_dist + frame_freeze * dist_step):
                self.dist = 0
            self.updateShotsResults()
        if self.time is not None:
            dt = 0.002 # [s]
            self.time += dt
            if self.time > self.max_time + frame_freeze * dt:
                self.time = 0

    def checkCollisions(self):
        robots = numpy.concatenate(
            (self.problem.opponents, self.getDefenders()), 1)
        min_dist = 2 * self.problem.robot_radius
        if (self.problem.min_dist != None):
            min_dist = self.problem.min_dist
        for r1 in range(robots.shape[1] - 1):
            for r2 in range(r1+1, robots.shape[1]):
                dist = numpy.linalg.norm(robots[:, r1] - robots[:, r2])
                if (dist < min_dist):
                    return True
        return False

    def drawDist(self, screen):
        if (not self.max_dist is None):
            shown_dist = min(self.dist, self.max_dist)
            text = "Dist: {:f} / {:f}".format(shown_dist, self.max_dist)
            text_surface = self.font.render(text, False, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.midtop = (self.size[0] / 2, 0)
            screen.blit(text_surface, text_rect)

    def drawStatus(self, screen):
        text = "Success"
        if self.opponent_can_score or self.collision or self.goalies_count > 1 or self.defenders_invalid:
            text = "Failed: "
            if self.defenders_invalid:
                text += " defenders are not on grid"
            if self.opponent_can_score:
                text += " opponent can score"
            if self.collision:
                text += " collision detected"
            if self.goalies_count > 1:
                text += " {:d} defenders in goal area".format(
                    self.goalies_count)
        text_surface = self.font.render(text, False, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.midbottom = (self.size[0] / 2, self.size[1])
        screen.blit(text_surface, text_rect)

    def checkDefendersInvalid(self):
        # If defenders are on the grid, the number of steps should 'almost' be an int
        pos_steps = self.solution.defenders / self.problem.pos_step
        return np.max(np.abs(pos_steps-np.round(pos_steps))) > 10 ** -6

    def checkGoalArea(self):
        self.goalies_count = 0
        if not self.problem.goalkeeper_area is None:
            limits = self.problem.goalkeeper_area
            defenders = self.getDefenders()
            for def_id in range(defenders.shape[1]):
                x_ok = limits[0, 0] <= defenders[0, def_id] <= limits[0, 1]
                y_ok = limits[1, 1] <= defenders[1, def_id] <= limits[1, 0]
                if x_ok and y_ok:
                    self.goalies_count += 1

    def drawGoalArea(self, screen):
        if not self.problem.goalkeeper_area is None:
            limits = self.problem.goalkeeper_area
            top_left = self.getPixelFromField(limits[:, 0])
            bot_right = self.getPixelFromField(limits[:, 1])
            left = top_left[0]
            top = top_left[1]
            width = bot_right[0] - top_left[0]
            height = bot_right[1] - top_left[1]
            goalkeeper_area = pygame.Rect(left, top, width, height)
            pygame.draw.rect(screen, (0, 0, 255), goalkeeper_area)

    def draw(self, screen):
        self.opponent_can_score = False
        self.step()
        self.collision = self.checkCollisions()
        self.defenders_invalid = self.checkDefendersInvalid()
        self.checkGoalArea()
        self.drawGoalArea(screen)
        self.drawDefendersZones(screen)
        self.drawShots(screen)
        self.drawGoals(screen)
        self.drawOpponents(screen)
        self.drawDefenders(screen)
        self.drawDist(screen)
        self.drawStatus(screen)

    def run(self):
        pygame.init()
        self.font = pygame.font.SysFont("Ubuntu Mono", 50)
        screen = pygame.display.set_mode(self.size)
        running = True
        dynamic = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_ESCAPE]):
                running = False

            screen.fill(self.background_color)
            self.draw(screen)

            pygame.display.flip()
