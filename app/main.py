from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .model import SiteModel
from .models import SimulationRun, AgentPosition
# Add these to the top of app/main.py
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")



app = FastAPI(title="ABM Site Planning API")

# Automatically create tables in Postgres
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"status": "ABM Backend is Online"}

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/simulation-results/{run_id}")
def get_results(run_id: int, db: Session = Depends(get_db)):
    results = db.query(AgentPosition).filter(AgentPosition.run_id == run_id).all()
    if not results:
        return {"error": "No results found for this Run ID"}
    
    return {
        "run_id": run_id,
        "total_points": len(results),
        "data": [
            {"step": p.step_number, "agent": p.agent_id, "x": p.x, "y": p.y} 
            for p in results
        ]
    }

@app.post("/run-simulation/")
def run_simulation(
    n_workers: int, 
    width: int = 300, 
    height: int = 200, 
    db: Session = Depends(get_db)
):
    # 1. Initialize the Mesa Model with the Dynamic Dimensions
    # Ensure your SiteModel in model.py accepts width_meters/height_meters!
    model = SiteModel(n_workers=n_workers, width_meters=width, height_meters=height)
    
    # 2. Log the Run (using the custom width/height in the name)
    layout_desc = f"Site_{width}x{height}"
    new_run = SimulationRun(layout_name=layout_desc, agent_count=n_workers)
    db.add(new_run)
    db.commit()
    db.refresh(new_run)
    
    # 3. Run for 50 steps (let's give them more time to move!)
    steps = 50
    for step in range(steps):
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
    return {
        "message": f"Simulation {new_run.id} complete", 
        "run_id": new_run.id,
        "dimensions": f"{width}m x {height}m",
        "steps_saved": steps
    }