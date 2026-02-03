class Position():
    def __init__(self, entity, layer:int=0,x:int=0, y:int=0):
        self.layer = layer
        self.x = x
        self.y = y

    def set_layer(self, layer):
        self.layer = layer

    def move(self, dx, dy):
        self.x += dx
        self.y += dy