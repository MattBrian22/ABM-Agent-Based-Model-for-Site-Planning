from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .model import SiteModel
from .models import SimulationRun, AgentPosition
# Add these to the top of app/main.py
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

templates = Jinja2Templates(directory="templates")

app = FastAPI(title="ABM Site Planning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows the dashboard to talk to the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # 1. Initialize
    model = SiteModel(n_workers=n_workers, width_meters=width, height_meters=height)
    
    # 2. Log the Run
    layout_desc = f"Site_{width}x{height}"
    new_run = SimulationRun(layout_name=layout_desc, agent_count=n_workers)
    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    # 3. 🔥 THE MISSING STEP: Run the agents and save their paths!
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
    
    # 4. Finalize
    db.commit()

    # 5. 🔥 THE MISSING RETURN: Send the data back to the Dashboard
    return {
        "message": "Simulation complete",
        "run_id": new_run.id,
        "total_steps": steps
    }