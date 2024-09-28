import json
import logging

from flask import request

from routes import app
import traceback

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
        self.grid_len_x = len(grid[0])
        self.grid_len_y = len(grid)
        self.occupied = set()  # Keep track of occupied spots (x, y)

        logger.info(f"({grid[1][0]}, {grid[self.grid_len_y-2][self.grid_len_x-1]})")

        self.entrance_dir = EAST if grid[1][0] == "I" else SOUTH
        self.exit_dir = EAST if grid[self.grid_len_y-2][self.grid_len_x-1] == "O" else SOUTH

        if self.entrance_dir == EAST and self.exit_dir == EAST:
            self.navigate_entry = self.handle_east_to_east_entry
        elif self.entrance_dir == EAST and self.exit_dir == SOUTH:
            self.navigate_entry = self.handle_east_to_south_entry
        elif self.entrance_dir == SOUTH and self.exit_dir == EAST:
            self.navigate_entry = self.handle_south_to_east_entry
        elif self.entrance_dir == SOUTH and self.exit_dir == SOUTH:
            self.navigate_entry = self.handle_south_to_south_entry

    def display_lot(self):
        """Display the current state of the parking lot"""
        for row in self.grid:
            print(' '.join(row))
        print()

    def can_fit(self, vehicle):
        """Check if a vehicle can fit in the parking lot at the given (x, y) location"""
        # Determine required area based on vehicle's orientation (direction)

        logger.info(f"Original: [{vehicle.y}, {vehicle.x}]")
        
        if vehicle.direction in [EAST, WEST]:
            required_length = vehicle.length
            required_width = vehicle.width
        else:  # NORTH, SOUTH direction
            required_length = vehicle.width
            required_width = vehicle.length

        # Check if the vehicle's position fits within the grid and doesn't hit walls/other vehicles
        for i in range(required_length):
            for j in range(required_width):
                new_x, new_y = vehicle.x + i, vehicle.y + j

                logger.info(f"[{new_y}, {new_x}]")

                if new_x < 0 or new_y < 0:
                    continue
                if self.grid[new_y][new_x] not in [" ", "I"]:  # Allow only empty spaces and entrances
                    logger.error(f"Symbol found: {self.grid[new_y][new_x]}")
                    return False
        return True

    def is_within_bounds(self, x, y):
        """Check if a position is within the bounds of the parking lot"""
        within_bounds = 1 <= x < len(self.grid) - 1 and 1 <= y < len(self.grid[0]) - 1
        logger.info(f'within bounds: {within_bounds}')
        return within_bounds

    def park_vehicle(self, vehicle):
        """Attempt to park a vehicle at the given (x, y) position"""
        if self.can_fit(vehicle):
            # If the vehicle fits, mark its position on the parking lot grid
            self.mark_occupied(vehicle)
            print(f"Vehicle {vehicle.plateNumber} parked at ({vehicle.x}, {vehicle.y}) facing {vehicle.direction}")
            self.display_lot()

    def mark_occupied(self, vehicle):
        """Mark the grid as occupied by the vehicle"""
        # Determine the space occupied by the vehicle based on its direction
        x, y = vehicle.x, vehicle.y

        if vehicle.direction in [EAST, WEST]:
            required_length = vehicle.length
            required_width = vehicle.width
        else:
            required_length = vehicle.width
            required_width = vehicle.length

        for i in range(required_length):
            for j in range(required_width):
                self.grid[x + i][y + j] = "V"  # Marking the space as occupied by the vehicle
                self.occupied.add((x + i, y + j))

    def exit_vehicle(self, vehicle):
        """Remove a vehicle from the parking lot, freeing its space"""
        print(f"Vehicle {vehicle.plateNumber} exiting from ({vehicle.x}, {vehicle.y})")
        self.clear_occupied(vehicle)
        self.display_lot()

    def clear_occupied(self, vehicle):
        """Clear the space occupied by the vehicle"""
        # Determine the space occupied by the vehicle based on its direction
        if vehicle.direction in [EAST, WEST]:
            required_length = vehicle.length
            required_width = vehicle.width
        else:
            required_length = vehicle.width
            required_width = vehicle.length

        for i in range(required_length):
            for j in range(required_width):
                self.grid[vehicle.x + i][vehicle.y + j] = " "  # Clear the space
                self.occupied.remove((vehicle.x + i, vehicle.y + j))

    def turn_right_asap(self, vehicle, max_attempts=10):
        logger.info(f"Before turning right: [{vehicle.y}, {vehicle.x}]")
        attempts = 0
        while attempts < max_attempts:
            vehicle.forward_right()
            attempts += 1
            if self.can_fit(vehicle):
                return 0  # Success, vehicle moved and fits
            else:
                vehicle.reverse_right()  # Undo the turn
                vehicle.forward()  # Try moving forward instead
                if not self.can_fit(vehicle):
                    vehicle.reverse()  # Reverse last move
                    return 1  # Failure, can't fit in any position

        return 1  # Failure, max attempts reached

    def turn_left_asap(self, vehicle, max_attempts=10):
        attempts = 0
        while attempts < max_attempts:
            vehicle.forward_left()  # Try turning left
            attempts += 1
            if self.can_fit(vehicle):
                return 0  # Success, vehicle moved and fits
            else:
                vehicle.reverse_left()  # Undo the left turn
                vehicle.forward()  # Try moving forward instead
                if not self.can_fit(vehicle):
                    vehicle.reverse()  # Reverse last forward move
                    return 1  # Failure, can't fit in any position

        return 1  # Failure, max attempts reached

    def turn_right_late(self, vehicle, max_attempts=10):
        attempts = 0
        while self.can_fit(vehicle) and attempts < max_attempts:
            vehicle.forward()
            attempts += 1

        vehicle.reverse()  # Reverse last move after reaching max forward

        attempts = 0
        while attempts < max_attempts:
            vehicle.forward_right()  # Try turning right
            if self.can_fit(vehicle):
                return 0  # Success, turned and fits
            else:
                vehicle.reverse_right()  # Undo right turn
                vehicle.reverse()  # Try reversing and retrying
                attempts += 1

            if not self.can_fit(vehicle):
                return 1  # Failure, max attempts reached

        return 1  # Failure, max attempts reached

    def turn_left_late(self, vehicle, max_attempts=10):
        attempts = 0
        while self.can_fit(vehicle) and attempts < max_attempts:
            vehicle.forward()
            attempts += 1

        vehicle.reverse()  # Reverse last move after reaching max forward

        attempts = 0
        while attempts < max_attempts:
            vehicle.forward_left()  # Try turning left
            if self.can_fit(vehicle):
                return 0  # Success, turned and fits
            else:
                vehicle.reverse_left()  # Undo left turn
                vehicle.reverse()  # Try reversing and retrying
                attempts += 1

            if not self.can_fit(vehicle):
                return 1  # Failure, max attempts reached

        return 1  # Failure, max attempts reached

    def handle_east_to_east_entry(self, vehicle):
        """Handle parking logic for East-to-East orientation."""
        current_x, current_y = vehicle.x, vehicle.y

        # Try to turn right as soon as possible
        err = self.turn_right_asap(vehicle)
        if err:
            raise VehicleCannotFitException(vehicle, f"Collision or boundary issue at position {(current_x, current_y)}")
        
        # If turning right fails, try turning left after moving forward
        err = self.turn_left_late(vehicle)
        if err:
            raise VehicleCannotFitException(vehicle, f"Collision or boundary issue at position {(current_x, current_y)}")
        
        while self.can_fit(vehicle):
            vehicle.forward()
        vehicle.reverse()
        self.park_vehicle(vehicle)

    def handle_east_to_south_entry(self, vehicle):
        """Handle parking logic for East-to-South orientation."""
        current_x, current_y = vehicle.x, vehicle.y

        # Try turning right after moving forward
        err = self.turn_right_late(vehicle)
        if err:
            raise VehicleCannotFitException(vehicle, f"Collision or boundary issue at position {(current_x, current_y)}")
        
        while self.can_fit(vehicle):
            vehicle.forward()
        vehicle.reverse()
        self.park_vehicle(vehicle)

    def handle_south_to_east_entry(self, vehicle):
        """Handle parking logic for South-to-East orientation."""
        current_x, current_y = vehicle.x, vehicle.y

        # Try turning left after moving forward
        err = self.turn_left_late(vehicle)
        if err:
            raise VehicleCannotFitException(vehicle, f"Collision or boundary issue at position {(current_x, current_y)}")
        
        while self.can_fit(vehicle):
            vehicle.forward()
        vehicle.reverse()
        self.park_vehicle(vehicle)

    def handle_south_to_south_entry(self, vehicle):
        """Handle parking logic for South-to-South orientation."""
        current_x, current_y = vehicle.x, vehicle.y

        # Try turning left as soon as possible
        err = self.turn_left_asap(vehicle)
        if err:
            # If turning left fails, try turning right late
            err = self.turn_right_late(vehicle)
            if err:
                raise VehicleCannotFitException(vehicle, f"Collision or boundary issue at position {(current_x, current_y)}")

        while self.can_fit(vehicle):
            vehicle.forward()
        vehicle.reverse()
        self.park_vehicle(vehicle)
    
    def get_exit(self, vehicle):
        if self.exit_dir == EAST:
            return self.grid_len_x - vehicle.length, self.grid_len_y - 1 - vehicle.width
        elif self.exit_dir == SOUTH:
            return self.grid_len_x - 1 - vehicle.width, self.grid_len_y - vehicle.length

# Base Vehicle class
class Vehicle:
    def __init__(self, plateNumber, direction, length, width, parking_fare):
        self.plateNumber = plateNumber
        self.direction = direction

        self.length = length
        self.width = width

        self.x = 0 - self.length + 1 if direction == EAST else 1
        self.y = 1 if direction == EAST else 0 - self.length + 1

        logger.info(f"Vehicle x: {self.x}, Vehicle y: {self.y}")
        
        self.parking_fare = parking_fare

    def __repr__(self):
        return f"{self.__class__.__name__}({self.plateNumber}, x={self.x}, y={self.y}, direction={self.direction})"
    
    def forward_left(self):
        if self.direction == NORTH:
            self.x = self.x - self.length + self.width
            self.direction = WEST
        elif self.direction == WEST:
            self.direction = SOUTH
        elif self.direction == SOUTH:
            self.y = self.y + self.length - self.width
            self.direction = EAST
        elif self.direction == EAST:
            self.x = self.x + self.length - self.width
            self.y = self.y - self.length + self.width
            self.direction = NORTH
        logger.info(f'turning left to [{self.y}, {self.x}]')

    def forward_right(self):
        if self.direction == NORTH:
            self.direction = EAST
        elif self.direction == EAST:
            self.x = self.x + self.length - self.width
            self.direction = SOUTH
        elif self.direction == SOUTH:
            self.x = self.x - self.length + self.width
            self.y = self.y + self.length - self.width
            self.direction = WEST
        elif self.direction == WEST:
            self.y = self.y - self.length + self.width
            self.direction = NORTH
        logger.info(f'turning right to [{self.y}, {self.x}]')
        
    def reverse_left(self):
        if self.direction == NORTH:
            self.x = self.x - self.length + self.width
            self.y = self.y + self.length - self.width
            self.direction = EAST
        elif self.direction == WEST:
            self.x = self.x + self.length - self.width
            self.direction = NORTH
        elif self.direction == SOUTH:
            self.direction = WEST
        elif self.direction == EAST:
            self.y = self.y - self.length + self.width
            self.direction = SOUTH
        logger.info(f'reversing left to [{self.y}, {self.x}]')

    def reverse_right(self):
        if self.direction == NORTH:
            self.y = self.y + self.length - self.width
            self.direction = WEST
        elif self.direction == EAST:
            self.direction = NORTH
        elif self.direction == SOUTH:
            self.x = self.x - self.length + self.width
            self.direction = EAST
        elif self.direction == WEST:
            self.x = self.x + self.length - self.width
            self.y = self.y - self.length + self.width
            self.direction = SOUTH
        logger.info(f'reversing right to [{self.y}, {self.x}]')
        
    def reverse(self):
        if self.direction == NORTH:
            self.y += 1
        elif self.direction == SOUTH:
            self.y -= 1
        elif self.direction == EAST:
            self.x -= 1
        elif self.direction == WEST:
            self.x += 1
        logger.info(f'reversing to [{self.y}, {self.x}]')
        
    def forward(self):
        if self.direction == NORTH:
            self.y -= 1
        elif self.direction == SOUTH:
            self.y += 1
        elif self.direction == EAST:
            self.x += 1
        elif self.direction == WEST:
            self.x -= 1
        logger.info(f'forward to [{self.y}, {self.x}]')

# Subclass for Motorcycle
class Motorcycle(Vehicle):
    def __init__(self, plateNumber, direction, length=2, width=1, parking_fare=1):
        super().__init__(plateNumber, direction=direction, length=length, width=width, parking_fare=parking_fare)

# Subclass for Car
class Car(Vehicle):
    def __init__(self, plateNumber, direction, length=3, width=2, parking_fare=5):
        super().__init__(plateNumber, direction=direction, length=length, width=width, parking_fare=parking_fare)

# Subclass for Truck
class Truck(Vehicle):
    def __init__(self, plateNumber, direction, length=5, width=2, parking_fare=10):
        super().__init__(plateNumber, direction=direction, length=length, width=width, parking_fare=parking_fare)

def process_test_case(test_case):
    minimum_fare = test_case["minimumTotalFare"]
    parking_lot_layout = test_case["parkingLot"]
    actions = test_case["actions"]
    
    parking_lot = ParkingLot(parking_lot_layout)

    vehicle_dict = {}
    
    for vehicle_data in test_case["vehicles"]:
        plate = vehicle_data["plateNumber"]
        length = vehicle_data["length"]
        width = vehicle_data["width"]
        fare = vehicle_data["parkingFare"]
        
        if length == 2 and width == 1:
            vehicle = Motorcycle(plate, direction=parking_lot.entrance_dir, length=length, width=width, parking_fare=fare)
        elif length == 3 and width == 2:
            vehicle = Car(plate, direction=parking_lot.entrance_dir, length=length, width=width, parking_fare=fare)
        elif length == 5 and width == 2:
            vehicle = Truck(plate, direction=parking_lot.entrance_dir, length=length, width=width, parking_fare=fare)
        else:
            continue
        
        vehicle_dict[plate] = vehicle

    total_fare = 0
    result_actions = []
    parked_vehicles = []

    for action in actions:
        plate = action["plateNumber"]
        action_type = action["action"]
        vehicle = vehicle_dict.get(plate)
        
        if action_type == "park":
            parked = False
            try:
                parking_lot.navigate_entry(vehicle)
                result_actions.append({
                    "plateNumber": plate,
                    "action": "park",
                    "execute": True,
                    "position": {"x": vehicle.x, "y": vehicle.y, "direction": vehicle.direction}
                })
                parked = True
                parked_vehicles.append(plate)
            except VehicleCannotFitException as e:
                logger.warning(f"Failed to park vehicle {plate}: {str(e)}")
                logger.error(traceback.format_exc())
            if not parked:
                result_actions.append({
                    "plateNumber": plate,
                    "action": "park",
                    "execute": False,
                    "position": None
                })
        
        elif action_type == "exit":
            try:
                if plate in parked_vehicles:
                    exit_x, exit_y = parking_lot.get_exit(vehicle)
                    parking_lot.exit_vehicle(vehicle)
                    total_fare += vehicle.parking_fare
                    result_actions.append({
                        "plateNumber": plate,
                        "action": "exit",
                        "execute": True,
                        "position": {"x": exit_x, "y": exit_y, "direction": vehicle.direction}
                    })
                else:
                    result_actions.append({
                        "plateNumber": plate,
                        "action": "exit",
                        "execute": False,
                        "position": None
                    })
            except Exception as e:
                logger.error(traceback.format_exc())
                result_actions.append({
                    "plateNumber": plate,
                    "action": "exit",
                    "execute": False,
                    "position": None
                })

    if total_fare >= minimum_fare:
        logger.info(f"Minimum fare reached: {total_fare}")
    else:
        logger.warning(f"Failed to reach minimum fare: {total_fare}")
    
    return result_actions

def handle_parking_lot_tests(test_cases):
    all_results = []
    for test_case in test_cases:
        result_actions = process_test_case(test_case)
        all_results.append({
            "actions": result_actions
        })
    return all_results

@app.route('/parkinglot', methods=['POST'])
def parkinglot():
    data = request.get_json()
    logger.info(data)
    logging.info("data sent for evaluation {}".format(data))
    result = handle_parking_lot_tests(data)
    logger.info(result)
    logging.info("My result :{}".format(result))
    return json.dumps(result)