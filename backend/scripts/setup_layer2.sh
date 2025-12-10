#!/bin/bash
# Layer 2 Setup Script
# This script sets up the complete Layer 2 environment

set -e  # Exit on error

echo "=================================="
echo "Layer 2 Setup Script"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the backend directory${NC}"
    echo "   cd backend && bash scripts/setup_layer2.sh"
    exit 1
fi

echo -e "${GREEN}Step 1: Starting Docker containers...${NC}"
docker-compose up -d
echo "Waiting for databases to be ready (15 seconds)..."
sleep 15

echo ""
echo -e "${GREEN}Step 2: Installing Python dependencies...${NC}"
pip install -r requirements.txt

echo ""
echo -e "${GREEN}Step 3: Downloading spaCy model...${NC}"
python -m spacy download en_core_web_sm || true

echo ""
echo -e "${GREEN}Step 4: Testing database connections...${NC}"
python scripts/init_databases.py

echo ""
echo -e "${GREEN}Step 5: Running Alembic migrations...${NC}"
alembic upgrade head

echo ""
echo -e "${GREEN}Step 6: Verifying setup...${NC}"
python scripts/init_databases.py

echo ""
echo "=================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start the FastAPI server:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. Access the API docs:"
echo "   http://localhost:8000/api/docs"
echo ""
echo "3. Access database management UIs:"
echo "   - pgAdmin:        http://localhost:5050"
echo "   - Mongo Express:  http://localhost:8081"
echo "   - Redis Commander: http://localhost:8082"
echo ""
