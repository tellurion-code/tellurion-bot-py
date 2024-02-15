"""Bot for playing the game as optimally as possible."""

import math
import random
from dataclasses import dataclass

from modules.petrigon.hex import AXIAL_DIRECTION_VECTORS
from modules.petrigon.player import Context, Player


class TreeNode:
    """A node in the minimax tree."""
    def __init__(self, map, players, maximising, powers_data, use_combination={}, last_direction=None):
        self.map = map                          # Game map at this node
        self.players = players                  # Players allowed to take a move from this node
        self.children = {}                      # Children of this node (Dict<Hex,TreeNode>). The Hex is the direction chosen
        self.last_direction = last_direction    # Last direction chosen by the last player
        self.eval = None                        # Final evaluation given by the algorithm
        self.players_powers_data = powers_data  # Data of the powers of each player (Dict<int,PowersData>)
        self.use_combination = use_combination  # Combinations of used powers this turn (Dict<str,int>)
        self.maximising = maximising            # Whether the node is a MAX or MIN node

    @property
    def depth(self):
        return max(x.depth for x in self.children.values()) + 1 if len(self.children) else 0
    
    @property
    def total_nodes(self):
        return sum(x.total_nodes for x in self.children.values()) if len(self.children) else 1

    def add_child(self, direction, node):
        self.children[direction] = node

    def remove_child(self, direction):
        del self.children[direction]

    def __hash__(self):
        h = hash(self.map)
        for player in self.players: h ^= hash(player)
        for data in self.players_powers_data.values(): h ^= hash(data)
        return h
    
    def __eq__(self, other):
        return isinstance(other, TreeNode) and hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other


@dataclass
class Transposition:
    evaluation: int
    turn: int


class GameBot(Player):
    def __init__(self, game, id, depth=1):
        super().__init__(game, None)
        self.id = id
        self.depth = depth

        self.transpositions = {}    # Dict<Node,Transposition> used to quickly get the evaluation of a move that was already evaluated
        self.num_evaluated_positions = None

    @property
    def upper_bound(self):
        return (sum(6*i * (self.game.map.size - i + 1) ** 2 for i in range(1, self.game.map.size+1)) + (self.game.map.size + 1) ** 2) / 3

    @property
    def other_players(self):
        return list(player for player in self.game.players.values() if player != self)

    def evaluate(self, context):
        score = [self.evaluate_for_player(context, self.game.players[self.game.order[i]]) for i in self.game.order]
        return score
    
    def evaluate_for_player(self, context, player):
        return sum((context.map.size - hex.length + 1) ** 2 for hex, value in context.map.items() if value == player.index)

    async def take_move(self):
        # Confirm the game has a panel (it's running)
        if not hasattr(self.game, "panel"): return

        # We're unlikely to meet a transposition we've stored more than one turn ago
        self.transpositions = {i: x for i,x in self.transpositions.items() if x.turn < self.game.turn - 1}

        direction = self.find_best_direction()
        await self.game.handle_direction(direction)

    def find_best_direction(self):
        root = TreeNode(
            self.game.map, 
            players=[self], 
            maximising=True, 
            powers_data={i: p.current_context.powers_data for i,p in self.game.players.items()}
        )
        # turn = self.game.player_turn(self)
        # best_eval = self.maxn(root, self.upper_bound)[turn]

        # print(f"Evaluations for Bot {-self.id}")
        best_eval = self.brs(root)
        self.num_evaluated_positions = root.total_nodes
        # print(f"(Best: {best_eval}):\n" + '\n'.join(f"  {DIRECTIONS_TO_EMOJIS[x.last_direction]}  {x.eval}" for x in root.children.values()))
        best_node = max(root.children.values(), key=lambda x: x.eval, default=None)
        # if best_node and best_node.eval < best_eval: print(f"Difference in eval and choice: {best_node.eval}/{best_eval}")

        return best_node.last_direction if best_node else random.choice(AXIAL_DIRECTION_VECTORS)
    
    def brs(self, node: TreeNode, alpha=-math.inf, beta=math.inf, depth=None):
        """
        Best Reply Search, as described in https://dke.maastrichtuniversity.nl/m.winands/documents/BestReplySearch.pdf,
        which can implement the full breadth of alpha-beta pruning,
        improved to BRS+ from https://www.researchgate.net/publication/259591343_Improving_Best-Reply_Search (TODO)
        """
        if depth is None: depth = self.depth * 2
        if depth == 0: return self.evaluate_for_player(node.map, self) * (1 if node.maximising else -1)

        if node in self.transpositions: return self.transpositions[node].evaluation

        for player in node.players:  # Only consider self on MAX nodes, and opponents on MIN nodes (or one opponent, if it's their extra turn)
            context = Context(node.map, node.players_powers_data[player.id])
            usable_powers_combinations = player.usable_powers_combinations(context)
            for direction in AXIAL_DIRECTION_VECTORS:
                context = player.start_turn(context)
                for combination in usable_powers_combinations:
                    context = player.use_powers_from_combination(context, combination)
                    result = player.move(context, direction)  # Calculate the next possible move
                    if not result.valid: continue
                    pass_turn, context = player.end_turn(result.context)

                    child = TreeNode(
                        context.map,
                        players=(self.other_players if node.maximising else [self]) if pass_turn else [player],
                        maximising=not node.maximising if pass_turn else node.maximising,
                        powers_data={i: v if i != player.id else context.powers_data for i,v in node.players_powers_data.items()},
                        use_combination=combination,
                        last_direction=direction
                    )
                    node.add_child(direction, child)

                    # print(f"{'  ' * (self.depth * 2 - depth)}Checking {DIRECTIONS_TO_EMOJIS[direction]}  for {player}:")
                    child.eval = self.brs(child, alpha=-beta, beta=-alpha, depth=depth-1) * (-1 if pass_turn else 1)
                    self.transpositions[child] = Transposition(child.eval, self.game.turn)
                    # print(f"{'  ' * (self.depth * 2 - depth)}Result: {child.eval}")
                    if child.eval >= beta: return child.eval  # Snip!
                    alpha = max(alpha, child.eval)

        if len(node.children) == 0:  # If the node has no children, either we or all oponents can't move: either way, the current "team" has lost
            return -math.inf

        return alpha
    
    def __str__(self):
        return f"`🤖 Bot {-self.id}`" + (f" ({self.num_evaluated_positions}/{len(self.transpositions)})" if self.num_evaluated_positions else "")
