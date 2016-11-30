import sys

import pygame

import GuiScreens


class BasicGame:
    # Constructor of the basic game class.
    # This constructor calls initialize and main_loop method.

    # Mouse if True, Keyboard if False
    mouse_or_keyboard = True

    def __init__(self):
        self.initialize()
        self.main_loop()

    # Initialization method. Allows the game to initialize different
    # parameters and load assets before the game runs
    def initialize(self):

        # Fixes sound delay
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pygame.font.init()

        self.font = pygame.font.SysFont("Arial", 15)

        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.caption = "Breakout"
        pygame.display.set_caption(self.caption)

        self.framerate = 60
        self.background_color = (255, 255, 255)

        self.clock = pygame.time.Clock()
        self.show_fps = False
        # sets the current scene to the title screen.
        self.current_scene = GuiScreens.TitleScreen()

        self.icon = pygame.image.load("images/icon.png")
        pygame.display.set_icon(self.icon)

    # main loop method keeps the game running. This method continuously
    # calls the update and draw methods to keep the game alive.
    def main_loop(self):
        while True:
            gametime = pygame.time.get_ticks()
            self.update(gametime)
            self.draw(gametime)
            self.clock.tick(self.framerate)

    # Update method contains game update logic, such as updating the game
    # variables, checking for collisions, gathering input, and
    # playing audio.
    def update(self, gametime):

        events = pygame.event.get()
        pressed_keys = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.show_fps = not self.show_fps
            # pass all events on to the scenes to handle themselves.

            self.current_scene.handle_input(event, pressed_keys)

        # update current scene
        self.current_scene.update(gametime)

        # Makes sure the current scene is always updated.
        self.current_scene = self.current_scene.next_scene

    # Draw method, draws the current state of the game on the screen                        
    def draw(self, gametime):
        self.screen.fill(self.background_color)

        # show the FPS
        if self.show_fps == True:
            fps = self.font.render(str(int(self.clock.get_fps())), 1, (0, 0, 0))
            self.screen.blit(fps, (0, 0))

        # render the current scene
        self.current_scene.render(self.screen)

        pygame.display.flip()


if __name__ == "__main__":
    game = BasicGame()
