import BasicGame
import pygame


class Block(pygame.sprite.Sprite):
    number_of_blocks = 0

    def __init__(self, x, y, colour):
        # Assign an ID to the block, although I don't currently need it
        self.id = Block.number_of_blocks + 1
        Block.number_of_blocks += 1

        # Creates a Rect for the block, extremely easy to keep track of position and size
        self.x = x
        self.y = y
        self.original_colour = colour

        # Loads the image of the block for the colour specified
        self.image = pygame.image.load("images/" + colour + ".png").convert()
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())
        self.colour = colour

    def make_gold(self):
        self.colour = "gold"
        self.image = pygame.image.load("images/" + self.colour + ".png").convert_alpha()
        self.rect = pygame.Rect(self.x - 5, self.y - 3, self.image.get_width(), self.image.get_height())

    def ungold(self):
        self.colour = self.original_colour
        self.image = pygame.image.load("images/" + self.colour + ".png").convert()
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Paddle(pygame.sprite.Sprite):
    def __init__(self):

        self.image = pygame.image.load("images/paddle.png").convert()

        # Rect for position and size
        self.rect = pygame.Rect(370, pygame.display.Info().current_h - 50, 80, 15)
        self.move_left = False
        self.move_right = False

    def handle_input(self, event, pressed_keys):
        
        # check if mouse or keyboard controls and move the paddle
        if BasicGame.BasicGame.mouse_or_keyboard:
            if event.type == pygame.MOUSEMOTION:
                self.rect.x = event.pos[0] - self.rect.width / 2
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move_left = True
                if event.key == pygame.K_RIGHT:
                    self.move_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.move_left = False
                if event.key == pygame.K_RIGHT:
                    self.move_right = False
    
    # draws the paddle on the screen
    def draw(self, screen):
        if self.rect.x <= 0:
            self.rect.x = 0
        elif self.rect.x + self.rect.width >= pygame.display.Info().current_w:
            self.rect.x = pygame.display.Info().current_w - self.rect.width
        if self.move_left:
            self.rect.x -= 10
        elif self.move_right:
            self.rect.x += 10
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.image = pygame.transform.scale(pygame.image.load("images/ball.png").convert_alpha(), (20, 20))
        self.yspeed = 4.0
        self.xspeed = 0
        self.maxspeed = 8.0
        self.direction = "Right"
        self.display_width = pygame.display.Info().current_w
        self.display_height = pygame.display.Info().current_h
        self.wall_hit_sound = pygame.mixer.Sound("sounds/wall_hit.wav")

    # this function will bounce the ball. supplying the direction makes it bounce in a certain direction
    # other wise it just reverses it's y direction
    def bounce(self, direction=None):

        if direction == "Right":
            self.direction = "Right"
        elif direction == "Left":
            self.direction = "Left"
        elif direction == None:
            self.yspeed = self.yspeed * -1
        else:
            if direction >= 0:
                is_pos = True
            else:
                is_pos = False

            i = abs(direction)

            multiplier = i / 40

            self.xspeed = self.maxspeed * multiplier

            # Fix glitch
            if self.xspeed < 1:
                self.xspeed = 1

            if is_pos:
                self.direction = "Right"
            else:
                self.direction = "Left"

            self.yspeed *= -1
    
    # just puts the ball on the supplied paddle surface
    def launch_mode(self, paddle):
        self.rect.centerx = paddle.rect.centerx
        self.rect.midbottom = paddle.rect.midtop

    def update(self):
        self.rect.y -= self.yspeed

        if self.direction == "Left":
            self.rect.x -= abs(self.xspeed)
        elif self.direction == "Right":

            # Using absolute value fixes bug I had where it was adding a negative number making it think it was going
            # right but it was actually going left
            self.rect.x += abs(self.xspeed)

        # handle wall hits and play sounds. Will stop already playing sound to stop overlay
        if self.rect.right >= self.display_width:
            self.wall_hit_sound.stop()
            self.wall_hit_sound.play()
            self.rect.right = self.display_width
            self.bounce("Left")

        if self.rect.left <= 0:
            self.bounce("Right")
            self.rect.x = 0
            self.wall_hit_sound.stop()
            self.wall_hit_sound.play()

        if self.rect.top <= 0:
            self.wall_hit_sound.stop()
            self.wall_hit_sound.play()
            self.rect.top = 0
            self.bounce()

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
