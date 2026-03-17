from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .model import SiteModel
from .models import SimulationRun, AgentPosition

app = FastAPI(title="ABM Site Planning API")

# This creates the tables in Postgres automatically when you start the server
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"status": "ABM Backend is Online"}

@app.post("/run-simulation/{n_workers}")
def run_simulation(n_workers: int, db: Session = Depends(get_db)):
    # 1. Initialize the Mesa Model
    model = SiteModel(n_workers=n_workers, width=100, height=100)
    
    # 2. Log the Run in the Database
    new_run = SimulationRun(layout_name="Standard_Lab", agent_count=n_workers)
    db.add(new_run)
    db.commit()
    db.refresh(new_run)
    
    # 3. Run for 10 steps and save positions
    for step in range(10):
        model.step()
        for agent in model.schedule.agents:
            pos = AgentPosition(
                run_id=new_run.id,
                step_number=step,
                agent_id=agent.unique_id,
                x=float(agent.pos[0]),
                y=float(agent.pos[1])
            )
            db.add(pos)
    
    db.commit()
    return {"message": f"Simulation {new_run.id} complete", "steps_saved": 10}