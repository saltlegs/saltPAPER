
class Entity():
    def __init__(self, world):
        self.components = {}
        world.entities.append(self)

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

    def __getattr__(self, name):
        for component in self.components.values():
            if hasattr(component, name):
                return getattr(component, name)
        raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")
