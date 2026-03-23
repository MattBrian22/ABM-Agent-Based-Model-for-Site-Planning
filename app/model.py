from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import ContinuousSpace
import random

class SiteModel(Model): 
    def __init__(self, n_workers, width_meters, height_meters):
        super().__init__() 
        self.num_agents = n_workers
        self.mode = "Profit"  # Default mode
        self.space = ContinuousSpace(width_meters, height_meters, True)
        self.schedule = RandomActivation(self)
        
        # Define a "High Value Zone" (e.g., the Lab Block at Wood Wharf)
        self.lab_zone = {"x": width_meters * 0.8, "y": height_meters * 0.8}
        
        for i in range(self.num_agents):
            a = LabWorker(i, self)
            self.schedule.add(a)
            x = self.random.uniform(0, self.space.width)
            y = self.random.uniform(0, self.space.height)
            self.space.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()

class LabWorker(Agent):
    def step(self):
        # 1. Decide WHERE to go based on the Mode
        if self.model.mode == "Profit":
            # Move toward the Lab Zone (Top Right)
            self.move_toward(self.model.lab_zone["x"], self.model.lab_zone["y"])
        else:
            # Move randomly (Resilience/Wander mode)
            self.wander()

    def move_toward(self, target_x, target_y):
        curr_x, curr_y = self.pos
        # Calculate a small step (1 meter) toward the target
        dx = 1.0 if target_x > curr_x else -1.0
        dy = 1.0 if target_y > curr_y else -1.0
        new_pos = (curr_x + dx, curr_y + dy)
        
        # Safety check: keep agent inside the site bounds
        if 0 < new_pos[0] < self.model.space.width and 0 < new_pos[1] < self.model.space.height:
            self.model.space.move_agent(self, new_pos)

    def wander(self):
        curr_x, curr_y = self.pos
        # Random step between -2 and 2 meters
        new_pos = (
            curr_x + random.uniform(-2, 2),
            curr_y + random.uniform(-2, 2)
        )
        if 0 < new_pos[0] < self.model.space.width and 0 < new_pos[1] < self.model.space.height:
            self.model.space.move_agent(self, new_pos)