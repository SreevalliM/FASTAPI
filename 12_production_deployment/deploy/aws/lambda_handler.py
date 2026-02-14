# AWS Lambda with Mangum adapter
# This allows running FastAPI on AWS Lambda

# Install: pip install mangum

from mangum import Mangum
from 12_production_api import app

# Create Lambda handler
handler = Mangum(app, lifespan="off")

# Deploy using AWS SAM or Serverless Framework
