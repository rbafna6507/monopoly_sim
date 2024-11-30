import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card } from './card';


const PlayerPositionChart = ({ gameState = { players: [], gameLog: [], aiReasoningLog: [] } }) => {
  const [propertyHistory, setPropertyHistory] = useState([]);
  const PLAYER_COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#a855f7'];

  // Reset history when game starts or when there are no players
  useEffect(() => {
    // Reset when game starts (checking both game log and players)
    if ((gameState.gameLog.length === 1 && gameState.gameLog[0] === 'Game started!') || gameState.players.length === 0) {
      setPropertyHistory([]);
      return;
    }

    if (!gameState?.players?.length) return;

    // Find the current round from AI log
    const roundMatch = gameState.aiReasoningLog
      .find(log => log.includes('@@@@ Round'))
      ?.match(/@@@@ Round (\d+) @@@@/);
    
    const currentRound = roundMatch ? parseInt(roundMatch[1], 10) : 0;

    // Only add new entry if we don't already have this round
    if (currentRound >= 0 && (!propertyHistory.length || propertyHistory[propertyHistory.length - 1]?.round !== currentRound)) {
      const newEntry = {
        round: currentRound,
        ...gameState.players.reduce((acc, player, idx) => ({
          ...acc,
          [`player${idx}Properties`]: player.properties?.length ?? 0,
          [`player${idx}PropertiesList`]: player.properties ?? [],
          [`player${idx}Money`]: player.money ?? 0,
          [`player${idx}Position`]: player.position ?? 0,
          [`player${idx}Name`]: player.name ?? `Player ${idx + 1}`
        }), {})
      };

      setPropertyHistory(prev => [...prev, newEntry].sort((a, b) => a.round - b.round));
    }
  }, [gameState]);

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.[0]?.payload) return null;

    const round = payload[0].payload.round;
    const playerData = gameState.players.map((_, idx) => ({
      name: payload[0].payload[`player${idx}Name`] ?? `Player ${idx + 1}`,
      properties: payload[0].payload[`player${idx}PropertiesList`] ?? [],
      propertyCount: payload[0].payload[`player${idx}Properties`] ?? 0,
      money: payload[0].payload[`player${idx}Money`] ?? 0,
      position: payload[0].payload[`player${idx}Position`] ?? 0,
      color: PLAYER_COLORS[idx]
    }));

    return (
      <div className="bg-white p-4 shadow-lg rounded-lg border">
        <div className="font-bold mb-2">Round {round}</div>
        <div className="space-y-3">
          {playerData.map((player, idx) => (
            <div key={idx} className="space-y-1">
              <div className="font-semibold" style={{ color: player.color }}>
                {player.name}
              </div>
              <div className="text-sm text-gray-600 pl-2">
                <div>Properties Owned: {player.propertyCount}</div>
                <div>Cash: ${player.money.toLocaleString()}</div>
                <div className="text-xs max-w-md">
                  Properties: {player.properties.map(p => p.name).join(', ') || 'None'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (!gameState?.players?.length) {
    return (
      <Card className="p-4 min-w-[600px]">
        <div className="font-bold mb-4">Properties Owned Over Time</div>
        <div className="h-96 flex items-center justify-center text-gray-500">
          Waiting for game to start...
        </div>
      </Card>
    );
  }

  const visibleRounds = propertyHistory.length > 0 ? [
    propertyHistory[0].round,
    propertyHistory[propertyHistory.length - 1].round
  ] : [0, 0];

  return (
    <Card className="p-4 min-w-[600px]">
      <div className="font-bold mb-4">
        Properties Owned Over Time 
        <span className="text-sm font-normal text-gray-500 ml-2">
          (Rounds {visibleRounds[0]} - {visibleRounds[1]})
        </span>
      </div>
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={propertyHistory}
            margin={{ top: 10, right: 30, left: 30, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="round" 
              label={{ value: 'Round', position: 'bottom' }}
            />
            <YAxis 
              domain={[0, 28]}
              label={{ value: 'Properties Owned', angle: -90, position: 'left' }}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {gameState.players.map((_, idx) => (
              <Line
                key={idx}
                type="monotone"
                dataKey={`player${idx}Properties`}
                name={`Player ${idx + 1}`}
                stroke={PLAYER_COLORS[idx]}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};

export default PlayerPositionChart;