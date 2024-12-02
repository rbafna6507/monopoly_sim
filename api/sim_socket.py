from flask import Flask
from flask_sock import Sock
from flask_cors import CORS
from monopoly_sim import MonopolySimulator
from monpoly_defs import Player, property_to_dict, player_to_dict
import threading
import time
import json

"""

This file contains the websocket server for the Monopoly simulator.

Wraps the MonopolySimulator class defined in monopoly_sim.py to run and return data through
a websocket connection to the react frontend. 
"""

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)
sock = Sock(app)

# global game state dictionary that contains:
# - simulator: the MonopolySimulator instance
# - game_log: a list of game logs
# - ai_log: a list of ai logs
# - is_running: a boolean indicating if the game is running
# - clients: a set of WebSocket connections
game_state = {
    'simulator': None,
    'game_log': [],
    'ai_log': [],
    'is_running': False,
    'clients': set()  # Store WebSocket connections
}

def broadcast_state():
    """broadcast the current game state to all connected clients"""
    
    # if the simulator is running, send the current state to the clients
    if game_state['simulator']:
        state_data = {
            'type': 'state_update',
            'data': {
                'players': [player_to_dict(p) for p in game_state['simulator'].players],
                'game_log': game_state['game_log'],
                'ai_log': game_state['ai_log'],
                'is_running': game_state['is_running']
            }
        }
        message = json.dumps(state_data)
        dead_clients = set()
        for ws in game_state['clients']:
            try:
                ws.send(message)
            except Exception:
                dead_clients.add(ws)
        
        # Clean up dead connections
        game_state['clients'] -= dead_clients

def game_loop():
    """game loop that simulates the game until only one player remains solvent"""
    
    # while the game is running, simulate the game  
    while game_state['is_running']:
        # if only one player remains solvent, end the game
        if len([p for p in game_state['simulator'].players if p.money > 0]) <= 1:
            game_state['is_running'] = False
            update = 'Game Over!'
            game_state['game_log'].insert(0, update)
            broadcast_state()
            break

        # log the current round
        game_state['ai_log'].append(f"@@@@ Round {game_state['simulator'].round} @@@@")
        game_state['simulator'].round += 1
        game_state['ai_log'].append("")

        for player in game_state['simulator'].players:
            if player.money > 0:
                old_position = player.position
                turn_logs = game_state['simulator'].take_turn(player)
                
                game_update = f"{player.name} moved from {old_position} to {player.position}"
                game_state['game_log'].insert(0, game_update)
                game_state['ai_log'].extend(turn_logs)
                
                # truncate logs
                if len(game_state['game_log']) > 20:
                    game_state['game_log'].pop()
                if len(game_state['ai_log']) > 100:
                    game_state['ai_log'] = game_state['ai_log'][-100:]
                
                broadcast_state()
                time.sleep(0)

def reset_game_state():
    """reset the game state"""
    
    global game_state
    game_state = {
        'simulator': None,
        'game_log': [],
        'ai_log': [],
        'is_running': False,
        'clients': game_state['clients'] if 'clients' in game_state else set()  # Preserve client connections
    }

@sock.route('/ws')
def handle_websocket(ws):
    """handle a websocket connection"""
    
    game_state['clients'].add(ws)
    try:
        while True:
            message = ws.receive()
            data = json.loads(message)
            
            if data['type'] == 'start_game':
                # reset the game state before starting a new game
                reset_game_state()
                game_state['clients'].add(ws)  # re-add the current client
                
                landing_frequencies = {
                    0: 0.02907, 1: 0.02005, 2: 0.01769, 3: 0.02034, 4: 0.02187,
                    5: 0.02797, 6: 0.02124, 7: 0.00814, 8: 0.02179, 9: 0.02163,
                    10: 0.01724, 11: 0.02550, 12: 0.02610, 13: 0.02171, 14: 0.02424,
                    15: 0.02633, 16: 0.02681, 17: 0.02295, 18: 0.02822, 19: 0.02809,
                    20: 0.02826, 21: 0.02611, 22: 0.01045, 23: 0.02563, 24: 0.02990,
                    25: 0.02889, 26: 0.02536, 27: 0.02515, 28: 0.02650, 29: 0.02434,
                    30: 0.00000, 31: 0.02519, 32: 0.02468, 33: 0.02224, 34: 0.02349,
                    35: 0.02287, 36: 0.00815, 37: 0.02057, 38: 0.02047, 39: 0.02480
                }

                # initialize the simulator with the landing frequencies and 5 players
                game_state['simulator'] = MonopolySimulator(landing_frequencies)
                game_state['simulator'].players = [
                    Player("Player 1", 1500, []),
                    Player("Player 2", 1500, []),
                    Player("Player 3", 1500, []),
                    Player("Player 4", 1500, []),
                    Player("Player 5", 1500, [])
                ]
                game_state['game_log'] = ['Game started!']
                game_state['is_running'] = True
                
                thread = threading.Thread(target=game_loop)
                thread.daemon = True
                thread.start()

            elif data['type'] == 'stop_game':
                if game_state['is_running']:
                    game_state['is_running'] = False

            broadcast_state()
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        game_state['clients'].remove(ws)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)