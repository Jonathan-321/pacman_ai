from abc import ABC, abstractmethod
from typing import List, Tuple, Set, Deque, Dict
from collections import deque
from queue import PriorityQueue
import math

class SearchAlgorithm(ABC):
    @abstractmethod
    def find_path(self, start: Tuple[int, int], 
                 goals: List[Tuple[int, int]], 
                 maze) -> List[Tuple[int, int]]:
        """Find a path from start to the nearest goal"""
        pass

class BreadthFirstSearch(SearchAlgorithm):
    def find_path(self, start: Tuple[int, int], 
                 goals: List[Tuple[int, int]], 
                 maze) -> List[Tuple[int, int]]:
        """
        Implements BFS to find the shortest path to the nearest goal
        Returns: List of positions forming the path
        """
        if not goals:
            return []
        
        # Convert goals to set for O(1) lookup
        goal_set = set(goals)
        
        # Queue stores (position, path)
        queue = deque([(start, [start])])
        visited = {start}
        
        # Possible movements (up, right, down, left)
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        while queue:
            current, path = queue.popleft()
            
            # Check if current position is a goal
            if current in goal_set:
                return path[1:]  # Exclude start position
            
            # Try all possible movements
            for dx, dy in directions:
                next_x, next_y = current[0] + dx, current[1] + dy
                next_pos = (next_x, next_y)
                
                if (next_pos not in visited and 
                    maze.is_valid_position(next_x, next_y)):
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
        
        return []  # No path found

class AStarSearch(SearchAlgorithm):
    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Manhattan distance heuristic"""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    def find_path(self, start: Tuple[int, int], 
                 goals: List[Tuple[int, int]], 
                 maze) -> List[Tuple[int, int]]:
        """
        Implements A* search to find the optimal path to the nearest goal
        Returns: List of positions forming the path
        """
        if not goals:
            return []
        
        # Find nearest goal using Manhattan distance
        nearest_goal = min(goals, key=lambda g: self.heuristic(start, g))
        
        # Priority queue stores (f_score, position, path)
        open_set = PriorityQueue()
        open_set.put((0, start, [start]))
        
        # Track g_scores (cost from start to node)
        g_scores = {start: 0}
        
        # Track visited nodes
        visited = {start}
        
        # Possible movements
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        while not open_set.empty():
            _, current, path = open_set.get()
            
            if current == nearest_goal:
                return path[1:]  # Exclude start position
            
            for dx, dy in directions:
                next_x, next_y = current[0] + dx, current[1] + dy
                next_pos = (next_x, next_y)
                
                if maze.is_valid_position(next_x, next_y):
                    # Calculate g_score for neighbor
                    tentative_g = g_scores[current] + 1
                    
                    if next_pos not in g_scores or tentative_g < g_scores[next_pos]:
                        g_scores[next_pos] = tentative_g
                        f_score = tentative_g + self.heuristic(next_pos, nearest_goal)
                        
                        if next_pos not in visited:
                            visited.add(next_pos)
                            open_set.put((f_score, next_pos, path + [next_pos]))
        
        return []  # No path found

class UniformCostSearch(SearchAlgorithm):
    def find_path(self, start: Tuple[int, int], 
                 goals: List[Tuple[int, int]], 
                 maze) -> List[Tuple[int, int]]:
        """
        Implements Uniform Cost Search to find the lowest-cost path
        Returns: List of positions forming the path
        """
        if not goals:
            return []
        
        # Convert goals to set for O(1) lookup
        goal_set = set(goals)
        
        # Priority queue stores (cost, position, path)
        queue = PriorityQueue()
        queue.put((0, start, [start]))
        
        # Track visited nodes and their costs
        visited = {start: 0}
        
        # Possible movements
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        while not queue.empty():
            cost, current, path = queue.get()
            
            if current in goal_set:
                return path[1:]  # Exclude start position
            
            for dx, dy in directions:
                next_x, next_y = current[0] + dx, current[1] + dy
                next_pos = (next_x, next_y)
                
                # Calculate new cost (assume cost of 1 for each move)
                new_cost = cost + 1
                
                if (maze.is_valid_position(next_x, next_y) and 
                    (next_pos not in visited or new_cost < visited[next_pos])):
                    visited[next_pos] = new_cost
                    queue.put((new_cost, next_pos, path + [next_pos]))
        
        return []  # No path found