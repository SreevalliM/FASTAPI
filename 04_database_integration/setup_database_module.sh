#!/bin/bash
# Setup script for Database Integration Module

echo "🚀 Setting up Database Integration Module"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "fastapi-env" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found.${NC}"
    echo "Creating virtual environment..."
    python3 -m venv fastapi-env
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source fastapi-env/bin/activate

# Install dependencies
echo ""
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt

# Check installations
echo ""
echo -e "${BLUE}🔍 Verifying installations...${NC}"

python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" 2>/dev/null || echo "❌ FastAPI not installed"
python -c "import sqlmodel; print('✅ SQLModel:', sqlmodel.__version__)" 2>/dev/null || echo "❌ SQLModel not installed"
python -c "import alembic; print('✅ Alembic:', alembic.__version__)" 2>/dev/null || echo "❌ Alembic not installed"

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}📚 Next steps:${NC}"
echo "1. Review the tutorial: 04_DATABASE_INTEGRATION_TUTORIAL.md"
echo "2. Run the in-memory API: python 04_book_api_memory.py"
echo "3. Try SQLite version: python 05_book_api_sqlite.py"
echo "4. Complete exercises in: database_exercises.py"
echo ""
echo -e "${YELLOW}💡 Quick Reference: DATABASE_QUICK_REFERENCE.md${NC}"
