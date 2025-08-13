# TermoApp Docker Deployment Script for Windows
# Usage: .\deploy.ps1 [build|start|stop|restart|logs|clean]

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if .env file exists
function Test-EnvFile {
    if (-not (Test-Path ".env")) {
        Write-Warning ".env file not found. Creating from env.example..."
        if (Test-Path "env.example") {
            Copy-Item "env.example" ".env"
            Write-Success "Created .env file from env.example"
            Write-Warning "Please edit .env file with your actual configuration"
        } else {
            Write-Error "env.example not found. Please create a .env file manually"
            exit 1
        }
    }
}

# Build the Docker image
function Build-Image {
    Write-Status "Building TermoApp Docker image..."
    docker-compose build
    Write-Success "Docker image built successfully"
}

# Start the application
function Start-App {
    Write-Status "Starting TermoApp..."
    Test-EnvFile
    docker-compose up -d
    Write-Success "TermoApp started successfully"
    Write-Status "Application is running at http://localhost:5000"
}

# Stop the application
function Stop-App {
    Write-Status "Stopping TermoApp..."
    docker-compose down
    Write-Success "TermoApp stopped successfully"
}

# Restart the application
function Restart-App {
    Write-Status "Restarting TermoApp..."
    docker-compose restart
    Write-Success "TermoApp restarted successfully"
}

# Show logs
function Show-Logs {
    Write-Status "Showing TermoApp logs..."
    docker-compose logs -f
}

# Clean up containers and images
function Clean-Resources {
    Write-Warning "This will remove all containers and images. Are you sure? (y/N)"
    $response = Read-Host
    if ($response -match "^[yY]$|^[yY][eE][sS]$") {
        Write-Status "Cleaning up Docker resources..."
        docker-compose down -v --rmi all
        docker system prune -f
        Write-Success "Cleanup completed"
    } else {
        Write-Status "Cleanup cancelled"
    }
}

# Show status
function Show-Status {
    Write-Status "TermoApp status:"
    docker-compose ps
}

# Show help
function Show-Help {
    Write-Host "TermoApp Docker Deployment Script for Windows" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [COMMAND]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  build     Build the Docker image"
    Write-Host "  start     Start the application"
    Write-Host "  stop      Stop the application"
    Write-Host "  restart   Restart the application"
    Write-Host "  logs      Show application logs"
    Write-Host "  status    Show application status"
    Write-Host "  clean     Clean up Docker resources"
    Write-Host "  help      Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\deploy.ps1 build    # Build the image"
    Write-Host "  .\deploy.ps1 start    # Start the application"
    Write-Host "  .\deploy.ps1 logs     # View logs"
}

# Main script logic
switch ($Command.ToLower()) {
    "build" {
        Build-Image
    }
    "start" {
        Start-App
    }
    "stop" {
        Stop-App
    }
    "restart" {
        Restart-App
    }
    "logs" {
        Show-Logs
    }
    "status" {
        Show-Status
    }
    "clean" {
        Clean-Resources
    }
    "help" {
        Show-Help
    }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
        exit 1
    }
} 