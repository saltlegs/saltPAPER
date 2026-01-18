from dataclasses import dataclass

@dataclass
class Position():
    x: int = 0
    y: int = 0


print(dict(Position(5,3)))


