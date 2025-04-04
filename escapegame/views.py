from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    EscapeRoom, Room, Puzzle, InventoryItem, 
    ItemLocation, GameSession, GameEvent
)
from .serializers import (
    EscapeRoomSerializer, EscapeRoomDetailSerializer, RoomSerializer,
    PuzzleSerializer, InventoryItemSerializer, GameSessionSerializer,
    GameEventSerializer, PuzzleAttemptSerializer, ItemInteractionSerializer
)
from .permissions import IsOwnerOrReadOnly, IsGameSessionOwner

class EscapeRoomViewSet(viewsets.ModelViewSet):
    """API endpoint for escape rooms"""
    queryset = EscapeRoom.objects.all()
    serializer_class = EscapeRoomSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return EscapeRoom.objects.all()
        elif user.is_authenticated:
            return EscapeRoom.objects.filter(
                Q(is_published=True) | Q(created_by=user)
            )
        else:
            return EscapeRoom.objects.filter(is_published=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EscapeRoomDetailSerializer
        return EscapeRoomSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start_game(self, request, pk=None):
        """Start a new game session for the escape room"""
        escape_room = self.get_object()
        
        # Find the starting room
        starting_room = escape_room.rooms.filter(is_starting_room=True).first()
        if not starting_room:
            return Response(
                {"error": "This escape room has no starting room defined."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new game session
        session = GameSession.objects.create(
            user=request.user,
            escape_room=escape_room,
            current_room=starting_room,
            game_state={
                'inventory': [],
                'solved_puzzles': [],
                'unlocked_rooms': [str(starting_room.id)],
                'hints_used': 0
            }
        )
        
        # Log the game start event
        GameEvent.objects.create(
            session=session,
            event_type='game_started',
            event_data={'room_id': str(starting_room.id)}
        )
        
        serializer = GameSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for rooms within escape rooms"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        escape_room_id = self.request.query_params.get('escape_room', None)
        if escape_room_id:
            return Room.objects.filter(escape_room__id=escape_room_id)
        return Room.objects.none()

class GameSessionViewSet(viewsets.ModelViewSet):
    """API endpoint for game sessions"""
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsGameSessionOwner]
    
    def get_queryset(self):
        return GameSession.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def move_to_room(self, request, pk=None):
        """Move to another room in the escape room"""
        session = self.get_object()
        room_id = request.data.get('room_id')
        
        if not room_id:
            return Response(
                {"error": "Room ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the room exists and is part of the escape room
        try:
            target_room = Room.objects.get(id=room_id, escape_room=session.escape_room)
        except Room.DoesNotExist:
            return Response(
                {"error": "Room not found in this escape room."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the room is unlocked
        unlocked_rooms = session.game_state.get('unlocked_rooms', [])
        if str(target_room.id) not in unlocked_rooms:
            return Response(
                {"error": "This room is locked."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the current room
        session.current_room = target_room
        session.save()
        
        # Log the room change event
        GameEvent.objects.create(
            session=session,
            event_type='room_changed',
            event_data={'room_id': str(target_room.id)}
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def solve_puzzle(self, request, pk=None):
        """Attempt to solve a puzzle"""
        session = self.get_object()
        serializer = PuzzleAttemptSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        puzzle_id = serializer.validated_data['puzzle_id']
        solution_attempt = serializer.validated_data['solution_attempt']
        
        # Check if the puzzle exists and is in the current room
        try:
            puzzle = Puzzle.objects.get(
                id=puzzle_id, 
                room=session.current_room
            )
        except Puzzle.DoesNotExist:
            return Response(
                {"error": "Puzzle not found in current room."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the puzzle is already solved
        solved_puzzles = session.game_state.get('solved_puzzles', [])
        if str(puzzle_id) in solved_puzzles:
            return Response(
                {"message": "This puzzle is already solved."},
                status=status.HTTP_200_OK
            )
        
        # Check if the solution is correct
        is_correct = self._check_puzzle_solution(puzzle, solution_attempt)
        
        # Log the attempt
        GameEvent.objects.create(
            session=session,
            event_type='puzzle_attempt',
            event_data={
                'puzzle_id': str(puzzle_id),
                'success': is_correct
            }
        )
        
        if is_correct:
            # Mark the puzzle as solved
            session.mark_puzzle_solved(str(puzzle_id))
            
            # Check if this unlocks any rooms
            self._check_room_unlocks(session)
            
            return Response({"success": True, "message": "Puzzle solved correctly!"})
        else:
            return Response(
                {"success": False, "message": "Incorrect solution."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def interact_with_item(self, request, pk=None):
        """Interact with an item (collect, use, combine)"""
        session = self.get_object()
        serializer = ItemInteractionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        item_id = serializer.validated_data['item_id']
        action = serializer.validated_data['action']
        target_id = serializer.validated_data.get('target_id')
        
        # Process the interaction based on the action
        if action == 'collect':
            return self._collect_item(session, item_id)
        elif action == 'use':
            return self._use_item(session, item_id, target_id)
        elif action == 'combine':
            return self._combine_items(session, item_id, target_id)
        else:
            return Response(
                {"error": "Invalid action. Supported actions: collect, use, combine"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def request_hint(self, request, pk=None):
        """Request a hint for a puzzle"""
        session = self.get_object()
        puzzle_id = request.data.get('puzzle_id')
        
        if not puzzle_id:
            return Response(
                {"error": "Puzzle ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the puzzle exists
        try:
            puzzle = Puzzle.objects.get(id=puzzle_id)
        except Puzzle.DoesNotExist:
            return Response(
                {"error": "Puzzle not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Increment the hints used counter
        if 'hints_used' not in session.game_state:
            session.game_state['hints_used'] = 0
        
        session.game_state['hints_used'] += 1
        session.save()
        
        # Log the hint request
        GameEvent.objects.create(
            session=session,
            event_type='hint_requested',
            event_data={'puzzle_id': str(puzzle_id)}
        )
        
        return Response({
            "hint": puzzle.hint_text,
            "hints_used": session.game_state['hints_used']
        })
    
    @action(detail=True, methods=['post'])
    def complete_game(self, request, pk=None):
        """Mark the game as completed"""
        session = self.get_object()
        
        # Check if the player is in the final room
        if not session.current_room.is_final_room:
            return Response(
                {"error": "You must reach the final room to complete the game."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark the session as completed
        session.is_completed = True
        session.end_time = timezone.now()
        
        # Calculate time spent
        time_spent = session.end_time - session.start_time
        session.time_spent_seconds = int(time_spent.total_seconds())
        session.save()
        
        # Log the game completion
        GameEvent.objects.create(
            session=session,
            event_type='game_completed',
            event_data={
                'time_spent_seconds': session.time_spent_seconds,
                'hints_used': session.game_state.get('hints_used', 0)
            }
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    def _check_puzzle_solution(self, puzzle, solution_attempt):
        """Check if the provided solution matches the puzzle's solution"""
        correct_solution = puzzle.solution
        
        # Different puzzle types might have different solution formats
        if puzzle.puzzle_type == 'CODE':
            # For code puzzles, just compare the code
            return solution_attempt.get('code') == correct_solution.get('code')
        
        elif puzzle.puzzle_type == 'SEQUENCE':
            # For sequence puzzles, compare the sequence
            return solution_attempt.get('sequence') == correct_solution.get('sequence')
        
        elif puzzle.puzzle_type == 'SWITCHES':
            # For switch puzzles, compare the switch states
            return solution_attempt.get('switches') == correct_solution.get('switches')
        
        elif puzzle.puzzle_type == 'TERMINAL':
            # For terminal puzzles, compare the command
            return solution_attempt.get('command') == correct_solution.get('command')
        
        elif puzzle.puzzle_type == 'QUIZ':
            # For quizzes, check the answers
            return solution_attempt.get('answers') == correct_solution.get('answers')
        
        # For custom puzzles, do a direct comparison
        return solution_attempt == correct_solution
    
    def _check_room_unlocks(self, session):
        """Check if any rooms should be unlocked based on solved puzzles"""
        # Get all connections from the current room
        connections = session.current_room.connections_from.filter(is_locked=True)
        
        for connection in connections:
            if not connection.unlock_condition:
                continue
            
            # Check if the unlock condition is met
            condition_type = connection.unlock_condition.get('type')
            
            if condition_type == 'puzzle_solved':
                # Check if the required puzzle is solved
                puzzle_id = connection.unlock_condition.get('puzzle_id')
                solved_puzzles = session.game_state.get('solved_puzzles', [])
                
                if puzzle_id in solved_puzzles:
                    # Unlock the room
                    session.unlock_room(str(connection.to_room.id))
            
            elif condition_type == 'all_puzzles_solved':
                # Check if all puzzles in the room are solved
                room_puzzles = session.current_room.puzzles.all()
                puzzle_ids = [str(p.id) for p in room_puzzles]
                solved_puzzles = session.game_state.get('solved_puzzles', [])
                
                if all(pid in solved_puzzles for pid in puzzle_ids):
                    # Unlock the room
                    session.unlock_room(str(connection.to_room.id))
    
    def _collect_item(self, session, item_id):
        """Collect an item and add it to inventory"""
        # Check if the item exists in the current room
        try:
            item_location = ItemLocation.objects.get(
                item__id=item_id,
                room=session.current_room
            )
        except ItemLocation.DoesNotExist:
            return Response(
                {"error": "Item not found in current room."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the item is hidden and if it should be revealed
        if item_location.is_hidden:
            if not self._check_reveal_condition(session, item_location.reveal_condition):
                return Response(
                    {"error": "This item is not available yet."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Add the item to inventory
        session.add_to_inventory(str(item_id))
        
        # Log the item collection
        GameEvent.objects.create(
            session=session,
            event_type='item_collected',
            event_data={'item_id': str(item_id)}
        )
        
        return Response({
            "success": True,
            "message": f"Added {item_location.item.name} to inventory",
            "item": InventoryItemSerializer(item_location.item).data
        })
    
    def _use_item(self, session, item_id, target_id):
        """Use an item on a target (puzzle or another item)"""
        # Check if the item is in inventory
        inventory = session.game_state.get('inventory', [])
        if str(item_id) not in inventory:
            return Response(
                {"error": "This item is not in your inventory."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If no target specified, just return item details
        if not target_id:
            try:
                item = InventoryItem.objects.get(id=item_id)
                return Response({
                    "message": f"You are holding {item.name}",
                    "item": InventoryItemSerializer(item).data
                })
            except InventoryItem.DoesNotExist:
                return Response(
                    {"error": "Item not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Check if target is a puzzle
        try:
            puzzle = Puzzle.objects.get(id=target_id, room=session.current_room)
            # Log the item use on puzzle
            GameEvent.objects.create(
                session=session,
                event_type='item_used',
                event_data={
                    'item_id': str(item_id),
                    'target_type': 'puzzle',
                    'target_id': str(target_id)
                }
            )
            
            # Check if this item is needed for the puzzle
            if puzzle.configuration.get('required_item') == str(item_id):
                return Response({
                    "success": True,
                    "message": "Item used successfully on puzzle.",
                    "effect": "puzzle_unlocked"
                })
            else:
                return Response({
                    "success": False,
                    "message": "This item doesn't work with this puzzle."
                })
        except Puzzle.DoesNotExist:
            # Not a puzzle, continue checking
            pass
        
        # Check if target is another item in the room
        try:
            target_location = ItemLocation.objects.get(
                item__id=target_id,
                room=session.current_room
            )
            
            # Log the item use on another item
            GameEvent.objects.create(
                session=session,
                event_type='item_used',
                event_data={
                    'item_id': str(item_id),
                    'target_type': 'item',
                    'target_id': str(target_id)
                }
            )
            
            return Response({
                "success": True,
                "message": f"You used the item on {target_location.item.name}."
            })
        except ItemLocation.DoesNotExist:
            return Response(
                {"error": "Target not found in current room."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _combine_items(self, session, item_id, target_id):
        """Combine two items to create a new one"""
        # Check if both items are in inventory
        inventory = session.game_state.get('inventory', [])
        if str(item_id) not in inventory or str(target_id) not in inventory:
            return Response(
                {"error": "Both items must be in your inventory to combine them."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the items can be combined
        try:
            item1 = InventoryItem.objects.get(id=item_id)
            item2 = InventoryItem.objects.get(id=target_id)
        except InventoryItem.DoesNotExist:
            return Response(
                {"error": "One or both items not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if item1 can be combined with item2 to create a new item
        if item1.can_be_combined and item1.combination_result:
            # Check if item2 is a component for the combination
            components = item1.combination_result.components.all()
            if item2 in components:
                # Create the new item
                result_item = item1.combination_result
                
                # Remove the component items from inventory
                inventory.remove(str(item_id))
                inventory.remove(str(target_id))
                
                # Add the result item to inventory
                session.add_to_inventory(str(result_item.id))
                
                # Log the item combination
                GameEvent.objects.create(
                    session=session,
                    event_type='items_combined',
                    event_data={
                        'item1_id': str(item_id),
                        'item2_id': str(target_id),
                        'result_id': str(result_item.id)
                    }
                )
                
                return Response({
                    "success": True,
                    "message": f"Combined items to create {result_item.name}",
                    "new_item": InventoryItemSerializer(result_item).data
                })
        
        # Check the reverse combination (item2 + item1)
        if item2.can_be_combined and item2.combination_result:
            components = item2.combination_result.components.all()
            if item1 in components:
                # Create the new item
                result_item = item2.combination_result
                
                # Remove the component items from inventory
                inventory.remove(str(item_id))
                inventory.remove(str(target_id))
                
                # Add the result item to inventory
                session.add_to_inventory(str(result_item.id))
                
                # Log the item combination
                GameEvent.objects.create(
                    session=session,
                    event_type='items_combined',
                    event_data={
                        'item1_id': str(item_id),
                        'item2_id': str(target_id),
                        'result_id': str(result_item.id)
                    }
                )
                
                return Response({
                    "success": True,
                    "message": f"Combined items to create {result_item.name}",
                    "new_item": InventoryItemSerializer(result_item).data
                })
        
        return Response({
            "success": False,
            "message": "These items cannot be combined."
        })
    
    def _check_reveal_condition(self, session, condition):
        """Check if a reveal condition is met"""
        if not condition:
            return False
        
        condition_type = condition.get('type')
        
        if condition_type == 'puzzle_solved':
            # Check if the required puzzle is solved
            puzzle_id = condition.get('puzzle_id')
            solved_puzzles = session.game_state.get('solved_puzzles', [])
            return puzzle_id in solved_puzzles
        
        elif condition_type == 'item_in_inventory':
            # Check if the required item is in inventory
            item_id = condition.get('item_id')
            inventory = session.game_state.get('inventory', [])
            return item_id in inventory
        
        return False

class GameEventViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for game events"""
    serializer_class = GameEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.request.query_params.get('session', None)
        if session_id:
            return GameEvent.objects.filter(
                session__id=session_id,
                session__user=self.request.user
            )
        return GameEvent.objects.none()
