import uuid
from typing import List, Tuple, Dict
from datetime import datetime, timedelta, timezone
from pydantic import Field, BaseModel
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from random import sample
from constants import *
import asyncio



origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

games = {}

class Game(BaseModel):
    id: str
    secret: str  
    difficulty: str
    obfuscation: bool
    solved: bool = False  # Track if the game has been solved
    attempts: List[str] = Field(default_factory=list)
    responses: List[str] = Field(default_factory=list)
    clues: Dict[Tuple[int, int], Dict[str, str]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
# Helper function: close games that have been inactive for more than INACTIVITY_HOURS.
def cleanup_old_games():
    now = datetime.now(timezone.utc)
    threshold = timedelta(hours=INACTIVITY_HOURS)
    for game in games.values():
        # Use last_updated to determine inactivity.
        if not game.solved and (now - game.last_updated) > threshold:
            game.solved = True
            print(f"Game {game.id} closed due to inactivity (open >{INACTIVITY_HOURS}h).")

# Background function that waits INACTIVITY_HOURS before closing the game.
async def cleanup_after_inactivity(game_id: str, scheduled_last_updated: datetime):
    # Wait INACTIVITY_HOURS hours (in production consider a more robust mechanism)
    await asyncio.sleep(INACTIVITY_HOURS * 3600)
    # After waiting, if the game is still in memory...
    game = games.get(game_id)
    if game and not game.solved:
        # Check if the last update timestamp matches the scheduled timestamp.
        if game.last_updated == scheduled_last_updated:
            game.solved = True
            print(f"Game {game.id} closed after {INACTIVITY_HOURS} hours of inactivity.")

@app.get("/")
async def root():
    cleanup_old_games() 
    return {"message": "Hello, Arrow 5!"}

class GameCreateRequest(BaseModel):
    playerName: str
    difficulty: str
    obfuscation: bool

@app.post("/games")
async def create_game(data: GameCreateRequest, background_tasks: BackgroundTasks):
    cleanup_old_games() 
    game_id = str(uuid.uuid4())
    secret = generateCode(CODE_LENGTH, data.obfuscation)
    game = Game(
        id=game_id, 
        secret=secret,
        difficulty=data.difficulty,
        obfuscation=data.obfuscation,
        solved=False,  
    )
    games[game_id] = game
    print("\n\nGame created:", game_id)
    print("secret", game.secret)
    print("game", game)
    # Programa la tarea en segundo plano utilizando el valor actual de last_updated.
    background_tasks.add_task(cleanup_after_inactivity, game_id, game.last_updated)
    return game.id

@app.get("/games/{game_id}")
async def get_game(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    game = games[game_id]
    clues_serializable = { f"{key[0]}_{key[1]}": value for key, value in game.clues.items() }
    return {
        "id": game.id,
        "attempts": game.attempts,
        "responses": game.responses,
        "clues": clues_serializable,
        "solved": game.solved
    }

class AttemptRequest(BaseModel):
    attempt: str

@app.post("/games/{game_id}/attempt")
async def submit_attempt(game_id: str, data: AttemptRequest, background_tasks: BackgroundTasks):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    game = games[game_id]
    try:
        result, is_solved = evaluate(game.secret, data.attempt, game.obfuscation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    game.attempts.append(data.attempt)
    game.responses.append(result)
    
    # Actualiza el timestamp al hacer un intento.
    game.last_updated = datetime.now(timezone.utc)
    
    if is_solved:
        game.solved = True
    else:
        # Registra una nueva tarea de limpieza con el nuevo last_updated.
        background_tasks.add_task(cleanup_after_inactivity, game_id, game.last_updated)
        
    print(game.secret)
    return {"result": result, "solved": is_solved}

@app.get("/games/{game_id}/clue")
async def get_clue(game_id: str, attemptIndex: int, tileIndex: int, background_tasks: BackgroundTasks):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    game = games[game_id]
    
    if attemptIndex < 0 or attemptIndex >= len(game.attempts):
        raise HTTPException(status_code=400, detail="Invalid attempt index")
    
    if tileIndex < 0 or tileIndex >= CODE_LENGTH:
        raise HTTPException(status_code=400, detail="Invalid tile index")
    
    if game.difficulty == "0":
        raise HTTPException(status_code=400, detail="No clues allowed for this difficulty")
    elif game.difficulty == "1":
        if game.clues:  
            raise HTTPException(status_code=400, detail="Only one clue allowed for this game")
    elif game.difficulty == "n":
        clues_for_attempt = [k for k in game.clues.keys() if k[0] == attemptIndex]
        if clues_for_attempt:
            raise HTTPException(status_code=400, detail="Only one clue allowed per attempt")

    key: Tuple[int, int] = (attemptIndex, tileIndex)
    
    if key in game.clues:
        raise HTTPException(
            status_code=400,
            detail="Clue for this attempt and tile has already been requested"
        )
    try:
        clue_str = clue(game.secret, game.attempts[attemptIndex], tileIndex)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    game.clues[key] = {"result": clue_str}
    
    # Actualiza la marca de tiempo al solicitar una pista.
    game.last_updated = datetime.now(timezone.utc)
    background_tasks.add_task(cleanup_after_inactivity, game_id, game.last_updated)
    
    print(game.clues)
    return {"clue": clue_str}

def generateCode(k: int, obfuscation: bool = False) -> str:
    if obfuscation:
        code = sample(ALPH[0:12], k)
    else:
        code = sample(ALPH[0:11], k)
    return "".join(code)

def evaluate(secret: str, attempt: str, obfuscation: bool = False) -> Tuple[str, bool]:
    if len(attempt) < CODE_LENGTH: 
        raise ValueError("Attempt needs to be 5 characters long")
    if len(attempt) == CODE_LENGTH and len(set(attempt)) < CODE_LENGTH:
        raise ValueError("Attempt needs to have 5 different characters")
    
    if secret == attempt:
        return ("=" * CODE_LENGTH, True)
    
    result = ""
    
    for i, a in enumerate(attempt):
        if obfuscation:
            if a == 'y':
                continue
            if a == 'x':
                result += "="
                continue
        
        if a in set(secret):
            if a == secret[i]:
                result += "="
            else:
                index = secret.index(a)
                if index < i:
                    result += "<"
                else:
                    result += ">"
    
    return (result, False)

def clue(secret: str, attempt: str, position: int) -> str:
    print("\033[32m\n\nClue requested\033[0m")
    print("secret   ", "attempt  ", "position ")
    print(f"{secret:10}{attempt:10}{position}")

    result = "absent"
    symbol = attempt[position]
    if symbol in secret:
        real_position = secret.index(symbol)
        print(f"  real position: {real_position}")
        if real_position == position:
            result = "steady"
        elif real_position < position:
            result = "left"
        else:
            result = "right"
    return result

