
class Entity():
    _id_counter = 0

    def __init__(self, world):
        self.id = Entity._id_counter
        Entity._id_counter += 1
        self.components = {}
        self.world = world
        self.killed = False
        world.entities[self.id] = self

    def add(self, component):
        self.components[type(component)] = component

    def add_many(self, *components):
        for component in components:
            self.add(component)

    def get(self, component_type):
        for comp_cls, comp in self.components.items():
            if issubclass(comp_cls, component_type):
                return comp
        return None

    def has(self, component_type):
        return (self.get(component_type) is not None)

    def remove(self, component_type):
        comp = self.get(component_type)
        if comp:
            self.components.pop(type(comp), None)

    def kill(self):
        self.killed = True
        self.world.entities.pop(self.id, None)
        return self

    def __getattr__(self, name):
        for component in self.components.values():
            if hasattr(component, name):
                return getattr(component, name)
        raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

    def __setattr__(self, name, value):
        if "components" in self.__dict__:
            for component in self.components.values():
                if hasattr(component, name):
                    setattr(component, name, value)
                    return
        object.__setattr__(self, name, value)
