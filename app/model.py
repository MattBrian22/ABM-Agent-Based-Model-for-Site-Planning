from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace

# app/model.py

class SiteModel(Model): 
    # Change width -> width_meters and height -> height_meters
    def __init__(self, n_workers, width_meters, height_meters):
        super().__init__() 
        self.num_agents = n_workers
        # Use the new names here too
        self.space = ContinuousSpace(width_meters, height_meters, True)
        self.schedule = RandomActivation(self)
        
        for i in range(self.num_agents):
            a = LabWorker(i, self)
            self.schedule.add(a)
            x = self.random.uniform(0, self.space.width)
            y = self.random.uniform(0, self.space.height)
            self.space.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()

# Conceptual look at the "Geo-Logic"
class UrbanModel(Model):
    def __init__(self, geojson_site_plan, width_meters=300, height_meters=200):
        # The 'site plan' is now a real map layout
        self.space = ContinuousSpace(width_meters, height_meters, torus=False)
        self.obstacles = self.load_polygons(geojson_site_plan) 
        # Now an obstacle can be a real building footprint (in meters)
        # Example: A 20m x 40m Lab Block
        self.obstacles = [
            [50, 50, 70, 90], 
        ]
        
    def calculate_happiness(self, agent):
        # Logic for the "Happiness Utility" based on shadow patterns
        sunlight = self.get_sunlight_exposure(agent.pos)
        return sunlight * 0.8 + agent.proximity_to_transit * 0.2
class LabWorker(Agent):
    def step(self):
        # 1. Calculate a potential move
        dx = self.random.uniform(-5, 5)
        dy = self.random.uniform(-5, 5)
        new_pos = (self.pos[0] + dx, self.pos[1] + dy)

        # 2. THE OBSTACLE: Let's define a building at x(120-180), y(80-120)
        # Check if new_pos is inside the "Building"
        if 120 <= new_pos[0] <= 180 and 80 <= new_pos[1] <= 120:
            # COLLISION! The agent "bumps" into the wall and stays put
            return 
        
        # 3. Only move if the path is clear
        # Also ensure they don't walk off the site boundaries
        if (0 <= new_pos[0] <= self.model.space.width and 
            0 <= new_pos[1] <= self.model.space.height):
            self.model.space.move_agent(self, new_pos)