"""Main application modeule for the AdventureWorks API.

This module initializes the FastAPI application and includes all route handlers.
"""

from fastapi import FastAPI
from src.api.routes import products


# Create the FastAPI application instance
app = FastAPI(
    title="AdventureWorks API",
    description="API for managing AdventureWorks product catalog",
    version="1.0.0",
)

# Include our product routes
app.include_router(products.router)
