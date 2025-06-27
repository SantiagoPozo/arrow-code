# Arrow 5: A Spies Game

## Overview

**Arrow** 5 is a solo deduction game where you, a special agent, attempt to uncover the secret code of the Corporation. Through a series of coded attacks, you receive directional hints indicating how close each guess is to the solution. The game is designed to challenge logic and reasoning in a fun, interactive format.


## Tech Stack

- **Backend:** FastAPI, Python, WebSockets
- **Frontend:** React, TypeScript, SASS
- **Database:** TBD (in-memory cache or persistent storage for game sessions)

## Installation

### Prerequisites

- **Python** (version 3.9+ recommended)
- **Node.js** (version 16+ recommended)

### Setup

#### Backend (FastAPI)

1. Clone the repository:
   git clone https://github.com/SantiagoPozo/arrow-code.git
   cd arrow-code
2. Create and activate a virtual environment:
   python3 -m venv env
   source env/bin/activate # For macOS/Linux
   env\Scripts\activate # For Windows
3. Install dependencies:
   pip install fastapi uvicorn
4. Run the FastAPI server from backend/:
   uvicorn main:app --reload

#### Frontend (React + TypeScript with Vite)

The frontend uses [Vite](https://vitejs.dev/) for a fast and modern development environment with React and TypeScript.

##### Setup

1. Navigate to the `frontend` directory:

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
npm install axios
npm run dev
```

## API Endpoints

### REST API

- POST /games → Creates a new game.
- GET /games/{game_id} → Retrieves the current game state.
- POST /games/{game_id}/move → Submits a move.

### WebSocket

- ws://server_address/ws/game/{game_id} → Real-time connection for game updates and moves.

## Deployment

### Backend (Render)

1. Push your `deploy` branch to GitHub:
   ```bash
   git push origin deploy
   ```
2. In Render dashboard, click **New** → **Web Service**, connect your GitHub repo and select the `deploy` branch.
3. Set:
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
4. Add any required environment variables (e.g. `INACTIVITY_HOURS`).
5. Deploy and note the service URL.

### Frontend (GitHub Pages)

1. Switch to `deploy` branch and install `gh-pages`:
   ```bash
   cd frontend
   npm install --save-dev gh-pages
   ```
2. Add to `package.json`:
   ```json
   "homepage": "https://<your-username>.github.io/arrow-code",
   "scripts": {
     "predeploy": "npm run build",
     "deploy": "gh-pages -d dist"
   }
   ```
3. Commit and push `deploy` branch:
   ```bash
   git add package.json
   git commit -m "Add GitHub Pages deploy configuration"
   git push origin deploy
   ```
4. Run deployment:
   ```bash
   npm run deploy
   ```
5. In GitHub repo settings, enable Pages from the `gh-pages` branch (root).

## License

This project is licensed under the GNU General Public License, Version 3, 29 June 2007.
See the [LICENSE](LICENSE) file for details.
