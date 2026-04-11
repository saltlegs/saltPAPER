class axes:
    VERTICAL = True
    HORIZONTAL = False

class MenuList:
    """
    a navigable menu using x,y coordinates. pointer is always (x, y).
    - axis:   the free axis (axes.VERTICAL = up/down moves, axes.HORIZONTAL = left/right moves)
    - twodim: if True, both axes are free; if False, only the given axis moves
    - limit:  in 2D, limits movement on the non-free axis: 'min' (clamp to start), 'max' (clamp to end), None (wrap)

    1D vertical:   items at (0,0), (0,1), (0,2)... left/right clamped to x=0\n
    1D horizontal: items at (0,0), (1,0), (2,0)... up/down clamped to y=0\n
    2D:            items at any (x,y), all directions free
    """
    def __init__(self, axis:bool, twodim:bool=False, limit:str|None=None):
        if limit not in ('min', 'max', None):
            raise ValueError(f'{limit} is not a valid limit, must be min, max or None')
        self.axis   = axis
        self.twodim = twodim
        self.limit  = limit

        self.select_callback = None   # (callback, args) fired on any select()
        self.move_callback   = None   # (callback, args) fired on any pointer move

        self.items     = {}   # keys are (x, y)
        self.callbacks = {}   # keys are (x, y), values are (callback, args)
        self.pointer   = (0, 0)

    def set_item(self, position:int|tuple[int,int], item, callback=None, args=None):
        """
        add an item to the menu.
        - 1D: set_item(0, item)          - index along the free axis
        - 2D: set_item((x, y), item)
        - callback: optional function to call on select()
        - args:     optional list of args to pass to the callback
        """
        if isinstance(position, int):
            position = (0, position) if self.axis == axes.VERTICAL else (position, 0)
        self.items[position] = item
        if callback is not None:
            self.callbacks[position] = (callback, args or [])

    def set_select_callback(self, callback, args=None):
        """set a callback to fire whenever select() is called"""
        self.select_callback = (callback, args or [])

    def set_move_callback(self, callback, args=None):
        """set a callback to fire whenever the pointer moves"""
        self.move_callback = (callback, args or [])

    @property
    def selected(self):
        """returns the currently selected item"""
        return self.items.get(self.pointer)
    
    def select(self):
        """call the callback for the currently selected item if there is one"""
        if self.select_callback is not None:
            cb, args = self.select_callback
            cb(*args)
        if self.pointer in self.callbacks:
            cb, args = self.callbacks[self.pointer]
            return cb(*args)

    def _move(self, dx:int, dy:int):
        x, y = self.pointer

        if dy != 0 and (self.axis == axes.VERTICAL or self.twodim):
            y_positions = sorted(set(k[1] for k in self.items if k[0] == x))
            if y_positions:
                if self.twodim and self.axis == axes.HORIZONTAL:
                    # y is the non-free axis in 2D horizontal - apply limit
                    new_y = y + dy
                    if self.limit == 'min':   new_y = max(y_positions[0], new_y)
                    elif self.limit == 'max': new_y = min(y_positions[-1], new_y)
                    else:                     new_y = y_positions[new_y % len(y_positions)]
                else:
                    idx = y_positions.index(y) if y in y_positions else 0
                    new_y = y_positions[(idx + dy) % len(y_positions)]
                y = new_y

        if dx != 0 and (self.axis == axes.HORIZONTAL or self.twodim):
            x_positions = sorted(set(k[0] for k in self.items if k[1] == y))
            if x_positions:
                if self.twodim and self.axis == axes.VERTICAL:
                    # x is the non-free axis in 2D vertical - apply limit
                    new_x = x + dx
                    if self.limit == 'min':   new_x = max(x_positions[0], new_x)
                    elif self.limit == 'max': new_x = min(x_positions[-1], new_x)
                    else:                     new_x = x_positions[new_x % len(x_positions)]
                else:
                    idx = x_positions.index(x) if x in x_positions else 0
                    new_x = x_positions[(idx + dx) % len(x_positions)]
                x = new_x

        self.pointer = (x, y)
        if self.move_callback is not None:
            cb, args = self.move_callback
            cb(*args)

    def up(self):
        """move up (y-1); only moves if axis is vertical or twodim"""
        self._move(0, -1)

    def down(self):
        """move down (y+1); only moves if axis is vertical or twodim"""
        self._move(0, +1)

    def left(self):
        """move left (x-1); only moves if axis is horizontal or twodim"""
        self._move(-1, 0)

    def right(self):
        """move right (x+1); only moves if axis is horizontal or twodim"""
        self._move(+1, 0)

