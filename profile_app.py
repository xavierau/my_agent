import cProfile
import pstats_analysis
import uvicorn

# Import your FastAPI app instance
from server import app

if __name__ == "__main__":
    cProfile.run(
        'uvicorn.run(app, host="127.0.0.1", port=8000)',
        'profile_output.stats'
    )


