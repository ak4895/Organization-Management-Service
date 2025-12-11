from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import db_connection
from app.routes import organizations, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting Organization Management Service...")
    try:
        db_connection.connect()
        print("Database connection established")
        
        # Seed demo data on startup
        print("\nInitializing demo data...")
        from app.seed_data import seed_demo_data
        seed_demo_data()
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
    
    yield
    
    # Shutdown
    print("Shutting down Organization Management Service...")
    db_connection.close()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-tenant Organization Management Service with MongoDB",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


# Include routers
app.include_router(organizations.router)
app.include_router(admin.router)


# Root endpoint
@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML links to API documentation"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Organization Management Service</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 50px;
                max-width: 600px;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .version {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 30px;
            }
            p {
                color: #555;
                margin-bottom: 30px;
                line-height: 1.6;
            }
            .links-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 30px;
            }
            @media (max-width: 600px) {
                .links-grid {
                    grid-template-columns: 1fr;
                }
                .container {
                    padding: 30px;
                }
                h1 {
                    font-size: 1.8em;
                }
            }
            a {
                display: inline-block;
                padding: 15px 25px;
                margin: 10px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: transform 0.3s, box-shadow 0.3s;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            a:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
            }
            .docs-link {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
            }
            .docs-link:hover {
                box-shadow: 0 8px 25px rgba(245, 87, 108, 0.6);
            }
            .redoc-link {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
            }
            .redoc-link:hover {
                box-shadow: 0 8px 25px rgba(79, 172, 254, 0.6);
            }
            .health-link {
                background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                box-shadow: 0 5px 15px rgba(67, 233, 123, 0.4);
            }
            .health-link:hover {
                box-shadow: 0 8px 25px rgba(67, 233, 123, 0.6);
            }
            .admin-link {
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
                box-shadow: 0 5px 15px rgba(250, 112, 154, 0.4);
            }
            .admin-link:hover {
                box-shadow: 0 8px 25px rgba(250, 112, 154, 0.6);
            }
            .grid-item {
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .grid-full {
                grid-column: 1 / -1;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #999;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Organization Management Service</h1>
            <p class="version">v1.0.0</p>
            <p>Multi-tenant backend service for managing organizations with MongoDB</p>
            
            <div class="links-grid">
                <div class="grid-item">
                    <a href="/docs" class="docs-link">📚 Swagger Docs</a>
                </div>
                <div class="grid-item">
                    <a href="/redoc" class="redoc-link">📖 ReDoc</a>
                </div>
                <div class="grid-item">
                    <a href="/admin/login" class="admin-link">🔐 Admin Login</a>
                </div>
                <div class="grid-item">
                    <a href="/health" class="health-link">💚 Health Check</a>
                </div>
            </div>
            
            <div class="footer">
                <p>Click any link above to explore the API</p>
            </div>
        </div>
    </body>
    </html>
    """


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_connection.get_master_db().command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status
    }


# Demo/Sample Data endpoint
@app.post("/demo/create-sample-data", tags=["Demo"])
async def create_sample_data():
    """Create sample organization and admin data for demonstration"""
    from app.services import OrganizationService
    
    try:
        org_service = OrganizationService()
        
        # Check if sample org already exists
        if org_service.organization_exists("Demo Company"):
            return {
                "message": "Sample data already exists",
                "organization_name": "Demo Company",
                "email": "admin@democompany.com",
                "password": "Demo@123456",
                "note": "Use these credentials to login"
            }
        
        # Create sample organization
        org = org_service.create_organization(
            organization_name="Demo Company",
            email="admin@democompany.com",
            password="Demo@123456"
        )
        
        return {
            "message": "Sample data created successfully",
            "organization": {
                "id": str(org.organization_id),
                "name": org.organization_name,
                "collection": org.collection_name,
                "admin_email": org.admin_email
            },
            "credentials": {
                "email": "admin@democompany.com",
                "password": "Demo@123456"
            },
            "next_steps": [
                "Use /admin/login endpoint to get JWT token",
                "Use the token to access protected endpoints",
                "Visit /docs to test all endpoints"
            ]
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to create sample data"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)


# Custom ReDoc endpoint (since automatic one was not working)
@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def redoc_html():
    """ReDoc API documentation"""
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <title>ReDoc - Organization Management Service</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
          body {
            margin: 0;
            padding: 0;
          }
        </style>
      </head>
      <body>
        <redoc spec-url='/openapi.json'></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"> </script>
      </body>
    </html>
    """
