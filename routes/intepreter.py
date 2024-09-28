from flask import Flask, request, jsonify
import logging

from routes import app
logger = logging.getLogger(__name__)

variables = {}  # Store for variables

def eval_expression(expression):
    try:
        parts = expression.strip('()').split()
        func_name = parts[0]

        if func_name == "puts":
            if len(parts) != 2 or not parts[1].startswith('"') or not parts[1].endswith('"'):
                return None, "Error: puts expects a single string argument"
            return parts[1][1:-1], None  # Strip quotes

        elif func_name == "set":
            if len(parts) != 3:
                return None, "Error: Incorrect number of arguments for set"
            var_name = parts[1]
            if var_name in variables:
                return None, f"Error: Variable '{var_name}' already defined"
            variables[var_name] = parts[2]
            return None, None

        elif func_name == "concat":
            if len(parts) != 3 or not all(p.startswith('"') and p.endswith('"') for p in parts[1:]):
                return None, "Error: concat expects two string arguments"
            return parts[1][1:-1] + parts[2][1:-1], None

        elif func_name == "lowercase":
            if len(parts) != 2 or not parts[1].startswith('"') or not parts[1].endswith('"'):
                return None, "Error: lowercase expects a single string argument"
            return parts[1][1:-1].lower(), None

        elif func_name == "uppercase":
            if len(parts) != 2 or not parts[1].startswith('"') or not parts[1].endswith('"'):
                return None, "Error: uppercase expects a single string argument"
            return parts[1][1:-1].upper(), None
        
        # replace function
        elif func_name == "replace":
            if len(parts) != 4 or not all(p.startswith('"') and p.endswith('"') for p in parts[1:]):
                return None, "Error: replace expects three string arguments"
            source, target, replacement = parts[1][1:-1], parts[2][1:-1], parts[3][1:-1]
            return source.replace(target, replacement), None

        # substring function
        elif func_name == "substring":
            if len(parts) != 4 or not parts[1].startswith('"') or not parts[1].endswith('"'):
                return None, "Error: substring expects a string and two numeric arguments"
            try:
                start, end = int(parts[2]), int(parts[3])
                source = parts[1][1:-1]
                if start < 0 or end > len(source) or start >= end:
                    return None, "Error: Index out of bounds"
                return source[start:end], None
            except ValueError:
                return None, "Error: Invalid index type"

        # add function
        elif func_name == "add":
            try:
                numbers = [float(x) for x in parts[1:]]
                return round(sum(numbers), 4), None
            except ValueError:
                return None, "Error: add expects numeric arguments"

        # subtract function
        elif func_name == "subtract":
            if len(parts) != 3:
                return None, "Error: subtract expects two numeric arguments"
            try:
                result = float(parts[1]) - float(parts[2])
                return round(result, 4), None
            except ValueError:
                return None, "Error: subtract expects numeric arguments"

        # multiply function
        elif func_name == "multiply":
            try:
                result = 1
                for num in parts[1:]:
                    result *= float(num)
                return round(result, 4), None
            except ValueError:
                return None, "Error: multiply expects numeric arguments"

        # divide function
        elif func_name == "divide":
            if len(parts) != 3:
                return None, "Error: divide expects two numeric arguments"
            try:
                dividend, divisor = float(parts[1]), float(parts[2])
                if divisor == 0:
                    return None, "Error: Division by zero"
                result = dividend / divisor
                return round(result, 4), None
            except ValueError:
                return None, "Error: divide expects numeric arguments"
        # Absolute value function
        elif func_name == "abs":
            if len(parts) != 2:
                return None, "Error: abs expects one numeric argument"
            try:
                return abs(float(parts[1])), None
            except ValueError:
                return None, "Error: abs expects a numeric argument"

        # Max function
        elif func_name == "max":
            try:
                numbers = [float(p) for p in parts[1:]]
                return max(numbers), None
            except ValueError:
                return None, "Error: max expects numeric arguments"

        # Min function
        elif func_name == "min":
            try:
                numbers = [float(p) for p in parts[1:]]
                return min(numbers), None
            except ValueError:
                return None, "Error: min expects numeric arguments"

        # Greater than (gt) function
        elif func_name == "gt":
            if len(parts) != 3:
                return None, "Error: gt expects two numeric arguments"
            try:
                return float(parts[1]) > float(parts[2]), None
            except ValueError:
                return None, "Error: gt expects numeric arguments"

        # Less than (lt) function
        elif func_name == "lt":
            if len(parts) != 3:
                return None, "Error: lt expects two numeric arguments"
            try:
                return float(parts[1]) < float(parts[2]), None
            except ValueError:
                return None, "Error: lt expects numeric arguments"

        # Equality check (equal) function
        elif func_name == "equal":
            if len(parts) != 3:
                return None, "Error: equal expects two arguments"
            return parts[1] == parts[2], None

        # Not equal (not_equal) function
        elif func_name == "not_equal":
            if len(parts) != 3:
                return None, "Error: not_equal expects two arguments"
            return parts[1] != parts[2], None

        # String conversion (str) function
        elif func_name == "str":
            if len(parts) != 2:
                return None, "Error: str expects one argument"
            return str(parts[1]), None

        # Error handling for unknown functions
        else:
            return None, f"Error: Unknown function '{func_name}'"

    except Exception as e:
        return None, str(e)


@app.route('/lisp-parser', methods=['POST'])
def interpret():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))

    expressions = data.get('expressions', [])
    output = []
    
    for expression in expressions:
        result, error = eval_expression(expression)
        if result is not None:
            output.append(result)
        if error is not None:
            output.append(error)
            break  # Stop processing after the first error

    return jsonify({"output": output})


if __name__ == '__main__':
    app.run(debug=True)
