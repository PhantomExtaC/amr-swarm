class WarehouseMap:
    def __init__(self, width=100, height=100):
        self.width = width
        self.height = height
        self.obstacles = set()
        self.dead_zones = set()
        self.charging_stations = [(0, 0), (0, 99), (99, 0), (99, 99)]
        
        self._generate_shelves()
        self._generate_dead_zones()

    def _generate_shelves(self):
        """
        Generates 10 horizontal shelf rows across the 100x100 grid.
        Shelves span X from 10 to 90.
        Corridors at X < 10 and X > 90 allow bots to move between aisles.
        """
        rows = [10, 18, 26, 34, 42, 50, 58, 66, 74, 82]
        for y in rows:
            for x in range(10, 91):
                self.obstacles.add((x, y))

    def _generate_dead_zones(self):
        """
        Defines central warehouse regions where main Wi-Fi fails.
        Bots must rely on local mesh gossip in these zones.
        """
        for x in range(30, 70):
            for y in range(30, 70):
                if (x, y) not in self.obstacles:
                    self.dead_zones.add((x, y))

    def is_valid(self, x: int, y: int) -> bool:
        """Returns True if the coordinate is within grid bounds and not an obstacle."""
        return 0 <= x < self.width and 0 <= y < self.height and (x, y) not in self.obstacles

    def is_dead_zone(self, x: int, y: int) -> bool:
        """Returns True if the coordinate is inside a Wi-Fi dead spot."""
        return (x, y) in self.dead_zones