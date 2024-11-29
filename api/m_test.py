import random
from typing import List, Dict, Tuple
import copy
from monpoly_defs import Player, Property


class MonopolySimulator:
    """simulate a game of Monopoly"""
    
    def __init__(self, landing_frequencies: Dict[int, float]):
        self.properties = self.initialize_properties(landing_frequencies)
        self.num_properties = len(self.properties)
        self.players: List[Player] = []
        self.round = 1
        
        
    def initialize_properties(self, landing_frequencies: Dict[int, float]) -> List[Property]:
        # property values in the order of the board
        # TODO: use keywrod arguments bc this is confusing
        #NOTE: docstrings
        properties = [
            Property("Mediterranean Avenue", 1, 60, [2, 10, 30, 90, 160, 250], "brown"),
            Property("Baltic Avenue", 3, 60, [4, 20, 60, 180, 320, 450], "brown"),
            Property("Oriental Avenue", 6, 100, [6, 30, 90, 270, 400, 550], "light_blue"),
            Property("Vermont Avenue", 8, 100, [6, 30, 90, 270, 400, 550], "light_blue"),
            Property("Connecticut Avenue", 9, 120, [8, 40, 100, 300, 450, 600], "light_blue"),
            Property("St. Charles Place", 11, 140, [10, 50, 150, 450, 625, 750], "pink"),
            Property("States Avenue", 13, 140, [10, 50, 150, 450, 625, 750], "pink"),
            Property("Virginia Avenue", 14, 160, [12, 60, 180, 500, 700, 900], "pink"),
            Property("St. James Place", 16, 180, [14, 70, 200, 550, 750, 950], "orange"),
            Property("Tennessee Avenue", 18, 180, [14, 70, 200, 550, 750, 950], "orange"),
            Property("New York Avenue", 19, 200, [16, 80, 220, 600, 800, 1000], "orange"),
            Property("Kentucky Avenue", 21, 220, [18, 90, 250, 700, 875, 1050], "red"),
            Property("Indiana Avenue", 23, 220, [18, 90, 250, 700, 875, 1050], "red"),
            Property("Illinois Avenue", 24, 240, [20, 100, 300, 750, 925, 1100], "red"),
            Property("Atlantic Avenue", 26, 260, [22, 110, 330, 800, 975, 1150], "yellow"),
            Property("Ventnor Avenue", 27, 260, [22, 110, 330, 800, 975, 1150], "yellow"),
            Property("Marvin Gardens", 29, 280, [24, 120, 360, 850, 1025, 1200], "yellow"),
            Property("Pacific Avenue", 31, 300, [26, 130, 390, 900, 1100, 1275], "green"),
            Property("North Carolina Avenue", 32, 300, [26, 130, 390, 900, 1100, 1275], "green"),
            Property("Pennsylvania Avenue", 34, 320, [28, 150, 450, 1000, 1200, 1400], "green"),
            Property("Park Place", 37, 350, [35, 175, 500, 1100, 1300, 1500], "dark_blue"),
            Property("Boardwalk", 39, 400, [50, 200, 600, 1400, 1700, 2000], "dark_blue"),
        ]
        
        # letting the landing frequencies be set by caller to play with different board setups
        for prop in properties:
            prop.landing_frequency = landing_frequencies.get(prop.position, 0.0)
            
        return properties


    def calculate_expected_property_value(self, property: Property, player: Player) -> float:
        """Expected value of a property based on rent, landing frequency, color set completion, 
            nearby opponent properties, and current cash"""
        value = 0.0
        
        # TODO: make these comments for each hueristic better
        # TODO: beef up docstring
        
        # incentivize higher landing frequencies using exponential scaling (and penalizing lower than average frequencies)
        # frequencies below average (0.025) get penalized, above get boosted
        landing_freq_multiplier = (property.landing_frequency / 0.025) ** 2
        base_rent_value = property.rent[0] * landing_freq_multiplier
        value += base_rent_value
        
        # color set progression bonus
        color_group = property.color_group.lower()
        owned_in_group = len(player.get_properties_in_color_group(color_group))
        if player.owns_complete_set(color_group):
            value *= 2.0
        elif owned_in_group > 0:
            value *= (1.0 + (0.25 * owned_in_group))  
            
        # 10% penalty per opponent property nearby
        opponent_props_nearby = self.count_nearby_opponent_properties(property, player)
        if opponent_props_nearby > 0:
            value *= (1.0 - (0.1 * opponent_props_nearby)) 
            
        # consider how much cash the player has - penalize value if low on cash
        cash_ratio = player.money / 1500 
        if cash_ratio < 0.5:  
            value *= 0.8 
            
        return value


    def count_nearby_opponent_properties(self, property: Property, player: Player) -> int:
        """count how many properties within 5 spaces are owned by opponents"""
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
        """create hueristics to estimate buying vs. not buying the current property"""
        # TODO: beef up docstring
        # TODO: add a chaos factor
        # TODO: more comments everywhere
        
        
        current_property = next((p for p in self.properties if p.position == player.position), None)
        if not current_property or not player.can_afford(current_property.price):
            return False, 0.0

        
        print('making a parallel universe to buy ', current_property.name)
        buy_universe = copy.deepcopy(player)
        no_buy_universe = copy.deepcopy(player)
        
        buy_universe.pay(current_property.price)
        current_property_copy = copy.deepcopy(current_property)
        current_property_copy.owner = buy_universe
        buy_universe.properties.append(current_property_copy)
        
        buy_score = 0
        no_buy_score = 0
        
        for _ in range(iterations):
            buy_result = self.simulate_future_turns(buy_universe, 40)
            no_buy_result = self.simulate_future_turns(no_buy_universe, 40)
            
            buy_score += buy_result
            no_buy_score += no_buy_result
        
        avg_buy_score = buy_score / iterations
        avg_no_buy_score = no_buy_score / iterations
        
        return avg_buy_score > avg_no_buy_score, avg_buy_score - avg_no_buy_score


    def simulate_future_turns(self, player: Player, num_turns: int) -> float:
        """simulate future turns and return a score based on money and property value"""
        sim_player = copy.deepcopy(player)
        score = 0.0
        
        for _ in range(num_turns):
            roll = random.randint(1, 6) + random.randint(1, 6)
            sim_player.position = (sim_player.position + roll) % 40  
            
            for prop in sim_player.properties:
                expected_landings = prop.landing_frequency * (len(self.players) - 1)
                expected_rent = prop.rent[0]  
                if sim_player.owns_complete_set(prop.color_group):
                    expected_rent *= 2  
                
                score += expected_landings * expected_rent
        
        score += sim_player.calculate_net_worth()
        for prop in sim_player.properties:
            score += self.calculate_expected_property_value(prop, sim_player)
            
        return score


    def make_decision(self, player: Player) -> Tuple[bool, str]:
        """decide to buy the property or not, and give reasoning"""
        
        current_property = next((p for p in self.properties if p.position == player.position), None)
        if not current_property:
            return False, "No property to buy at current position"
            
        if not player.can_afford(current_property.price):
            return False, f"Insufficient funds (${player.money} < ${current_property.price})"
        
        should_buy, value_difference = self.simulate_turn(player)
        
        color_group = current_property.color_group.lower()
        owned_in_group = len(player.get_properties_in_color_group(color_group))
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
        
        if player.money >= rent_amount:
            player.pay(rent_amount)
            current_property.owner.receive(rent_amount)
            log.append(f"Rent paid. Remaining money: ${player.money}")
            return log
            
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
            
        player.pay(rent_amount)
        current_property.owner.receive(rent_amount)
        log.append(f"After selling properties and paying rent, {player.name} has ${player.money} remaining")
        return log

    def execute_bankruptcy(self, bankrupt_player: Player, creditor: Player) -> List[str]:
        """Handle the bankruptcy of a player. Returns log of actions."""
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
    