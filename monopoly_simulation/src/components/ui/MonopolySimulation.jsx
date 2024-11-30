import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card } from './card';
import { DollarSign, User, Building2 } from 'lucide-react';
import PlayerPositionChart from './PlayerPositionChart';

const WS_URL = 'ws://127.0.0.1:5000/ws';

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

const INITIAL_GAME_STATE = {
  players: [],
  gameLog: [],
  isRunning: false,
  aiReasoningLog: []
};

const MonopolySimulation = () => {
  const [gameState, setGameState] = useState(INITIAL_GAME_STATE);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [isConnecting, setIsConnecting] = useState(false);
  const ws = useRef(null);

  const connectWebSocket = useCallback(() => {
    // Don't create a new connection if we're already connecting or connected
    if (isConnecting || (ws.current?.readyState === WebSocket.CONNECTING || 
        ws.current?.readyState === WebSocket.OPEN)) {
      return;
    }

    setIsConnecting(true);

    // Close existing connection if any
    if (ws.current) {
      ws.current.close();
    }
    
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      console.log('WebSocket Connected');
      setConnectionStatus('connected');
      setIsConnecting(false);
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'state_update') {
          setGameState({
            players: message.data.players,
            gameLog: message.data.game_log,
            isRunning: message.data.is_running,
            aiReasoningLog: message.data.ai_log
          });
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.current.onclose = () => {
      console.log('WebSocket connection closed');
      setConnectionStatus('disconnected');
      setGameState(INITIAL_GAME_STATE);
      setIsConnecting(false);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('error');
      setIsConnecting(false);
    };
  }, [isConnecting]);

  // Initial WebSocket setup
  useEffect(() => {
    connectWebSocket();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connectWebSocket]);

  const sendWebSocketMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  };

  const startGame = () => {
    // Only send the start game message if we're connected
    if (connectionStatus === 'connected' && !gameState.isRunning) {
      sendWebSocketMessage({ type: 'start_game' });
    }
  };

  const stopGame = () => {
    if (connectionStatus === 'connected' && gameState.isRunning) {
      sendWebSocketMessage({ type: 'stop_game' });
    }
  };

  // Rest of the render functions remain the same...
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
  
    const baseClasses = "relative h-20 border border-gray-300 p-2 text-xs flex flex-col";
    const cornerClasses = isCorner ? "items-center justify-center" : "";
  
    return (
      <div className={`${baseClasses} ${cornerClasses}`}>
        {propertyDetails && (
          <>
            <div className={`h-3 ${PROPERTY_COLORS[propertyDetails.color]} w-full -mt-2`} />
            <div className="mt-2 font-semibold leading-tight text-center">{propertyDetails.name}</div>
            <div className="text-gray-600 text-center mt-auto mb-1">${propertyDetails.price}</div>
          </>
        )}
        {isCorner && (
          <div className="font-bold text-center text-sm">
            {position === 0 && "GO"}
            {position === 10 && "JAIL"}
            {position === 20 && "FREE\nPARKING"}
            {position === 30 && "GO TO\nJAIL"}
          </div>
        )}
        {isRailroad && (
          <>
            <div className="text-center mt-3 font-semibold">Railroad</div>
            <div className="text-gray-600 text-center mt-auto mb-1">$200</div>
          </>
        )}
        {isUtility && (
          <>
            <div className="text-center mt-3 font-semibold">
              {position === 12 ? "Electric\nCompany" : "Water\nWorks"}
            </div>
            <div className="text-gray-600 text-center mt-auto mb-1">$150</div>
          </>
        )}
        {isTax && (
          <>
            <div className="text-center mt-3 font-semibold">
              {position === 4 ? "Income\nTax" : "Luxury\nTax"}
            </div>
            <div className="text-gray-600 text-center mt-auto mb-1">
              ${position === 4 ? "200" : "100"}
            </div>
          </>
        )}
        {(isChance || isCommunityChest) && (
          <div className="text-center mt-6 font-semibold">
            {isChance ? "Chance" : "Community\nChest"}
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
      <div key={`bottom-${i}`} className="w-20">
        {renderSpace(10-i)}
      </div>
    ));

    const rightColumn = [...Array(9)].map((_, i) => (
      <div key={`right-${i}`} className="h-20">
        {renderSpace(31 + i)}
      </div>
    ));

    const topRow = [...Array(11)].map((_, i) => (
      <div key={`top-${i}`} className="w-20">
        {renderSpace(20 + i)}
      </div>
    ));

    const leftColumn = [...Array(9)].map((_, i) => (
      <div key={`left-${i}`} className="h-20">
        {renderSpace(19 - i)}
      </div>
    ));

    return (
      <div className="relative w-fit bg-white shadow-lg rounded-lg p-4">
        <div className="flex">
          {topRow}
        </div>
        <div className="flex">
          <div className="flex flex-col">
            {leftColumn}
          </div>
          <div className="bg-green-50 flex-1">
            <div className="w-full h-full flex items-center justify-center relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl font-bold text-green-800 rotate-45 mb-8">
                    MONOPOLY
                  </div>
                  <div className="text-sm text-green-700 mt-[50%]">
                    {gameState.isRunning ? "Game in progress..." : "Press Start to begin"}
                  </div>
                </div>
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

  // const renderPlayerStats = () => (
  //   <div className="grid grid-cols-2 gap-6 mt-4">
  //     {gameState.players.map((player, idx) => (
  //       <Card key={idx} className="p-6">
  //         <div className={`font-bold ${PLAYER_COLORS[idx]} flex items-center gap-2`}>
  //           <User className="h-5 w-5" />
  //           {player.name}
  //         </div>
  //         <div className="flex items-center gap-1 mt-4">
  //           <DollarSign className="h-4 w-4" />
  //           {player.money}
  //         </div>
  //         <div className="mt-4 text-sm space-y-2">
  //           <div>Position: {player.position}</div>
  //           <div>Properties:</div>
  //           <div className="pl-3 text-xs space-y-1">
  //             {player.properties.map((prop, i) => (
  //               <div key={i} className="text-gray-600">{prop.name}</div>
  //             ))}
  //           </div>
  //         </div>
  //       </Card>
  //     ))}
  //   </div>
  // );

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
    <div className="p-4 max-w-[1800px] mx-auto">
      <div className="flex justify-between items-center mb-4">
        <div className="text-2xl font-bold">Monopoly Simulation</div>
        <div className="flex items-center gap-4">
          <div className={`px-2 py-1 rounded text-sm ${
            connectionStatus === 'connected' ? 'bg-green-100 text-green-800' :
            connectionStatus === 'error' ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {connectionStatus === 'connected' ? 'Connected' :
             connectionStatus === 'error' ? 'Connection Error' :
             'Disconnected'}
          </div>
          <div className="space-x-4">
            <button
              onClick={startGame}
              disabled={gameState.isRunning || connectionStatus !== 'connected'}
              className="px-4 py-2 bg-green-500 text-white rounded disabled:bg-gray-300"
            >
              Start Game
            </button>
            <button
              onClick={stopGame}
              disabled={!gameState.isRunning || connectionStatus !== 'connected'}
              className="px-4 py-2 bg-red-500 text-white rounded disabled:bg-gray-300"
            >
              Stop Game
            </button>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-[900px_1fr] gap-8">
        <div>
          <div>{renderBoard()}</div>
          <div className="mt-6">{renderAIReasoning()}</div>
        </div>
        <div className="flex flex-col gap-6">
          <PlayerPositionChart gameState={gameState} />
          {renderGameLog()}
        </div>
      </div>
    </div>
  );
};

export default MonopolySimulation;