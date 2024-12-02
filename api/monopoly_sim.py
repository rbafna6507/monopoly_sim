import random
from typing import List, Dict, Tuple
import copy
from monpoly_defs import Player, Property

"""

Simulator for Monopoly. The total funtionality fo this simulator is as follows:
    - simulate a full game of Monopoly until only one player remains solvent
    - on each turn, a player can buy the property they are currently on
    - if a player buys a property, the simulator will simulate the potential outcomes of the game
    - the simulator will then return a recommendation to buy or not buy the property
    - the simulator will also return a reasoning for the recommendation

This simulator implements basic decision making logic. Simply put, it attempts to maximize
the expected value of a property based on landing frequency, color set completion, nearby
opponent properties, and current cash.

"""


class MonopolySimulator:
    """simulate a game of Monopoly"""
    
    def __init__(self, landing_frequencies: Dict[int, float]):
        self.properties = self.initialize_properties(landing_frequencies)
        self.num_properties = len(self.properties)
        self.players: List[Player] = []
        self.round = 1
        
        
    def initialize_properties(self, landing_frequencies: Dict[int, float]) -> List[Property]:
        # property values in the order of the board
        properties = [
            Property(name="Mediterranean Avenue", position=1, price=60, rent=[2, 10, 30, 90, 160, 250], color_group="brown"),
            Property(name="Baltic Avenue", position=3, price=60, rent=[4, 20, 60, 180, 320, 450], color_group="brown"),
            Property(name="Oriental Avenue", position=6, price=100, rent=[6, 30, 90, 270, 400, 550], color_group="light_blue"),
            Property(name="Vermont Avenue", position=8, price=100, rent=[6, 30, 90, 270, 400, 550], color_group="light_blue"),
            Property(name="Connecticut Avenue", position=9, price=120, rent=[8, 40, 100, 300, 450, 600], color_group="light_blue"),
            Property(name="St. Charles Place", position=11, price=140, rent=[10, 50, 150, 450, 625, 750], color_group="pink"),
            Property(name="States Avenue", position=13, price=140, rent=[10, 50, 150, 450, 625, 750], color_group="pink"),
            Property(name="Virginia Avenue", position=14, price=160, rent=[12, 60, 180, 500, 700, 900], color_group="pink"),
            Property(name="St. James Place", position=16, price=180, rent=[14, 70, 200, 550, 750, 950], color_group="orange"),
            Property(name="Tennessee Avenue", position=18, price=180, rent=[14, 70, 200, 550, 750, 950], color_group="orange"),
            Property(name="New York Avenue", position=19, price=200, rent=[16, 80, 220, 600, 800, 1000], color_group="orange"),
            Property(name="Kentucky Avenue", position=21, price=220, rent=[18, 90, 250, 700, 875, 1050], color_group="red"),
            Property(name="Indiana Avenue", position=23, price=220, rent=[18, 90, 250, 700, 875, 1050], color_group="red"),
            Property(name="Illinois Avenue", position=24, price=240, rent=[20, 100, 300, 750, 925, 1100], color_group="red"),
            Property(name="Atlantic Avenue", position=26, price=260, rent=[22, 110, 330, 800, 975, 1150], color_group="yellow"),
            Property(name="Ventnor Avenue", position=27, price=260, rent=[22, 110, 330, 800, 975, 1150], color_group="yellow"),
            Property(name="Marvin Gardens", position=29, price=280, rent=[24, 120, 360, 850, 1025, 1200], color_group="yellow"),
            Property(name="Pacific Avenue", position=31, price=300, rent=[26, 130, 390, 900, 1100, 1275], color_group="green"),
            Property(name="North Carolina Avenue", position=32, price=300, rent=[26, 130, 390, 900, 1100, 1275], color_group="green"),
            Property(name="Pennsylvania Avenue", position=34, price=320, rent=[28, 150, 450, 1000, 1200, 1400], color_group="green"),
            Property(name="Park Place", position=37, price=350, rent=[35, 175, 500, 1100, 1300, 1500], color_group="dark_blue"),
            Property(name="Boardwalk", position=39, price=400, rent=[50, 200, 600, 1400, 1700, 2000], color_group= "dark_blue"),
        ]
        
        # letting the landing frequencies be set by caller to play with different board setups
        for prop in properties:
            prop.landing_frequency = landing_frequencies.get(prop.position, 0.0)
            
        return properties


    def calculate_expected_property_value(self, property: Property, player: Player) -> float:
        """Calculate expected value of a property based on rent, landing frequency, color set completion, 
            nearby opponent properties, and current cash"""
            
        # initialize base value of property to 0
        value = 0.0
        
        # creates a landing frequency multiplier that boosts or penalizes the value of the property if it is above or below average (.025).
        # multiply the property's rent by the multiplier to boost or penalize the property value
        landing_freq_multiplier = (property.landing_frequency / 0.025) ** 2
        base_rent_value = property.rent[0] * landing_freq_multiplier
        value += base_rent_value
        
        # if the player owns the entire color group, boost the value by 100%
        # if the player owns any properties in the color group, boost the value by 25% for each property
        color_group = property.color_group.lower()
        owned_in_group = len(player.get_properties_in_color_group(color_group))
        if player.owns_complete_set(color_group):
            value *= 2.0
        elif owned_in_group > 0:
            value *= (1.0 + (0.25 * owned_in_group))  
            
        # if there are opponent properties nearby, penalize the value by 10% for each nearby property (within 5 spaces)
        opponent_props_nearby = self.count_nearby_opponent_properties(property, player)
        if opponent_props_nearby > 0:
            value *= (1.0 - (0.1 * opponent_props_nearby)) 
            
        # if the player has less than half of the average starting cash, penalize the value by 20%
        cash_ratio = player.money / 1500 
        if cash_ratio < 0.5:  
            value *= 0.8 
            
        return value


    def count_nearby_opponent_properties(self, property: Property, player: Player) -> int:
        """count how many properties within 5 spaces are owned by opponents"""
        
        # initialize count of nearby opponent properties to 0.
        # iterate through all players and count the number of properties within 5 spaces
        # return the count
        count = 0
        for other_player in self.players:
            if other_player.name != player.name:
                for op in other_player.properties:
                    distance = min(
                        abs(op.position - property.position),
                        40 - abs(op.position - property.position)  # Account for board wrap-around
                    )
                    if distance <= 5:
                        count += 1
        return count


    def simulate_turn(self, player: Player, iterations: int = 1000) -> Tuple[bool, float]:
        """simulate potential outcomes of buying vs not buying the current property."""
        
        # if the property is not valid or the player cannot afford it, do not buy
        current_property = next((p for p in self.properties if p.position == player.position), None)
        if not current_property or not player.can_afford(current_property.price):
            return False, 0.0

        # create two 'simulations' of the game, one where the player buys the property and one where they don't, and copy the current game state into each
        # within each game state, get the respective player instance
        buy_universe = copy.deepcopy(self) 
        no_buy_universe = copy.deepcopy(self)
        buy_player = next(p for p in buy_universe.players if p.name == player.name)
        no_buy_player = next(p for p in no_buy_universe.players if p.name == player.name)
        
        # Execute the purchase in buy universe
        buy_property = next(p for p in buy_universe.properties if p.position == current_property.position)
        buy_player.pay(buy_property.price)
        buy_property.owner = buy_player
        buy_player.properties.append(buy_property)
        
        buy_score = 0
        no_buy_score = 0
        
        for _ in range(iterations):
            # Simulate both universes with full game state
            buy_result = self.simulate_future_turns(buy_universe, buy_player, 20)
            no_buy_result = self.simulate_future_turns(no_buy_universe, no_buy_player, 20)
            
            buy_score += buy_result
            no_buy_score += no_buy_result
        
        avg_buy_score = buy_score / iterations
        avg_no_buy_score = no_buy_score / iterations
        
        return avg_buy_score > avg_no_buy_score, avg_buy_score - avg_no_buy_score

    def simulate_future_turns(self, game_state: 'MonopolySimulator', player: Player, num_turns: int) -> float:
        """simulate future turns considering the full game state - used for game states where property is already bought
           is being evaluated whether to buy or not."""
        
        # initialize score to 0
        score = 0.0
        
        # simulate the future turns by iterating through the number of turns
        # on each turn, roll two dice, add them together to get the roll
        # if the player lands on a property that is owned by another player, collect rent
        # if the player does not have enough money, attempt to sell properties to pay the rent
        # if the player lands on a property that is unowned, do nothing
        for _ in range(num_turns):
            # Roll dice and move
            roll1, roll2 = random.randint(1, 6), random.randint(1, 6)
            roll = roll1 + roll2
            player.position = (player.position + roll) % 40
            
            # Handle property landing
            current_property = next((p for p in game_state.properties if p.position == player.position), None)
            if current_property and current_property.owner and current_property.owner != player:
                rent = current_property.rent[current_property.houses]
                if current_property.owner.owns_complete_set(current_property.color_group):
                    rent *= 2
                if player.money >= rent:
                    player.pay(rent)
                    current_property.owner.receive(rent)
        
        # add the player's current cash to the score
        score += player.money
        
        # add the value of the player's properties to the score
        # if the player owns the entire color group, add 50% more value to the property
        for prop in player.properties:
            property_value = prop.price
            if player.owns_complete_set(prop.color_group):
                property_value *= 1.5  # Premium for complete sets
            score += property_value
            
        # add the expected future rent income to the score
        # expected rent is the rent of the property at its current development level
        # if the player owns the entire color group, multiply the rent by 2
        for prop in player.properties:
            expected_landings = prop.landing_frequency * (len(game_state.players) - 1) * (num_turns / 40)
            expected_rent = prop.rent[prop.houses]
            if player.owns_complete_set(prop.color_group):
                expected_rent *= 2
            score += expected_landings * expected_rent
        
        return score


    def make_decision(self, player: Player) -> Tuple[bool, str]:
        """make a decision to buy or not buy the current property"""
        
        # get the current property the player is on
        current_property = next((p for p in self.properties if p.position == player.position), None)
        if not current_property:
            return False, "No property to buy at current position"
            
        # if the player cannot afford the property, do not buy
        if not player.can_afford(current_property.price):
            return False, f"Insufficient funds (${player.money} < ${current_property.price})"
        
        # simulate the turn to buy or not buy the property
        should_buy, value_difference = self.simulate_turn(player)
        
        # get the color group of the property
        color_group = current_property.color_group.lower()
        # get the number of properties the player owns in the color group
        owned_in_group = len(player.get_properties_in_color_group(color_group))
        # count the number of opponent properties within 5 spaces
        nearby_opponent_props = self.count_nearby_opponent_properties(current_property, player)
        
        reasoning = [
            f"Decision: {'Buy' if should_buy else 'Dont buy'} {current_property.name}",
            f"Expected value difference: ${value_difference:.2f}",
            f"Landing frequency: {current_property.landing_frequency:.3f}",
            f"Property price: ${current_property.price}",
            f"Current money: ${player.money}",
            f"Properties owned in {color_group}: {owned_in_group}",
            f"Nearby opponent properties: {nearby_opponent_props}",
            f"Base rent: ${current_property.rent[0]}",
            f"Risk level: {'High' if player.money - current_property.price < 300 else 'Low'}"
        ]
        
        return should_buy, "\n".join(reasoning)


    def run_full_game(self):
        """simulate a full game of Monopoly until only one player remains solvent"""
        print("\n=== Starting Full Monopoly Game Simulation ===\n")
        round_number = 1
        max_rounds = 200  # Prevent infinite games
        
        # game loop
        while len([p for p in self.players if p.money > 0]) > 1 and round_number < max_rounds:
            print(f"\n=== Round {round_number} ===")
            self.play_round()
            self._print_game_status()
            round_number += 1
        
        # winner post processing
        winner = next((p for p in self.players if p.money > 0), None)
        print("\n=== Game Over ===")
        if winner:
            print(f"Winner: {winner.name}")
            print(f"Final net worth: ${winner.calculate_net_worth()}")
            print("Owned properties:")
            for prop in winner.properties:
                print(f"- {prop.name}")
        else:
            print("Game ended in a draw (max rounds reached)")


    def play_round(self):
        """play a single round where each player takes a turn"""
        for player in self.players:
            if player.money > 0:  # Only active players take turns
                self.take_turn(player)

    
    def take_turn(self, player: Player):
        """perform a single player's turn"""
        turn_log = []
        turn_log.append(f"\n=== {player.name}'s turn ===")
        turn_log.append(f"Starting position: {player.position}")
        turn_log.append(f"Money: ${player.money}")
        
        # roll two dice, add them together to get the roll
        roll = random.randint(1, 6) + random.randint(1, 6)
        player.position = (player.position + roll) % 40
        # turn_log.append(f"Rolled {roll}, moved to position {player.position}")
        
        # check if landed on property
        current_property = next((p for p in self.properties if p.position == player.position), None)
        if not current_property:
            turn_log.append("Landed on non-property space")
            return turn_log
            
        # if property is owned, pay rent
        if current_property.owner and current_property.owner != player:
            rent = current_property.rent[current_property.houses]
            rent_log = self.handle_rent_payment(player, current_property, rent)
            turn_log.extend(rent_log)
        
        # if property is unowned, consider buying
        elif not current_property.owner:
            should_buy, reasoning = self.make_decision(player)
            turn_log.extend(reasoning.split('\n'))
            if should_buy and player.can_afford(current_property.price):
                current_property.owner = player
                player.properties.append(current_property)
                player.pay(current_property.price)
                turn_log.append(f"Property purchased. Remaining money: ${player.money}")
        
        return turn_log

    def handle_rent_payment(self, player: Player, current_property: Property, rent_amount: int) -> List[str]:
        """rent payment logic with property selling if player is out of money, 
            return logged actions of player"""
            
        log = []
        log.append(f"{player.name} must pay ${rent_amount} rent to {current_property.owner.name}")
        
        # if the player has enough money, pay the rent
        if player.money >= rent_amount:
            player.pay(rent_amount)
            current_property.owner.receive(rent_amount)
            log.append(f"Rent paid. Remaining money: ${player.money}")
            return log
            
        # if the player cannot afford rent, attempt to sell properties
        log.append(f"{player.name} cannot afford rent, attempting to sell properties...")
        debt_remaining = rent_amount - player.money
        properties_to_sell = []
        
        # sell cheapest properties first
        sorted_properties = sorted(player.properties, key=lambda p: p.price)
        current_value = 0
        for prop in sorted_properties:
            property_value = prop.price + (prop.houses * (prop.price // 2))
            current_value += property_value
            properties_to_sell.append(prop)
            
            if current_value >= debt_remaining:
                break
                
        # if after selling everything player still can't afford rent, player is bankrupt
        total_possible_value = sum(p.price + (p.houses * (p.price // 2)) for p in player.properties)
        if total_possible_value + player.money < rent_amount:
            log.append(f"{player.name} cannot raise enough money even by selling all properties!")
            self.execute_bankruptcy(player, current_property.owner)
            return log
            
        # sell the properties
        for prop in properties_to_sell:
            sale_value = prop.price + (prop.houses * (prop.price // 2))
            player.money += sale_value
            player.properties.remove(prop)
            prop.owner = None
            prop.houses = 0  # Reset development when sold
            log.append(f"{player.name} sold {prop.name} for ${sale_value}")
            
        # pay the rent
        player.pay(rent_amount)
        current_property.owner.receive(rent_amount)
        log.append(f"After selling properties and paying rent, {player.name} has ${player.money} remaining")
        return log

    def execute_bankruptcy(self, bankrupt_player: Player, creditor: Player) -> List[str]:
        """handle the bankruptcy of a player. returns log of actions."""
        log = []
        log.append(f"{bankrupt_player.name} is bankrupt!")
        
        # free all owned properties
        for prop in bankrupt_player.properties:
            log.append(f"Property {prop.name} is now available for purchase")
            prop.owner = None
            prop.houses = 0  # Reset development when freed
        
        bankrupt_player.properties = []
        bankrupt_player.money = 0
        
        log.append(f"{bankrupt_player.name} has been eliminated from the game")
        return log
    