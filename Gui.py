import pygame
from pygame.locals import *

pygame.font.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKGREY = (64, 64, 64)
GREY = (128, 128, 128)
LIGHTGREY = (212, 208, 200)


class StandardButton(object):
    # Create all the attributes
    def __init__(self, rect=None, label='', bgcolour=LIGHTGREY,
                 fgcolour=BLACK, hcolour=GREY, font=None, auto_resize=True, center_x=False, font_size=25):

        # If no position or size given then just stick it in the corner
        if rect is None:
            self.rect = pygame.Rect(0, 0, 30, 60)
        else:
            self.rect = pygame.Rect(rect)

        # Create attributes
        self.label = label
        self.bgcolour = bgcolour
        self.fgcolour = fgcolour
        self.hcolour = hcolour
        self.auto_resize = auto_resize
        self.center_x = center_x

        # If font not specified then use default
        if font is None:
            self.font = pygame.font.SysFont("Arial", font_size)
        else:
            self.font = font

        # Button states
        self.button_down = False
        self.mouse_over = False
        self.last_click_on_button = False
        self.visible = True

        # Create button surfaces for all states
        self.surface_normal = pygame.Surface(self.rect.size)
        self.surface_down = pygame.Surface(self.rect.size)
        self.surface_highlight = pygame.Surface(self.rect.size)

        # Draw the initial button
        self.update()

    def handle_event(self, event):
        # Don't care if the events aren't mouse related or the button isn't visible
        if event.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self.visible:
            return []

        ret_val = []

        has_exited = False
        if not self.mouse_over and self.rect.collidepoint(event.pos):
            # Mouse has entered
            self.mouse_over = True
            self.mouse_enter(event)
            ret_val.append('enter')
        elif self.mouse_over and not self.rect.collidepoint(event.pos):
            # Mouse exited
            self.mouse_over = False
            has_exited = True

        if self.rect.collidepoint(event.pos):
            # mouse event over button
            if event.type == MOUSEMOTION:
                self.mouse_move(event)
                ret_val.append('move')
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.button_down = True
                self.last_click_on_button = True
                self.mouse_down(event)
                ret_val.append('down')

        else:
            if event.type in (MOUSEBUTTONUP, MOUSEBUTTONDOWN) and event.button == 1:
                # if an up/down happens off button, next up wont cause click
                self.last_click_on_button = False

        # mouse up handled whether or not it was over button
        do_mouse_click = False
        if event.type == MOUSEBUTTONUP and event.button == 1:
            if self.last_click_on_button:
                do_mouse_click = True
            self.last_click_on_button = False

            if self.button_down:
                self.button_down = False
                self.mouse_up(event)
                ret_val.append('up')

            if do_mouse_click:
                self.button_down = False
                self.mouse_click(event)
                ret_val.append('click')

        if has_exited:
            self.mouse_exit(event)
            ret_val.append('exit')

        # returns a list of actions performed in the last frame. e.g click, up, exit, down
        return ret_val

    def draw(self, screen):
        if self.visible:
            if self.button_down:
                screen.blit(self.surface_down, self.rect)
            elif self.mouse_over:
                screen.blit(self.surface_highlight, self.rect)
            else:
                screen.blit(self.surface_normal, self.rect)

    def update(self):

        # Fill background colour
        self.surface_normal.fill(self.bgcolour)
        self.surface_down.fill(self.bgcolour)
        self.surface_highlight.fill(self.hcolour)

        # Draw text
        label_surface = self.font.render(self.label, True, self.fgcolour)
        labelrect = label_surface.get_rect()

        # Will automatically resize the button when the label is changed if needed
        # Also automatically re-centers the button to where it was before the label change
        # so it means I don't have to do it manually.
        if self.center_x:
            self.rect.x = self.rect.x - self.rect.width / 2

        if self.auto_resize:
            if labelrect.width >= self.rect.width - 50:
                center_pos = self.rect.center

                self.change_size(labelrect.width + 50, self.rect.height, False)  # False stops it updating
                self.change_pos(center_pos[0] - self.rect.width / 2, center_pos[1] - self.rect.height / 2, False)

                self.change_size(self.rect.width, labelrect.height + 5, False)

                # If I don't stop them updating then it just becomes a huge loop which never ends and eventually
                # breaks the program

        w = self.rect.width
        h = self.rect.height

        labelrect.center = int(w / 2), int(h / 2)

        # puts text on each button surface
        self.surface_normal.blit(label_surface, labelrect)
        self.surface_down.blit(label_surface, labelrect)
        self.surface_highlight.blit(label_surface, labelrect)

        # button borders
        pygame.draw.rect(self.surface_down, BLACK, pygame.Rect((0, 0, w, h)), 3)  # thick border on click
        pygame.draw.rect(self.surface_normal, BLACK, pygame.Rect((0, 0, w, h)), 1)  # thin border for normal
        pygame.draw.rect(self.surface_highlight, BLACK, pygame.Rect((0, 0, w, h)), 1)  # thin border for hover

    # This is useful if a button needs its label changing
    def set_label(self, label):
        self.label = label
        self.update()
        return self.label

    # I can change the size of the button and decide whether to update the button
    def change_size(self, w, h, update=True):
        self.rect.size = (w, h)
        self.surface_normal = pygame.transform.scale(self.surface_normal, (w, h))
        self.surface_down = pygame.transform.scale(self.surface_down, (w, h))
        self.surface_highlight = pygame.transform.scale(self.surface_highlight, (w, h))

        if update:
            self.update()

        return self.rect

    # I can change the position if needed
    def change_pos(self, x, y, update=True):
        self.rect.x = x
        self.rect.y = y

        if update:
            self.update()

    # These methods mean that any subclass of the standard button can easily implement its own actions for certain
    # mouse events. Such as my toggle button uses this mouse_click function to change the button text and boolean
    def mouse_click(self, event):
        pass

    def mouse_enter(self, event):
        pass

    def mouse_exit(self, event):
        pass

    def mouse_move(self, event):
        pass

    def mouse_down(self, event):
        pass

    def mouse_up(self, event):
        pass


class ToggleButton(StandardButton):
    def __init__(self, rect=None, label='', state_1='True', state_2='False', bgcolour=LIGHTGREY,
                 fgcolour=BLACK, hcolour=GREY, font=None, auto_resize=True, center_x=False, font_size=25):

        self.state = True
        self.state_1 = state_1
        self.state_2 = state_2
        self.state_text = state_1
        self.orig_x = rect[0]

        super().__init__(rect, label, bgcolour, fgcolour, hcolour, font, auto_resize, center_x, font_size)

    # Overrides StandardButton
    def update(self):

        # Fill background colour
        self.surface_normal.fill(self.bgcolour)
        self.surface_down.fill(self.bgcolour)
        self.surface_highlight.fill(self.hcolour)

        if self.state == True:
            self.state_text = self.state_1
        else:
            self.state_text = self.state_2

        # Draw text
        label_surface = self.font.render(self.label + ": " + str(self.state_text), True, self.fgcolour)
        labelrect = label_surface.get_rect()

        # Will automatically resize the button when the label is changed if needed
        # Also automatically re-centers the button to where it was before the label change
        # so it means I don't have to do it.

        if self.center_x:
            self.rect.centerx = self.orig_x

        if self.auto_resize:
            if labelrect.width >= self.rect.width - 50:
                center_pos = self.rect.center

                self.change_size(labelrect.width + 50, self.rect.height, False)  # False stops it updating
                self.change_pos(center_pos[0] - self.rect.width / 2, center_pos[1] - self.rect.height / 2, False)

                self.change_size(self.rect.width, labelrect.height + 5, False)

                # If I don't stop them updating then it just becomes a huge loop which never ends and eventually
                # breaks the program

        w = self.rect.width
        h = self.rect.height

        labelrect.center = int(w / 2), int(h / 2)

        # puts text on each button surface
        self.surface_normal.blit(label_surface, labelrect)
        self.surface_down.blit(label_surface, labelrect)
        self.surface_highlight.blit(label_surface, labelrect)

        # button borders
        pygame.draw.rect(self.surface_down, BLACK, pygame.Rect((0, 0, w, h)), 3)  # thick border on click
        pygame.draw.rect(self.surface_normal, BLACK, pygame.Rect((0, 0, w, h)), 1)  # thin border for normal
        pygame.draw.rect(self.surface_highlight, BLACK, pygame.Rect((0, 0, w, h)), 1)  # thin border for hover

    def mouse_click(self, event):
        if self.state:
            self.state = False
        else:
            self.state = True
        self.update()

    def get_state(self):
        return self.state


# This is a leaderboards box, but it is also capable of displaying any list in a scrollable table
# However, it is only used for the leaderboards.

# Works by drawing a surface(1) onto a surface(2), this clips the surface(1) by the dimensions of surface(2)
# Then it just scrolls by offsetting the x coordinates
class LeaderboardsBox(object):
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.box_surface = pygame.Surface(self.rect.size)
        self.container_surface = pygame.Surface((self.rect.width - 36, self.rect.height - 6))
        self.cell_data = []
        self.cell_height = 80
        self.cell_padding = 1
        self.table_rect = pygame.Rect(0, 0, self.rect.width - 36, 0)
        self.table_surface = pygame.Surface(self.table_rect.size)
        self.scrollbar_rect = pygame.Rect(self.container_surface.get_width() + 10, 0, 20, 50)
        self.scrollbar_surface = pygame.Surface(self.scrollbar_rect.size)
        self.font = pygame.font.SysFont("Arial", 35)
        self.mouse_down = False
        self.initial_click = (0, 0)
        self.y_diff = 0
        self.scrollbar_max_travel = self.rect.h - self.scrollbar_rect.height
        self.scrollbar_pos = self.scrollbar_rect.centery - self.scrollbar_rect.height / 2
        self.scrollbar_percent_travelled = self.scrollbar_pos / self.scrollbar_max_travel * 100

        self.update()

    # This makes sure that the table is always the right size after any changes
    # because the table can be edited in real time
    # If these measurements weren't updated, some data wouldn't show.
    def update_measurements(self):
        self.table_rect = pygame.Rect(0, 0, self.rect.width - 36, (self.cell_height + self.cell_padding) * len(self.cell_data))
        if self.table_rect.h < self.container_surface.get_height():
            self.table_rect.h = self.container_surface.get_height()
        self.table_surface = pygame.Surface(self.table_rect.size)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.mouse_down:

            # Need to create a collision rectangle as the scrollbar rect doesn't have accurate x and y coords
            # This is created by adding the scrollbar x and y to that of the rect it is inside.
            # This gets x and y coordinates for the screen space needed for mouse collision
            scrollbar_collision_rect = pygame.Rect(self.scrollbar_rect.x + self.rect.x,
                                                   self.scrollbar_rect.y + self.rect.y, self.scrollbar_rect.w,
                                                   self.scrollbar_rect.h)
            if scrollbar_collision_rect.collidepoint(event.pos):
                self.mouse_down = True
                self.initial_click = event.pos
                self.y_diff = self.initial_click[1] - scrollbar_collision_rect.top

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.mouse_down:
            self.mouse_down = False

        if event.type == pygame.MOUSEMOTION and self.mouse_down:
            self.scrollbar_rect.y = event.pos[1] - self.rect.y - self.y_diff
            if self.scrollbar_rect.y < 0:
                self.scrollbar_rect.y = 0
            if self.scrollbar_rect.bottom > self.box_surface.get_height():
                self.scrollbar_rect.bottom = self.box_surface.get_height()
            self.scrollbar_pos = self.scrollbar_rect.centery - self.scrollbar_rect.height / 2
            self.scrollbar_percent_travelled = self.scrollbar_pos / self.scrollbar_max_travel * 100

            self.table_rect.y = -((self.table_rect.h - self.container_surface.get_height()) * self.scrollbar_percent_travelled) / 100

    def add_cell_data(self, list):
        self.cell_data = list
        self.update_measurements()

    def add_item(self, name, score):
        self.cell_data.append({'name': name, 'score': score})
        self.update_measurements()

        return name, score

    def remove_item(self, index):
        self.cell_data.pop(index)

    def update(self):
        self.box_surface.fill((255, 255, 255))
        self.container_surface.fill((0, 255, 0))
        self.table_surface.fill((255, 255, 255))
        self.scrollbar_surface.fill((0, 0, 180))
        pygame.draw.rect(self.box_surface, BLACK, pygame.Rect((0, 0, self.rect.w, self.rect.h)), 3)

    def draw(self, screen):
        # This draws the data, it could be improved by having each cell as a new surface but this works fine.
        y = 0
        id_num = 1
        for i in self.cell_data:
            pygame.draw.rect(self.table_surface, BLACK, pygame.Rect((0, y, self.table_rect.w, self.cell_height)), 1)
            id = self.font.render(str(id_num), 1, (0, 0, 0))
            pygame.draw.line(self.table_surface, (0, 0, 0), (id.get_width() + 30, y),
                             (id.get_width() + 30, y + self.cell_height - 1), 3)
            name = self.font.render("Player: " + i['name'], 1, (0, 0, 0))
            score = self.font.render("Score: " + str(i['score']), 1, (0, 0, 0))
            self.table_surface.blit(id, (10, y + id.get_height() / 2))
            self.table_surface.blit(name, (id.get_width() + 50, y + name.get_height() / 2))
            self.table_surface.blit(score, (name.get_width() + 100, y + score.get_height() / 2))
            y += (self.cell_height + self.cell_padding)
            id_num += 1
        self.box_surface.blit(self.scrollbar_surface, self.scrollbar_rect)
        self.container_surface.blit(self.table_surface, self.table_rect)
        screen.blit(self.box_surface, self.rect)
        screen.blit(self.container_surface, (self.rect.x + 3, self.rect.y + 3))


# A simple text box object for text input
# This works similar to the leaderboards box. It draws the text onto the textbox surface, it can then be offset
# by a certain amount of pixel to the left in order to scroll horizontally.
class TextBox(object):
    def __init__(self, x, y, width, height, enter_action):
        # enter_action is the action performed when pressing the enter key
        self.rect = pygame.Rect(x, y, width, height)
        self.box_surface = pygame.Surface(self.rect.size)
        self.container_surface = pygame.Surface(self.rect.size)
        self.in_focus = False
        self.enter_action = enter_action
        self.string = ""
        self.font = pygame.font.SysFont('Arial', 30)
        self.text = None
        self.text_x_offset = -5
        self.update()

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.in_focus = True
            else:
                self.in_focus = False
        if self.in_focus:
            if event.type == pygame.KEYDOWN:
                # handle different events. Backspace acts like backspace, enter does the supplied action
                # and anything else is appended to the string
                if event.key == K_BACKSPACE:
                    self.string = self.string[:-1]
                    if self.text.get_width() + 5 > self.box_surface.get_width():
                        self.text_x_offset = (self.box_surface.get_width() - self.text.get_width())
                    elif self.text.get_width() + 5 < self.box_surface.get_width():
                        self.text_x_offset = 5
                elif event.key == K_RETURN:
                    self.enter_action()
                else:
                    if self.text.get_width() + 5 > self.box_surface.get_width():
                        self.text_x_offset = (self.box_surface.get_width() - self.text.get_width() - 20)
                    else:
                        self.text_x_offset = 5
                    self.string += event.unicode

    def get_text(self):
        return self.string

    def update(self):
        self.box_surface.fill((255, 255, 255))
        if self.in_focus:
            colour = (255, 0, 0)
        else:
            colour = (0, 0, 0)
        pygame.draw.rect(self.box_surface, colour, pygame.Rect((0, 0, self.rect.w, self.rect.h)), 3)

    def draw(self, screen):

        self.text = self.font.render(self.string, 0, (0, 0, 0))
        self.box_surface.blit(self.text, (self.text_x_offset, 5))
        screen.blit(self.box_surface, (self.rect.x, self.rect.y))
