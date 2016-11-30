import random

import pygame

import Entities
import Gui
import GuiScreens
from Scene import Scene


class GameScene(Scene):
    def __init__(self, start_time):

        pygame.key.set_repeat()
        # Stores 1 dimensional list of each block
        self.block_list = []
        self.width = pygame.display.Info().current_w
        self.height = pygame.display.Info().current_h
        self.start_time = start_time
        self.font = pygame.font.Font("8bitfont.ttf", 25)
        self.large_font = pygame.font.Font("8bitfont.ttf", 60)
        self.game_over_text = pygame.image.load("images/gameover.png").convert_alpha()
        self.game_over_state = False
        self.victory_state = False

        self.buttons = {}
        self.buttons['Main Menu'] = Gui.StandardButton((400, 350, 60, 30), 'Main Menu', center_x=True, font_size=40)
        self.buttons['Main Menu'].visible = False
        self.buttons['Leaderboards'] = Gui.StandardButton((400, 420, 60, 30), 'Add to leaderboards', center_x=True,
                                                          font_size=40)
        self.buttons['Leaderboards'].visible = False
        # Draw all the blocks on the screen
        self.draw_blocks()

        self.lives = 3
        self.score = 0

        # Initialises the Paddle and ball classes ready to use in the game
        self.paddle = Entities.Paddle()
        self.ball = Entities.Ball(self.paddle.rect.x + self.paddle.rect.width / 2 - 10, self.paddle.rect.y - 20)

        # Load audio
        self.block_hit_sound = pygame.mixer.Sound("sounds/hit.wav")
        self.game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")
        self.gametime = 0
        self.time_in_play_store = 0
        self.time_in_play = 0
        self.gold_block_exists = False
        self.time_store = 0
        self.running = False
        self.new_game = True
        self.speed_up_1 = False
        self.speed_up_2 = False

        # Is also a subclass of Scene so it needs to be initialized
        super().__init__()

    def handle_input(self, event, pressed_keys):
        if self.running or self.new_game:
            self.paddle.handle_input(event, pressed_keys)
        if self.new_game:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Launches ball at a random X velocity
                    self.ball.xspeed = random.uniform(-self.ball.maxspeed, self.ball.maxspeed)
                    self.new_game = False
                    self.running = True
                    self.start_time = self.gametime
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.ball.xspeed = random.uniform(-self.ball.maxspeed, self.ball.maxspeed)
                    self.new_game = False
                    self.running = True
                    self.start_time = self.gametime
        if 'click' in self.buttons['Main Menu'].handle_event(event):
            self.change_scene(GuiScreens.TitleScreen())
        if 'click' in self.buttons['Leaderboards'].handle_event(event):
            self.change_scene(GuiScreens.AddToLeaderboards(self.score))

    def draw_blocks(self):
        colour_list = ["red", "yellow", "green", "blue", "purple"]
        y_coord = 40
        start_x = 10
        for colour in colour_list:
            for i in range(0, 12):
                self.block_list.append(Entities.Block(start_x + 65 * i, y_coord, colour))
            y_coord += 20
            for i in range(0, 12):
                self.block_list.append(Entities.Block(start_x + 65 * i, y_coord, colour))
            y_coord += 20

    def update(self, gametime):
        self.gametime = gametime
        if not self.running and self.new_game:
            self.ball.launch_mode(self.paddle)

        # Collision detection
        elif self.running and not self.new_game:
            for block in self.block_list:
                if pygame.sprite.collide_rect(self.ball, block):
                    # So I've checked that they collide. But I need to check which side of the block they hit
                    # If they hit the left, they don't need to change the Y direction, just the X.
                    if self.ball.rect.right >= block.rect.left and self.ball.rect.centerx < block.rect.left and ((self.ball.rect.top > block.rect.top and self.ball.rect.top < block.rect.bottom) or (self.ball.rect.bottom > block.rect.top and self.ball.rect.bottom < block.rect.bottom)):
                        self.ball.bounce("Left")
                    elif self.ball.rect.left <= block.rect.right and self.ball.rect.centerx > block.rect.right and ((self.ball.rect.top > block.rect.top and self.ball.rect.top < block.rect.bottom) or (self.ball.rect.bottom > block.rect.top and self.ball.rect.bottom < block.rect.bottom)):
                        self.ball.bounce("Right")
                    else:
                        self.ball.bounce()
                    self.block_hit(block)

                    # Collision isn't perfect but stopped the glitch which happened before.

            if pygame.sprite.collide_rect(self.ball, self.paddle):
                # distance from the center of the paddle
                dist = self.ball.rect.centerx - self.paddle.rect.centerx
                # Bounces at an angle depending on how far away it is from the center of the paddle.
                self.ball.bounce(dist)

            if self.ball.rect.bottom > self.paddle.rect.top and (
                            self.ball.rect.right < self.paddle.rect.left or self.ball.rect.left > self.paddle.rect.right):
                self.game_over()

            # calculates the time in play. x is the difference in game time since the last frame
            # x is added to the overall time in play
            x = self.time_in_play_store
            self.time_in_play_store = self.gametime - self.start_time
            x = self.time_in_play_store - x
            if x < 0:
                x = 0
            self.time_in_play += x
            self.check_speed_up(gametime)

            # Update position of the ball
            self.ball.update()

        self.generate_gold_block(gametime)

    # checks the game time, after 1 minute the game speeds up, after 2 minutes it speeds up again.
    def check_speed_up(self, gametime):
        if self.time_in_play > 60000 and not self.speed_up_1:
            if self.ball.yspeed < 0:
                self.ball.yspeed = -6
            else:
                self.ball.yspeed = 6
            self.speed_up_1 = True
        if self.time_in_play > 120000 and not self.speed_up_2:
            if self.ball.yspeed < 0:
                self.ball.yspeed = -8
            else:
                self.ball.yspeed = 8
            self.speed_up_2 = True

    def block_hit(self, block):

        self.block_hit_sound.stop()
        self.block_hit_sound.play()

        # Scores for each block are added
        if block.colour == "purple":
            self.score += 10
        elif block.colour == "blue":
            self.score += 20
        elif block.colour == "green":
            self.score += 30
        elif block.colour == "yellow":
            self.score += 40
        elif block.colour == "red":
            self.score += 50
        elif block.colour == "gold":
            self.score += 100

        self.block_list.remove(block)

        if len(self.block_list) == 0:
            self.victory()

    # generate a gold block after 10 seconds.
    def generate_gold_block(self, gametime):
        if self.running and not self.new_game:
            if self.time_in_play > 10000:
                if not self.gold_block_exists:
                    self.time_store = self.time_in_play
                    self.current_gold_block = random.choice(self.block_list)
                    self.gold_block_exists = True
                    self.current_gold_block.make_gold()
                elif self.gold_block_exists and self.time_in_play > self.time_store + 10000:
                    self.time_store = gametime
                    self.current_gold_block.ungold()
                    self.current_gold_block = random.choice(self.block_list)
                    self.current_gold_block.make_gold()

    def game_over(self):
        if self.lives == 0:
            self.running = False
            self.game_over_state = True
            self.game_over_sound.play()
        else:
            self.lives -= 1
            self.running = False
            self.new_game = True

    def victory(self):
        self.running = False
        self.victory_state = True

    def render(self, screen):

        # Iterate through list and draw each block
        for block in self.block_list:
            block.draw(screen)

        score_text = self.font.render("Score: " + str(self.score), 0, (0, 0, 0))
        lives_text = self.font.render("Lives: " + str(self.lives), 0, (0, 0, 0))
        if self.speed_up_1 and self.speed_up_2:
            speed = 3
        elif self.speed_up_1:
            speed = 2
        else:
            speed = 1

        speed_text = self.font.render("Speed Level: " + str(speed), 0, (0, 0, 0))
        screen.blit(score_text, (20, 10))
        screen.blit(speed_text, (300, 10))
        screen.blit(lives_text, (700, 10))

        for k, v in self.buttons.items():
            v.draw(screen)

        if self.game_over_state:
            screen.blit(self.game_over_text, (self.width / 2 - self.game_over_text.get_width() / 2, 100))
            final_score = self.font.render("Your score: " + str(self.score), 0, (0, 0, 0))
            screen.blit(final_score, (self.width / 2 - final_score.get_width() / 2, 280))
            self.buttons['Main Menu'].visible = True
            self.buttons['Leaderboards'].visible = True

        if self.victory_state:
            victory_text = self.large_font.render("You win!", 0, (0, 0, 0))
            screen.blit(victory_text, (self.width / 2 - victory_text.get_width() / 2, 150))
            final_score = self.font.render("Your score: " + str(self.score), 0, (0, 0, 0))
            screen.blit(final_score, (self.width / 2 - final_score.get_width() / 2, 280))
            self.buttons['Main Menu'].visible = True
            self.buttons['Leaderboards'].visible = True
        pygame.draw.line(screen, (255,200,200), (0,self.paddle.rect.top + 1), (self.width, self.paddle.rect.top + 1), 3)
        self.paddle.draw(screen)
        self.ball.draw(screen)
