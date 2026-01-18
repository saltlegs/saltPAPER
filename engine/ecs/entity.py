
class Entity():
    def __init__(self):
        self.components = []

    def has_component_type(self, component_type):
        """checks for and returns a given component type. returns False if not found"""
        for component in self.components:
            if type(component) is component_type:
                return component
        return False
