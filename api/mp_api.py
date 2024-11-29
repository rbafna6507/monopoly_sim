from flask import Flask, jsonify
from flask_cors import CORS
from m_test import MonopolySimulator
from monpoly_defs import Player
import threading
import time
import queue

"""api bitch"""

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# game state
# TODO: comment tf out of this
game_state = {
    'simulator': None,
    'game_log': [],
    'ai_log': [],  
    'is_running': False,
    'update_queue': queue.Queue()
}

# easy conversion to json - could have used asdict(), but this makes it easier for me
def property_to_dict(prop):
    return {
        'name': prop.name,
        'position': prop.position,
        'price': prop.price,
        'rent': prop.rent,
        'color_group': prop.color_group,
        'landing_frequency': prop.landing_frequency,
        'houses': prop.houses,
        'owner': prop.owner.name if prop.owner else None
    }

def player_to_dict(player):
    return {
        'name': player.name,
        'money': player.money,
        'position': player.position,
        'properties': [property_to_dict(prop) for prop in player.properties]
    }

def game_loop():
    
    while game_state['is_running']:
        if len([p for p in game_state['simulator'].players if p.money > 0]) <= 1:
            game_state['is_running'] = False
            update = 'Game Over!'
            game_state['update_queue'].put({'game_log': update, 'ai_log': []})
            break
        game_state['ai_log'].append(f"@@@@ Round {game_state['simulator'].round} @@@@")
        game_state['simulator'].round += 1
        game_state['ai_log'].append("")
        for player in game_state['simulator'].players:
            if player.money > 0:
                old_position = player.position
                turn_logs = game_state['simulator'].take_turn(player)
                
                game_update = f"{player.name} moved from {old_position} to {player.position}"
                
                # Add logs to their respective collections
                game_state['game_log'].insert(0, game_update)
                game_state['ai_log'].extend(turn_logs)
                
                # truncate logs
                if len(game_state['game_log']) > 20:
                    game_state['game_log'].pop()
                if len(game_state['ai_log']) > 100:
                    game_state['ai_log'] = game_state['ai_log'][-100:]
                
                game_state['update_queue'].put({
                    'game_log': game_update,
                    'ai_log': turn_logs
                })
        time.sleep(.4)

@app.route('/api/start', methods=['GET', 'POST'])
def start_game():
    if not game_state['is_running']:
        landing_frequencies = {
            0: 0.02907, 1: 0.02005, 2: 0.01769, 3: 0.02034, 4: 0.02187, 5: 0.02797,
            6: 0.02124, 7: 0.00814, 8: 0.02179, 9: 0.02163, 10: 0.01724, 11: 0.02550,
            12: 0.02610, 13: 0.02171, 14: 0.02424, 15: 0.02633, 16: 0.02681, 17: 0.02295,
            18: 0.02822, 19: 0.02809, 20: 0.02826, 21: 0.02611, 22: 0.01045, 23: 0.02563,
            24: 0.02990, 25: 0.02889, 26: 0.02536, 27: 0.02515, 28: 0.02650, 29: 0.02434,
            30: 0.00000, 31: 0.02519, 32: 0.02468, 33: 0.02224, 34: 0.02349, 35: 0.02287,
            36: 0.00815, 37: 0.02057, 38: 0.02047, 39: 0.02480
        }

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
        
        # need to run game loop in thread so that i keeps running after call.
        
        # TODO: double check thread behavior - make sure it isn't blocking
        thread = threading.Thread(target=game_loop)
        thread.daemon = True
        thread.start()

        return jsonify({'status': 'success', 'message': 'Game started'})
    return jsonify({'status': 'error', 'message': 'Game already running'})

@app.route('/api/stop', methods=['GET','POST'])
def stop_game():
    if game_state['is_running']:
        # TODO: end thread
        # TODO: use asyncio? see pros/cons -
        game_state['is_running'] = False
        return jsonify({'status': 'success', 'message': 'Game stopped'})
    return jsonify({'status': 'error', 'message': 'No game running'})

@app.route('/api/state', methods=['GET','POST', 'OPTIONS'])
def get_state():
    if game_state['simulator']:
        return jsonify({
            'players': [player_to_dict(p) for p in game_state['simulator'].players],
            'game_log': game_state['game_log'],
            'ai_log': game_state['ai_log'],
            'is_running': game_state['is_running']
        })
    return jsonify({
        'players': [],
        'game_log': [],
        'ai_log': [],
        'is_running': False
    })

@app.route('/api/updates')
def get_updates():
    try:
        update = game_state['update_queue'].get_nowait()
        return jsonify({
            'update': True,
            'game_log': update['game_log'],
            'ai_log': update['ai_log']
        })
    except queue.Empty:
        return jsonify({
            'update': False,
            'game_log': None,
            'ai_log': None
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)