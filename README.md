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

(Currently for local development; deployment instructions will be defined as the project evolves.)

## License

This project is licensed under the GNU General Public License, Version 3, 29 June 2007.
See the [LICENSE](LICENSE) file for details.
