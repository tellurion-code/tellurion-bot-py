"""Bot for playing the game as optimally as possible."""

import math
import random
import asyncio
from dataclasses import dataclass

from modules.petrigon.hex import AXIAL_DIRECTION_VECTORS
from modules.petrigon.player import Player


class TreeNode:
    """A node in the minmax tree."""
    def __init__(self, map, player, last_direction=None):
        self.map = map                          # The map at this node
        self.player = player                    # The player who played the last move
        self.children = {}                      # The children of this node (Dict<Hex,TreeNode>). The Hex is the direction chosen
        self.last_direction = last_direction    # The last direction chosen by the last player
        self.eval = None                        # The final evaluation given by the algorithm

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
        return hash(self.map) ^ self.player.id
    
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

    def evaluate(self, map):
        score = [self.evaluate_for_player(map, self.game.players[self.game.order[i]]) for i in self.game.order]
        return score
    
    def evaluate_for_player(self, map, player):
        return sum((map.size - hex.length + 1) ** 2 for hex, value in map.items() if value == player.index)

    async def start_turn(self, interaction=None):
        await super().start_turn(interaction)
        asyncio.create_task(self.take_move())

    async def take_move(self):
        # Wait to confirm the game has a panel
        while not self.game.panel: pass

        # We're unlikely to meet a transposition we've stored more than one turn ago
        self.transpositions = {i: x for i,x in self.transpositions.items() if x.turn < self.game.turn - 1}

        direction = self.find_best_direction()
        await self.game.handle_direction(direction)

    def find_best_direction(self):
        root = TreeNode(self.game.map, self)
        # turn = self.game.player_turn(self)
        # best_eval = self.maxn(root, self.upper_bound)[turn]

        # print(f"Evaluations for Bot {-self.id}")
        best_eval = self.brs(root)
        self.num_evaluated_positions = root.total_nodes
        # print(f"(Best: {best_eval}):\n" + '\n'.join(f"  {DIRECTIONS_TO_EMOJIS[x.last_direction]}  {x.eval}" for x in root.children.values()))
        best_node = max(root.children.values(), key=lambda x: x.eval, default=None)
        if best_node and best_node.eval < best_eval: print(f"Difference in eval and choice: {best_node.eval}/{best_eval}")

        return best_node.last_direction if best_node else random.choice(AXIAL_DIRECTION_VECTORS)
    
    def brs(self, node: TreeNode, alpha=-math.inf, beta=math.inf, maximising=True, depth=None):
        """
        Best Reply Search, as described in https://dke.maastrichtuniversity.nl/m.winands/documents/BestReplySearch.pdf,
        which can implement the full breadth of alpha-beta pruning,
        improved to BRS+ from https://www.researchgate.net/publication/259591343_Improving_Best-Reply_Search (TODO)
        """
        if depth == None: depth = self.depth * 2
        if depth == 0: return self.evaluate_for_player(node.map, self) * (1 if maximising else -1)

        if node in self.transpositions: return self.transpositions[node].evaluation

        for player in self.game.players.values():
            if maximising != (player.id == self.id): continue  # Only consider self on MAX nodes, and opponents on MIN nodes

            for direction in AXIAL_DIRECTION_VECTORS:
                next_result = player.move(node.map, direction)
                if not next_result.valid: continue
                child = TreeNode(next_result.map, player, direction)
                node.add_child(direction, child)

                # print(f"{'  ' * (self.depth * 2 - depth)}Checking {DIRECTIONS_TO_EMOJIS[direction]}  for {player}:")
                child.eval = -self.brs(child, alpha=-beta, beta=-alpha, depth=depth-1, maximising=not maximising)
                self.transpositions[child] = Transposition(child.eval, self.game.turn)
                # print(f"{'  ' * (self.depth * 2 - depth)}Result: {child.eval}")
                if child.eval >= beta: return child.eval  # Snip!
                alpha = max(alpha, child.eval)

        if len(node.children) == 0:  # If the node has no children, either we or all oponents can't move: either way, the current "team" has lost
            return -math.inf

        return alpha
    
    def __str__(self):
        return f"`🤖 Bot {-self.id}`" + (f" ({self.num_evaluated_positions}/{len(self.transpositions)})" if self.num_evaluated_positions else "")
