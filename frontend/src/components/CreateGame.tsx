import React, { FormEvent } from "react";
import axios from "axios";
import Avatar from "./GameCreate/Avatars";
import Difficulty from "./GameCreate/Difficulty";
import Mode from "./GameCreate/Mode";
import SwitchColorScheme from "./SwitchColorScheme";

// Actualizamos el type de props
type CreateGameProps = {
  onGameCreated: (id: string) => void;
  playerName: string;
  setPlayerName: React.Dispatch<React.SetStateAction<string>>;
  playerAvatar: "she" | "he" | "they";
  setPlayerAvatar: React.Dispatch<React.SetStateAction<"she" | "he" | "they">>;
  gameDifficulty: string;
  setGameDifficulty: React.Dispatch<React.SetStateAction<string>>;
  obfuscation: boolean;
  setObfuscation: React.Dispatch<React.SetStateAction<boolean>>;
};

const CreateGame: React.FC<CreateGameProps> = ({
  onGameCreated,
  playerName,
  setPlayerName,
  playerAvatar,
  setPlayerAvatar,
  gameDifficulty,
  setGameDifficulty,
  obfuscation,
  setObfuscation,
}) => {
  const handleCreateGame = async (e?: FormEvent) => {
    e?.preventDefault();
    if (!playerName.trim()) return;
    try {
      // Guarda en localStorage la información actual (solo en CreateGame)
      localStorage.setItem("activePlayer", playerName);

      const res = await axios.post("http://127.0.0.1:8000/games", {
        playerName,
        difficulty: gameDifficulty,
        obfuscation,
      });

      // Escritura en localStorage para mantener la partida activa
      localStorage.setItem("isActiveGame", "true");
      localStorage.setItem("activeGameId", res.data);
      const activeGameSetup = {
        playerAvatar: playerAvatar,
        gameDifficulty: gameDifficulty,
        obfuscation: obfuscation,
      };
      localStorage.setItem("activeGameSetup", JSON.stringify(activeGameSetup));

      onGameCreated(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div id="create-game">
      <div id="title">
        <h1>Arr👁w Code</h1>
        <SwitchColorScheme />
      </div>
      <h2>A Spies Game of Deduction and Deception</h2>
      <form onSubmit={handleCreateGame}>
        <Avatar
          selectedAvatar={playerAvatar}
          onSelectAvatar={setPlayerAvatar}
        />
        <Difficulty
          selectedDifficulty={gameDifficulty}
          setSelectedDifficulty={setGameDifficulty}
          playerAvatar={playerAvatar}
        />

        <Mode
          obfuscation={obfuscation}
          setObfuscation={setObfuscation}
          playerAvatar={playerAvatar}
        />
        <input
          type="text"
          id="player-name"
          name="player-name"
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          placeholder="Enter your name"
          autoFocus
        />
        <button
          type="submit"
          disabled={!playerName.trim()}
          className={playerAvatar}
        >
          Create Game
        </button>
      </form>
    </div>
  );
};

export default CreateGame;
