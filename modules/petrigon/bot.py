"""Bot for playing the game as optimally as possible."""

import math
import random
from dataclasses import dataclass

from modules.petrigon.hex import AXIAL_DIRECTION_VECTORS, DIRECTIONS_TO_EMOJIS
from modules.petrigon.player import Player
from modules.petrigon.power import ActivePower
from modules.petrigon.zobrist import zobrist_hash


@zobrist_hash(fields=('context',))
class TreeNode:
    """A node in the minimax tree."""
    def __init__(self, context, maximising, use_combination={}, last_direction=None):
        self.context = context                  # Game state at this node
        self.maximising = maximising            # Whether the node is a MAX or MIN node
        self.use_combination = use_combination  # Combinations of used powers this turn (Dict<str,int>)
        self.last_direction = last_direction    # Last direction chosen by the last player

        self.children = []                      # Children of this node (Dict<Hex,TreeNode>). The Hex is the direction chosen
        self.eval = None                        # Final evaluation given by the algorithm

    @property
    def depth(self):
        return max(x.depth for x in self.children) + 1 if len(self.children) else 0
    
    @property
    def total_nodes(self):
        return sum(x.total_nodes for x in self.children) if len(self.children) else 1

    def add_child(self, node):
        self.children.append(node)

    def __str__(self):
        return f"{DIRECTIONS_TO_EMOJIS.get(self.last_direction)}  {', '.join(i + ': ' + str(x) for i,x in self.use_combination.items())}: {self.eval}"
    
    def __eq__(self, other):
        return isinstance(other, TreeNode) and hash(self) == hash(other)

    def __ne__(self, other):
        return not self == other


@dataclass
class Transposition:
    evaluation: int
    turn: int
    maximising: bool


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
        def distance_to_edge(context, hex): return (context.map.size - hex.length + 1)
        map_eval = sum(distance_to_edge(context, hex) for hex, value in context.map.items() if value == player.index)

        POWER_USES_INCENTIVE = 250
        powers_eval = sum(x.uses for x in self.powers_data_from_context(context).values() if isinstance(x, ActivePower)) * POWER_USES_INCENTIVE
        return map_eval + powers_eval

    async def take_move(self):
        # Confirm the game has a panel (it's running)
        if not hasattr(self.game, "panel"): return

        # We're unlikely to meet a transposition we've stored more than one turn ago
        self.transpositions = {i: x for i,x in self.transpositions.items() if x.turn < self.game.turn - 1}

        direction, use_combination = self.find_best_action()
        
        context = self.use_powers_from_combination(self.game.current_context, use_combination, with_announcements=True)
        if context: self.apply_powers_data(context)
        
        await self.game.handle_direction(direction)

    def find_best_action(self):
        root = TreeNode(
            self.game.current_context,
            maximising=True
        )
        # turn = self.game.player_turn(self)
        # best_eval = self.maxn(root, self.upper_bound)[turn]

        # print(f"Evaluations for Bot {-self.id}")
        best_eval = self.brs(root)
        self.num_evaluated_positions = root.total_nodes
        # self.print_tree(root)
        # print(f"(Best: {best_eval}):\n" + '\n'.join(f"  {x}" for x in root.children))

        # Decision: best evaluation, then least power uses, then random choice
        best_node = max(root.children, key=lambda x: (x.eval, -sum(x.use_combination.values()), random.random()), default=None)
        # if best_node and best_node.eval < best_eval: print(f"Difference in eval and choice: {best_node.eval}/{best_eval}")

        return (best_node.last_direction, best_node.use_combination) if best_node else (random.choice(AXIAL_DIRECTION_VECTORS), {})

    def print_tree(self, root, markerStr="+- ", levelMarkers=[]):
        emptyStr = " " * len(markerStr)
        connectionStr = "|" + emptyStr[:-1]
        level = len(levelMarkers)
        mapper = lambda draw: connectionStr if draw else emptyStr
        markers = "".join(map(mapper, levelMarkers[:-1]))
        markers += markerStr if level > 0 else ""
        print(f"{markers}{root}")
        for i, child in enumerate(root.children):
            isLast = i == len(root.children) - 1
            self.print_tree(child, markerStr, [*levelMarkers, not isLast])
    
    def brs(self, node: TreeNode, *, alpha=-math.inf, beta=math.inf, depth=None):
        """
        Best Reply Search, as described in https://dke.maastrichtuniversity.nl/m.winands/documents/BestReplySearch.pdf,
        which can implement the full breadth of alpha-beta pruning,
        improved to Althöfer's algorithm from https://www.mdpi.com/1999-4893/5/4/521,
        and improved to BRS+ from https://www.researchgate.net/publication/259591343_Improving_Best-Reply_Search (TODO)
        """
        if depth is None: depth = self.depth * 2

        evaluation = self.evaluate_for_player(node.context, self)
        if node in self.transpositions:
            transposition = self.transpositions[node]
            return transposition.evaluation * (-1 if transposition.maximising != node.maximising else 1)

        if depth == 0: return evaluation * (1 if node.maximising else -1)
        
        alpha -= evaluation
        for child in self.explore_children(node):
            node.add_child(child)

            # print(f"{'  ' * (self.depth * 2 - depth)}Checking {child}:")
            child_evaluation = -self.brs(child, alpha=-beta+evaluation, beta=-alpha, depth=depth-1)
            child.eval = child_evaluation + self.evaluate_for_player(child.context, self)
            self.transpositions[child] = Transposition(child_evaluation, self.game.turn, maximising=node.maximising)
            # print(f"{'  ' * (self.depth * 2 - depth)}Result: {child.eval}")
            alpha = max(alpha, child_evaluation)
            if alpha + evaluation >= beta: break  # Snip!
            # print(f"{'  ' * (self.depth * 2 - depth)}Updating alpha to {child.eval}")

        if len(node.children) == 0:  # If the node has no children, either we or all oponents can't move: either way, the current "team" has lost
            return -math.inf

        return alpha + evaluation
    
    def explore_children(self, node: TreeNode, extra_turn_of=None):
        players = [extra_turn_of] if extra_turn_of else ([self] if node.maximising else self.other_players)
        new_maximising = not node.maximising if extra_turn_of is None else node.maximising

        for player in players:  # Only consider self on MAX nodes, and opponents on MIN nodes (or one opponent, if it's their extra turn)
            powers_combinations = player.usable_powers_combinations(node.context)
            for direction in AXIAL_DIRECTION_VECTORS:
                turn_context = player.start_turn(node.context)
                for combination in powers_combinations:
                    # print(f"Using combination: {', '.join(i + ': ' + str(x) for i,x in combination.items())}")
                    power_context = player.use_powers_from_combination(turn_context, combination)
                    result = player.move(power_context, direction)  # Calculate the next possible move
                    if not result.valid: continue
                    pass_turn, play_context = player.end_turn(result)

                    child = TreeNode(
                        play_context,
                        maximising=new_maximising,
                        last_direction=direction if extra_turn_of is None else node.last_direction,
                        use_combination=combination if extra_turn_of is None else node.use_combination
                    )

                    if pass_turn:
                        yield child
                    else:  # We're playing a second turn: flatten the grandchildren as children
                        for grandchild in self.explore_children(child, extra_turn_of=player): yield grandchild
    
    def player_name(self, show_name=False):
        if self.game.tournament and not show_name: return super().player_name(show_name=False)
        return f"`🤖 Bot {-self.id}`" + (f" ({self.num_evaluated_positions}/{len(self.transpositions)})" if self.num_evaluated_positions else "")
