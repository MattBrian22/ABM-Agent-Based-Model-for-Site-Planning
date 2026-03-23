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
import os
from dotenv import load_dotenv
from fastapi import Request

load_dotenv()

# 1. Fetch it (Make sure this matches your .env file exactly!)
MAPBOX_TOKEN = os.getenv("Mapbox_TOKEN") # Matches your .env exactly

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
    # 2. Use the SAME variable name here
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "mapbox_token": MAPBOX_TOKEN} 
    )

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

# 1. Global State
active_simulation = {"model": None}

@app.post("/run-simulation/")
def run_simulation(n_workers: int, width: int = 300, height: int = 200, db: Session = Depends(get_db)):
    try:
        # 1. Initialize the Model (Ensure this name matches model.py exactly!)
        # If you renamed it to WoodWharfModel, change it here!
        model = SiteModel(n_workers=n_workers, width_meters=width, height_meters=height)
        active_simulation["model"] = model

        # 2. Create the Run record
        new_run = SimulationRun(layout_name=f"WoodWharf_{width}x{height}", agent_count=n_workers)
        db.add(new_run)
        db.commit()
        db.refresh(new_run)

        # 3. Run and Collect Data in a List (Faster & Safer)
        positions_to_save = []
        for step in range(50):
            model.step()
            for agent in model.schedule.agents:
                positions_to_save.append(
                    AgentPosition(
                        run_id=new_run.id,
                        step_number=step,
                        agent_id=agent.unique_id,
                        x=float(agent.pos[0]),
                        y=float(agent.pos[1])
                    )
                )
        
        # 4. Bulk Save (Prevents the "Internal Server Error" timeout)
        db.bulk_save_objects(positions_to_save)
        db.commit()

        return {"status": "success", "run_id": new_run.id}

    except Exception as e:
        # This will print the REAL error in your Docker/Terminal console
        print(f"CRITICAL ERROR: {str(e)}")
        return {"status": "error", "message": str(e)}

    return {
        "message": "Simulation complete",
        "run_id": new_run.id,
        "total_points": len(all_positions)
    }

@app.post("/update_mode")
async def update_mode(data: dict):
    model = active_simulation.get("model")
    if model:
        model.mode = data['mode'] # This now affects the LIVE model
        print(f"ALARM: Global Logic Shifted to {model.mode}")
        return {"status": "success", "mode": model.mode}
    return {"status": "error", "message": "No active model found"}