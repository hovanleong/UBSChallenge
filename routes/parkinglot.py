import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the level of the logger

# Create a file handler
file_handler = logging.FileHandler('app.parkinglot.log')  # Name of the file where logs will be written
file_handler.setLevel(logging.DEBUG)  # Set the logging level for the file handler

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)  # Apply the formatter to the handler

# Add the file handler to the logger
logger.addHandler(file_handler)

NORTH, SOUTH, EAST, WEST = "NORTH", "SOUTH", "EAST", "WEST"

class VehicleCannotFitException(Exception):
    def __init__(self, vehicle, reason):
        self.vehicle = vehicle
        self.reason = reason
        super().__init__(f"Vehicle {vehicle.plateNumber} cannot fit: {reason}")

class ParkingLot:
    def __init__(self, grid):
        self.grid = grid  # 2D array representing the parking lot
        self.occupied = set()  # Keep track of occupied spots (x, y)

    def display_lot(self):
        """Display the current state of the parking lot"""
        for row in self.grid:
            print(' '.join(row))
        print()

    def can_fit(self, vehicle, x, y):
        """Check if a vehicle can fit in the parking lot at the given (x, y) location"""
        # Determine required area based on vehicle's orientation (direction)
        if vehicle.direction in [EAST, WEST]:
            required_length = vehicle.length
            required_width = vehicle.width
        else:  # NORTH, SOUTH direction
            required_length = vehicle.width
            required_width = vehicle.length

        # Check if the vehicle's position fits within the grid and doesn't hit walls/other vehicles
        for i in range(required_length):
            for j in range(required_width):
                new_x, new_y = x + i, y + j
                if not self.is_within_bounds(new_x, new_y) or self.grid[new_x][new_y] != " ":
                    raise VehicleCannotFitException(vehicle, f"Collision or boundary issue at position {(new_x, new_y)}")
        return True

    def is_within_bounds(self, x, y):
        """Check if a position is within the bounds of the parking lot"""
        return 1 <= x < len(self.grid) - 1 and 1 <= y < len(self.grid[0]) - 1

    def park_vehicle(self, vehicle, x, y):
        """Attempt to park a vehicle at the given (x, y) position"""
        if self.can_fit(vehicle, x, y):
            # If the vehicle fits, mark its position on the parking lot grid
            self.mark_occupied(vehicle, x, y)
            print(f"Vehicle {vehicle.plateNumber} parked at ({x}, {y}) facing {vehicle.direction}")
            self.display_lot()

    def mark_occupied(self, vehicle, x, y):
        """Mark the grid as occupied by the vehicle"""
        # Determine the space occupied by the vehicle based on its direction
        if vehicle.direction in [NORTH, SOUTH]:
            required_length = vehicle.length
            required_width = vehicle.width
        else:
            required_length = vehicle.width
            required_width = vehicle.length

        for i in range(required_length):
            for j in range(required_width):
                self.grid[x + i][y + j] = "V"  # Marking the space as occupied by the vehicle
                self.occupied.add((x + i, y + j))

    def exit_vehicle(self, vehicle, x, y):
        """Remove a vehicle from the parking lot, freeing its space"""
        print(f"Vehicle {vehicle.plateNumber} exiting from ({x}, {y})")
        self.clear_occupied(vehicle, x, y)
        self.display_lot()

    def clear_occupied(self, vehicle, x, y):
        """Clear the space occupied by the vehicle"""
        # Determine the space occupied by the vehicle based on its direction
        if vehicle.direction in [NORTH, SOUTH]:
            required_length = vehicle.length
            required_width = vehicle.width
        else:
            required_length = vehicle.width
            required_width = vehicle.length

        for i in range(required_length):
            for j in range(required_width):
                self.grid[x + i][y + j] = " "  # Clear the space
                self.occupied.remove((x + i, y + j))

# Base Vehicle class
class Vehicle:
    def __init__(self, plateNumber, length, width, parkingFare, x, y, direction):
        self.plateNumber = plateNumber
        self.length = length
        self.width = width
        self.parkingFare = parkingFare
        self.x = x  # Current x-coordinate of the vehicle's top-left corner
        self.y = y  # Current y-coordinate of the vehicle's top-left corner
        self.direction = direction  # Initial direction (NORTH, SOUTH, EAST, WEST)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.plateNumber}, x={self.x}, y={self.y}, direction={self.direction})"
    
    def forward_left(direction):
        if direction == NORTH:
            return WEST
        elif direction == WEST:
            return SOUTH
        elif direction == SOUTH:
            return EAST
        elif direction == EAST:
            return NORTH

    def forward_right(direction):
        if direction == NORTH:
            return EAST
        elif direction == EAST:
            return SOUTH
        elif direction == SOUTH:
            return WEST
        elif direction == WEST:
            return NORTH
        
    def reverse_left(direction):
        if direction == NORTH:
            return EAST
        elif direction == WEST:
            return NORTH
        elif direction == SOUTH:
            return WEST
        elif direction == EAST:
            return SOUTH

    def reverse_right(direction):
        if direction == NORTH:
            return WEST
        elif direction == EAST:
            return NORTH
        elif direction == SOUTH:
            return EAST
        elif direction == WEST:
            return SOUTH
        
    def move_backward(x, y, direction):
        if direction == NORTH:
            return x, y + 1
        elif direction == SOUTH:
            return x, y - 1
        elif direction == EAST:
            return x - 1, y
        elif direction == WEST:
            return x + 1, y
        
    def move_forward(x, y, direction):
        if direction == NORTH:
            return x, y - 1
        elif direction == SOUTH:
            return x, y + 1
        elif direction == EAST:
            return x + 1, y
        elif direction == WEST:
            return x - 1, y

    # Turn left (counter-clockwise)
    def turn_left(self):
        self.direction = self.turn_left(self.direction)

    # Turn right (clockwise)
    def turn_right(self):
        self.direction = self.turn_right(self.direction)

# Subclass for Motorcycle
class Motorcycle(Vehicle):
    def __init__(self, plateNumber, x, y, direction):
        super().__init__(plateNumber, length=2, width=1, parkingFare=1, x=x, y=y, direction=direction)

    def move_backward(x, y, direction):
        if direction == NORTH:
            return x, y + 1
        elif direction == SOUTH:
            return x, y - 1
        elif direction == EAST:
            return x - 1, y
        elif direction == WEST:
            return x + 1, y
        
    def move_forward(x, y, direction):
        if direction == NORTH:
            return x, y - 1
        elif direction == SOUTH:
            return x, y + 1
        elif direction == EAST:
            return x + 1, y
        elif direction == WEST:
            return x - 1, y

# Subclass for Car
class Car(Vehicle):
    def __init__(self, plateNumber, x, y, direction):
        super().__init__(plateNumber, length=3, width=2, parkingFare=5, x=x, y=y, direction=direction)

# Subclass for Truck
class Truck(Vehicle):
    def __init__(self, plateNumber, x, y, direction):
        super().__init__(plateNumber, length=5, width=2, parkingFare=10, x=x, y=y, direction=direction)

def process_test_case(test_case):
    minimum_fare = test_case["minimumTotalFare"]
    parking_lot_layout = test_case["parkingLot"]
    actions = test_case["actions"]
    
    # Initialize the parking lot
    parking_lot = ParkingLot(parking_lot_layout)

    entrances = []
    exits = []
    for y, row in enumerate(parking_lot):
        for x, cell in enumerate(row):
            if cell == 'I':
                entrances.append((x, y))
            elif cell == 'O':
                exits.append((x, y))
    
    # Create a dictionary to store vehicles by plate number
    vehicle_dict = {}
    
    # Instantiate vehicles
    for vehicle_data in test_case["vehicles"]:
        plate = vehicle_data["plateNumber"]
        length = vehicle_data["length"]
        width = vehicle_data["width"]
        fare = vehicle_data["parkingFare"]
        
        if length == 2 and width == 1:
            vehicle = Motorcycle(plate, x=0, y=0, direction=EAST)  # Placeholder direction and position
        elif length == 3 and width == 2:
            vehicle = Car(plate, x=0, y=0, direction=EAST)
        elif length == 5 and width == 2:
            vehicle = Truck(plate, x=0, y=0, direction=EAST)
        else:
            continue  # Unknown vehicle type
        
        vehicle_dict[plate] = vehicle

    # Track total fare
    total_fare = 0

    # List to store results of actions
    result_actions = []

    # Process each action (parking or exiting)
    for action in actions:
        plate = action["plateNumber"]
        action_type = action["action"]
        vehicle = vehicle_dict.get(plate)
        
        if action_type == "park":
            # Try to park the vehicle at an entrance
            try:
                # Try to park at a specific entrance (you can choose a more sophisticated logic for entrances)
                entrance_x, entrance_y = 1, 1
                parking_lot.park_vehicle(vehicle, entrance_x, entrance_y)
                result_actions.append({
                    "plateNumber": plate,
                    "action": "park",
                    "execute": True,
                    "position": {"x": entrance_x, "y": entrance_y, "direction": vehicle.direction}
                })
            except VehicleCannotFitException as e:
                result_actions.append({
                    "plateNumber": plate,
                    "action": "park",
                    "execute": False,
                    "position": None
                })

        elif action_type == "exit":
            # Try to exit the vehicle from the parking lot
            try:
                exit_x, exit_y = 4, 5  # Example exit coordinates
                parking_lot.exit_vehicle(vehicle, exit_x, exit_y)
                total_fare += vehicle.parkingFare
                result_actions.append({
                    "plateNumber": plate,
                    "action": "exit",
                    "execute": True,
                    "position": {"x": exit_x, "y": exit_y, "direction": vehicle.direction}
                })
            except Exception as e:
                result_actions.append({
                    "plateNumber": plate,
                    "action": "exit",
                    "execute": False,
                    "position": None
                })
    
    return result_actions

# Example of handling multiple test cases
def handle_parking_lot_tests(test_cases):
    all_results = []
    for test_case in test_cases:
        result_actions = process_test_case(test_case)
        all_results.append({
            "actions": result_actions
        })
    return all_results

@app.route('/parkinglot', methods=['POST'])
def tourist():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    result = handle_parking_lot_tests(data)
    logging.info("My result :{}".format(result))
    return json.dumps(result)