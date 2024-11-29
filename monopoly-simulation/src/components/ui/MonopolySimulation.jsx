import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../ui/card';
import { DollarSign, User, Building2 } from 'lucide-react';

const API_URL = 'http://157.230.229.122:5000/api';

const PROPERTY_DETAILS = {
  1: { name: 'Mediterranean Ave', color: 'brown', price: 60 },
  3: { name: 'Baltic Ave', color: 'brown', price: 60 },
  6: { name: 'Oriental Ave', color: 'light_blue', price: 100 },
  8: { name: 'Vermont Ave', color: 'light_blue', price: 100 },
  9: { name: 'Connecticut Ave', color: 'light_blue', price: 120 },
  11: { name: 'St. Charles Place', color: 'pink', price: 140 },
  13: { name: 'States Ave', color: 'pink', price: 140 },
  14: { name: 'Virginia Ave', color: 'pink', price: 160 },
  16: { name: 'St. James Place', color: 'orange', price: 180 },
  18: { name: 'Tennessee Ave', color: 'orange', price: 180 },
  19: { name: 'New York Ave', color: 'orange', price: 200 },
  21: { name: 'Kentucky Ave', color: 'red', price: 220 },
  23: { name: 'Indiana Ave', color: 'red', price: 220 },
  24: { name: 'Illinois Ave', color: 'red', price: 240 },
  26: { name: 'Atlantic Ave', color: 'yellow', price: 260 },
  27: { name: 'Ventnor Ave', color: 'yellow', price: 260 },
  29: { name: 'Marvin Gardens', color: 'yellow', price: 280 },
  31: { name: 'Pacific Ave', color: 'green', price: 300 },
  32: { name: 'North Carolina Ave', color: 'green', price: 300 },
  34: { name: 'Pennsylvania Ave', color: 'green', price: 320 },
  37: { name: 'Park Place', color: 'dark_blue', price: 350 },
  39: { name: 'Boardwalk', color: 'dark_blue', price: 400 }
};

const PROPERTY_COLORS = {
  brown: 'bg-yellow-900',
  light_blue: 'bg-blue-300',
  pink: 'bg-pink-400',
  orange: 'bg-orange-500',
  red: 'bg-red-600',
  yellow: 'bg-yellow-400',
  green: 'bg-green-600',
  dark_blue: 'bg-blue-800',
};

const PLAYER_COLORS = [
  'text-red-500',
  'text-blue-500',
  'text-green-500',
  'text-purple-500'
];

const MonopolySimulation = () => {
  const [gameState, setGameState] = useState({
    players: [],
    gameLog: [],
    isRunning: false,
    aiReasoningLog: []
  });

  const startGame = async () => {
    try {
      const response = await fetch(`${API_URL}/start`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchGameState();
      }
    } catch (error) {
      console.error('Error starting game:', error);
    }
  };

  const stopGame = async () => {
    try {
      const response = await fetch(`${API_URL}/stop`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchGameState();
      }
    } catch (error) {
      console.error('Error stopping game:', error);
    }
  };

  const fetchGameState = async () => {
    try {
      const response = await fetch(`${API_URL}/state`);
      const data = await response.json();
      setGameState(prevState => ({
        ...prevState,
        players: data.players,
        gameLog: data.game_log,
        isRunning: data.is_running,
        aiReasoningLog: [...(prevState.aiReasoningLog || []), ...data.ai_log]
      }));
    } catch (error) {
      console.error('Error fetching game state:', error);
    }
  };

  const pollUpdates = useCallback(async () => {
    if (gameState.isRunning) {
      try {
        const response = await fetch(`${API_URL}/updates`);
        const data = await response.json();
        if (data.update) {
          setGameState(prevState => ({
            ...prevState,
            aiReasoningLog: [...prevState.aiReasoningLog, ...data.ai_log]
          }));
          fetchGameState();
        }
      } catch (error) {
        console.error('Error polling updates:', error);
      }
    }
  }, [gameState.isRunning]);

  useEffect(() => {
    fetchGameState();
    const interval = setInterval(pollUpdates, 1500);
    return () => clearInterval(interval);
  }, [pollUpdates]);

  const renderPlayer = (playerIndex, position) => {
    if (gameState.players[playerIndex]?.position === position) {
      return (
        <User 
          key={playerIndex}
          className={`${PLAYER_COLORS[playerIndex]} h-4 w-4 absolute 
            ${playerIndex % 2 === 0 ? 'left-1' : 'right-1'}
            ${playerIndex < 2 ? 'top-1' : 'bottom-1'}`}
        />
      );
    }
    return null;
  };

  const renderPropertyOwnership = (position) => {
    const property = PROPERTY_DETAILS[position];
    if (!property) return null;

    const owner = gameState.players.find(player => 
      player.properties.some(prop => prop.position === position)
    );

    if (owner) {
      const playerIndex = gameState.players.indexOf(owner);
      return (
        <Building2 
          className={`${PLAYER_COLORS[playerIndex]} h-4 w-4 absolute bottom-1 left-1/2 transform -translate-x-1/2`}
        />
      );
    }
    return null;
  };

  const renderSpace = (position) => {
    const propertyDetails = PROPERTY_DETAILS[position];
    const isCorner = [0, 10, 20, 30].includes(position);
    const isRailroad = [5, 15, 25, 35].includes(position);
    const isUtility = [12, 28].includes(position);
    const isTax = [4, 38].includes(position);
    const isChance = [7, 22, 36].includes(position);
    const isCommunityChest = [2, 17, 33].includes(position);

    return (
      <div className="relative h-16 w-full border border-gray-300 p-1 text-xs">
        {propertyDetails && (
          <>
            <div className={`h-2 ${PROPERTY_COLORS[propertyDetails.color]} w-full`} />
            <div className="mt-1 font-semibold truncate">{propertyDetails.name}</div>
            <div className="text-gray-600">${propertyDetails.price}</div>
          </>
        )}
        {isCorner && (
          <div className="font-bold flex items-center justify-center h-full">
            {position === 0 && "GO"}
            {position === 10 && "JAIL"}
            {position === 20 && "FREE PARKING"}
            {position === 30 && "GO TO JAIL"}
          </div>
        )}
        {isRailroad && (
          <div className="text-center mt-2">
            <div className="font-semibold">Railroad</div>
            <div className="text-gray-600">$200</div>
          </div>
        )}
        {isUtility && (
          <div className="text-center mt-2">
            <div className="font-semibold">
              {position === 12 ? "Electric Co." : "Water Works"}
            </div>
            <div className="text-gray-600">$150</div>
          </div>
        )}
        {isTax && (
          <div className="text-center mt-2">
            <div className="font-semibold">
              {position === 4 ? "Income Tax" : "Luxury Tax"}
            </div>
            <div className="text-gray-600">
              ${position === 4 ? "200" : "100"}
            </div>
          </div>
        )}
        {(isChance || isCommunityChest) && (
          <div className="text-center mt-2 font-semibold">
            {isChance ? "Chance" : "Community Chest"}
          </div>
        )}
        
        <div className="absolute top-0 left-0 w-full h-full">
          {gameState.players.map((_, idx) => renderPlayer(idx, position))}
          {renderPropertyOwnership(position)}
        </div>
      </div>
    );
  };

  const renderBoard = () => {
    const bottomRow = [...Array(11)].map((_, i) => (
      <div key={`bottom-${i}`} className="w-16">
        {renderSpace(10-i)}
      </div>
    ));

    const rightColumn = [...Array(9)].map((_, i) => (
      <div key={`left-${i}`} className="h-16">
        {renderSpace(31 + i)}
      </div>
    ));

    const topRow = [...Array(11)].map((_, i) => (
      <div key={`top-${i}`} className="w-16">
        {renderSpace(20 + i)}
      </div>
    ));

    const leftColumn = [...Array(9)].map((_, i) => (
      <div key={`right-${i}`} className="h-16">
        {renderSpace(19 - i)}
      </div>
    ));

    return (
      <div className="relative w-fit">
        <div className="flex">
          {topRow}
        </div>
        <div className="flex">
          <div className="flex flex-col">
            {leftColumn}
          </div>
          <div className="flex-1 bg-green-50 p-4 w-[576px] h-[384px] flex items-center justify-center">
            <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="text-4xl font-bold text-green-800 rotate-45">
                MONOPOLY
              </div>
              <div className="mt-8 text-center text-sm text-green-700">
                {gameState.isRunning ? "Game in progress..." : "Press Start to begin"}
              </div>
            </div>
          </div>
          <div className="flex flex-col">
            {rightColumn}
          </div>
        </div>
        <div className="flex">
          {bottomRow}
        </div>
      </div>
    );
  };

  const renderPlayerStats = () => (
    <div className="grid grid-cols-2 gap-6 mt-4">
      {gameState.players.map((player, idx) => (
        <Card key={idx} className="p-6">
          <div className={`font-bold ${PLAYER_COLORS[idx]} flex items-center gap-2`}>
            <User className="h-5 w-5" />
            {player.name}
          </div>
          <div className="flex items-center gap-1 mt-4">
            <DollarSign className="h-4 w-4" />
            {player.money}
          </div>
          <div className="mt-4 text-sm space-y-2">
            <div>Position: {player.position}</div>
            <div>Properties:</div>
            <div className="pl-3 text-xs space-y-1">
              {player.properties.map((prop, i) => (
                <div key={i} className="text-gray-600">{prop.name}</div>
              ))}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );

  const renderGameLog = () => (
    <Card className="mt-4 p-4 h-64 overflow-y-auto">
      <div className="font-bold mb-2">Game Log</div>
      <div className="space-y-1">
        {gameState.gameLog.map((log, idx) => (
          <div key={idx} className="text-sm text-gray-600 border-b border-gray-100 pb-1">
            {log}
          </div>
        ))}
      </div>
    </Card>
  );

  const renderAIReasoning = () => (
    <Card className="mt-4 p-4">
      <div className="font-bold mb-2">Monopoly Decision Engine</div>
      <div className="h-96 overflow-y-auto space-y-2 bg-gray-50 p-4 rounded font-mono text-sm">
        {gameState.aiReasoningLog.map((log, idx) => {
          const lines = log.split('\n');
          return (
            <div key={idx} className="border-b border-gray-200 pb-2">
              {lines.map((line, lineIdx) => (
                <div 
                  key={lineIdx}
                  className={`${
                    line.includes('Decision:') ? 'font-bold text-blue-600' :
                    line.includes('Expected value') ? 'text-green-600' :
                    line.includes('Risk level:') ? 'text-red-600' :
                    'text-gray-700'
                  }`}
                >
                  {line}
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </Card>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <div className="text-2xl font-bold">Monopoly Simulation</div>
        <div className="space-x-4">
          <button
            onClick={startGame}
            disabled={gameState.isRunning}
            className="px-4 py-2 bg-green-500 text-white rounded disabled:bg-gray-300"
          >
            Start Game
          </button>
          <button
            onClick={stopGame}
            disabled={!gameState.isRunning}
            className="px-4 py-2 bg-red-500 text-white rounded disabled:bg-gray-300"
          >
            Stop Game
          </button>
        </div>
      </div>
      <div className="flex gap-8">
        <div className="flex-1 max-w-[800px]">
          <div className="pl-8">
            {renderBoard()}
          </div>
          {renderAIReasoning()}
        </div>
        <div className="flex-1 min-w-[400px]">
          {renderPlayerStats()}
          {renderGameLog()}
        </div>
      </div>
    </div>
  );
};

export default MonopolySimulation;
