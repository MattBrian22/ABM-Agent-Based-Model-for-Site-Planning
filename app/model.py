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
        # 1. Propose a move (Wander - Level 1)
        new_x = self.pos[0] + self.random.uniform(-2, 2)
        new_y = self.pos[1] + self.random.uniform(-2, 2)
        
        # 2. LEVEL 0: SENSE (Collision Detection)
        # Example: Defining a skyscraper footprint between X: 140-160 and Y: 90-110
        is_collision = (140 <= new_x <= 160) and (90 <= new_y <= 110)
        
        # 3. ACT (Subsumption)
        if not is_collision:
            # Move is clear, proceed with Wander
            self.model.space.move_agent(self, (new_x, new_y))
        else:
            # Move is BLOCKED. Level 0 suppresses Level 1.
            # The agent stays put or "bounces"
            pass