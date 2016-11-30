import operator
import pickle
import sys

import pygame

import BasicGame
import Gui
from GameScene import GameScene
from Scene import Scene


class TitleScreen(Scene):
    def __init__(self):

        # Put all buttons into a dictionary, very easy to store and recall them
        self.buttons = {}
        # Each button has it's own key to the dictionary for easy event handling
        self.buttons['Play'] = Gui.StandardButton((400, 250, 60, 30), 'Play', center_x=True, font_size=40)
        self.buttons['Leaderboard'] = Gui.StandardButton((400, 320, 60, 30), 'Leaderboard', center_x=True, font_size=40)
        self.buttons['Controls'] = Gui.ToggleButton((400, 390, 60, 30), 'Controls', 'Mouse', 'Keyboard', center_x=True,
                                                    font_size=40)
        if BasicGame.BasicGame.mouse_or_keyboard:
            self.buttons['Controls'].state = True
        else:
            self.buttons['Controls'].state = False
        self.buttons['Quit'] = Gui.StandardButton((400, 460, 60, 30), 'Quit', center_x=True, font_size=40)

        self.logo_image = pygame.image.load("images/logo.png").convert_alpha()

        # Calls the initializer method in the Scene class because it is a subclass
        super().__init__()

    def handle_input(self, event, pressed_keys):

        # Each button returns a list of actions performed in the last frame. If the click action is performed
        # then it will return true and execute the code in the IF block

        if 'click' in self.buttons['Play'].handle_event(event):
            self.change_scene(HelpScreen())
        if 'click' in self.buttons['Controls'].handle_event(event):
            BasicGame.BasicGame.mouse_or_keyboard = self.buttons['Controls'].state
        if 'click' in self.buttons['Leaderboard'].handle_event(event):
            self.change_scene(LeaderboardsScreen())
        if 'click' in self.buttons['Quit'].handle_event(event):
            pygame.quit()
            sys.exit()

    def update(self, gametime):
        self.gametime = gametime

    def render(self, screen):

        screen.blit(self.logo_image, (400 - self.logo_image.get_width() / 2, 10))
        # Because each button is stored in a dictionary, you can easily iterate through and call their draw method
        for k, v in self.buttons.items():
            v.draw(screen)


class LeaderboardsScreen(Scene):
    def __init__(self):
        self.buttons = {}
        self.leaderboards_box = Gui.LeaderboardsBox(20, 80, 760, 500)
        try:
            self.leaderboards_box.add_cell_data(pickle.load(open("scores.dat", "rb")))
            # this sorts the list so the highest score is at the top. Defaults to small to big to you have to reverse it
            self.leaderboards_box.cell_data.sort(key=operator.itemgetter('score'), reverse=True)
        except:
            self.leaderboards_box.cell_data = []
        self.buttons['Main Menu'] = Gui.StandardButton((100, 20, 60, 30), 'Main Menu', font_size=40)
        super().__init__()

    def handle_input(self, event, pressed_keys):
        self.leaderboards_box.handle_input(event)
        if 'click' in self.buttons['Main Menu'].handle_event(event):
            self.change_scene(TitleScreen())

    def update(self, gametime):
        self.leaderboards_box.update()

    def render(self, screen):
        font = pygame.font.Font("8bitfont.ttf", 60)
        title = font.render("Leaderboards", 0, (0, 0, 0))
        screen.blit(title, (300, 20))
        self.leaderboards_box.draw(screen)
        for k, v in self.buttons.items():
            v.draw(screen)


class AddToLeaderboards(Scene):
    def __init__(self, score):
        pygame.key.set_repeat(500, 50)
        self.buttons = {}
        self.score = score
        self.buttons['Add'] = Gui.StandardButton((400, 350, 60, 30), "Add score", center_x=True, font_size=40)
        self.font = pygame.font.SysFont('Arial', 30)
        self.textbox = Gui.TextBox(300, 200, 200, 45, enter_action=self.enter_action)
        super().__init__()

    def enter_action(self):
        self.write_score_to_file(self.score)
        self.change_scene(LeaderboardsScreen())

    def handle_input(self, event, pressed_keys):
        self.textbox.handle_input(event)
        if 'click' in self.buttons['Add'].handle_event(event):
            self.write_score_to_file(self.score)
            self.change_scene(LeaderboardsScreen())

    def write_score_to_file(self, score):
        # first read the file
        try:
            # load the scores into a variable
            scores = pickle.load(open("scores.dat", "rb"))
        except:
            # if it cant find or open the file it creates an empty list
            scores = []
        # appends the new score on to the existing scores
        scores.append({'name': self.textbox.get_text(), 'score': score})
        # rewrites the entire file with the new list
        pickle.dump(scores, open("scores.dat", "wb"))

    def update(self, gametime):
        self.textbox.update()

    def render(self, screen):
        large_font = pygame.font.SysFont("Arial", 60)
        title = large_font.render("Add your score!", 1, (0, 0, 0))
        score = self.font.render("Score: " + str(self.score), 1, (0, 0, 0))
        label = self.font.render("Name: ", 1, (0, 0, 0))
        self.textbox.draw(screen)
        screen.blit(label, (self.textbox.rect.x - label.get_width() - 10, self.textbox.rect.y))
        screen.blit(title, (400 - title.get_width() / 2, 20))
        screen.blit(score, (400 - score.get_width() / 2, 100))
        for k, v in self.buttons.items():
            v.draw(screen)


class HelpScreen(Scene):
    def __init__(self):
        self.font = pygame.font.SysFont('Arial', 25)
        self.buttons = {}
        self.buttons['Start'] = Gui.StandardButton((400, 500, 60, 30), "Start!", center_x=True, font_size=40)
        self.purple = pygame.image.load("images/purple.png").convert()
        self.blue = pygame.image.load("images/blue.png").convert()
        self.green = pygame.image.load("images/green.png").convert()
        self.yellow = pygame.image.load("images/yellow.png").convert()
        self.red = pygame.image.load("images/red.png").convert()
        self.gold = pygame.image.load("images/gold.png").convert_alpha()
        self.text = [
            "Welcome to Breakout",
            "The aim of the game is to bounce the ball off the paddle and hit the blocks.",
            "Each time you hit a block you earn points depending on the colour of the block.",
            "Purple: 10",
            "Blue: 20",
            "Green: 30",
            "Yellow: 40",
            "Red: 50",
            "Every 10 seconds a new golden block appears, this can earn you 100 points.",
            "After 1 minute the speed increases, after 2 minutes the speed increases again.",
            "Don't let the ball hit the red line! You'll lose a life and you only have 3!",
            "Press left click or space to launch the ball."]
        super().__init__()

    def handle_input(self, event, pressed_keys):
        if 'click' in self.buttons['Start'].handle_event(event):
            self.change_scene(GameScene(pygame.time.get_ticks()))

    def update(self, gametime):
        pass

    def render(self, screen):
        y_start = 20
        for text in self.text:
            x = self.font.render(text, 1, (0, 0, 0))
            screen.blit(x, (20, y_start))
            y_start += 40
        for k, v in self.buttons.items():
            v.draw(screen)

        screen.blit(self.purple, (130, 145))
        screen.blit(self.blue, (130, 185))
        screen.blit(self.green, (130, 225))
        screen.blit(self.yellow, (130, 265))
        screen.blit(self.red, (130, 305))
        screen.blit(self.gold, (700, 345))
