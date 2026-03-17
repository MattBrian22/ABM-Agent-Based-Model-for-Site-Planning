from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    layout_name = Column(String)
    agent_count = Column(Integer)

class AgentPosition(Base):
    __tablename__ = "agent_positions"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("simulation_runs.id"))
    step_number = Column(Integer)
    agent_id = Column(Integer)
    x = Column(Float)
    y = Column(Float)