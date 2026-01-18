from engine.ecs.entity import Entity



def spawn(*components):
    entity = Entity()

        entities = {} 

    @classmethod
    def _assign_id(cls, entity, override=None) -> int | str | None:
        """assigns ids to entities. be aware that old ids are reassigned. returns the id value set or None if failed"""
        if override is not None:
            cls.entities[override] = entity
            return override
        for i in range(len(cls.entities)+1):
            if cls.entities.get(i) is None:
                cls.entities[i] = entity
                return i
        return None
    
    @classmethod
    def get_entity_with_id(cls, id):
        """returns the item at the id given. be aware that old ids are reassigned. returns None if no id is found"""
        item = cls.entities.get(id)
        return item
