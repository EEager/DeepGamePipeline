class SpatialHashGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}

    def _cell_key(self, pos):
        return (int(pos.x) // self.cell_size, int(pos.y) // self.cell_size)

    def add(self, obj):
        key = self._cell_key(obj.position)
        self.grid.setdefault(key, set()).add(obj)

    def remove(self, obj):
        key = self._cell_key(obj.position)
        if key in self.grid:
            self.grid[key].discard(obj)

    def move(self, obj, old_pos):
        old_key = self._cell_key(old_pos)
        new_key = self._cell_key(obj.position)
        if old_key != new_key:
            self.remove(obj)
            self.add(obj)

    def get_nearby(self, pos, radius=1):
        cx, cy = self._cell_key(pos)
        result = set()
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                key = (cx+dx, cy+dy)
                result.update(self.grid.get(key, set()))
        return result 