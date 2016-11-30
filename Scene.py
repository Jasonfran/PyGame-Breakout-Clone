class Scene:
    """ Very simply scene system for easily changing scenes """

    def __init__(self):
        self.next_scene = self

    def handle_input(self, event, pressed_keys):
        raise NotImplementedError

    def update(self, gametime):
        raise NotImplementedError

    def render(self, screen):
        raise NotImplementedError

    def change_scene(self, next_scene):
        self.next_scene = next_scene
