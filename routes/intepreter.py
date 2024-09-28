from flask import Flask, request, jsonify
import logging
import re

from routes import app
logger = logging.getLogger(__name__)

variables = {}  # Store for variables

def eval_expression(expression, line_number):
    expression = expression.strip()
    
    # Check for simple values like numbers, variables, or strings
    if expression.isdigit() or re.match(r'^-?\d+(\.\d+)?$', expression):
        return float(expression), None
    elif expression.startswith('"') and expression.endswith('"'):
        return expression[1:-1], None
    elif expression in variables:
        return float(variables[expression]), None
    elif expression.startswith('(') and expression.endswith(')'):
        # It's a sub-expression; we need to evaluate it
        return eval_function(expression, line_number)
    else:
        return None, f"ERROR at line {line_number}: Invalid expression '{expression}'"

def eval_function(expression, line_number):
    parts = re.findall(r'\(.*?\)|[^\s()]+', expression.strip('()'))
    func_name = parts[0]

    try:
        if func_name == "puts":
            result, error = eval_expression(parts[1], line_number)
            if error:
                return None, error
            return str(result), None

        elif func_name == "set":
            if len(parts) != 3:
                return None, f"ERROR at line {line_number}: Incorrect number of arguments for set"
            var_name = parts[1]
            value, error = eval_expression(parts[2], line_number)
            if error:
                return None, error
            variables[var_name] = value
            return None, None

        elif func_name == "add":
            values = [eval_expression(p, line_number)[0] for p in parts[1:]]
            return round(sum(values), 4), None

        elif func_name == "subtract":
            values = [eval_expression(p, line_number)[0] for p in parts[1:]]
            return round(values[0] - sum(values[1:]), 4), None

        elif func_name == "multiply":
            values = [eval_expression(p, line_number)[0] for p in parts[1:]]
            result = 1
            for v in values:
                result *= v
            return round(result, 4), None

        elif func_name == "divide":
            values = [eval_expression(p, line_number)[0] for p in parts[1:]]
            if 0 in values[1:]:
                return None, f"ERROR at line {line_number}: Division by zero"
            result = values[0]
            for v in values[1:]:
                result /= v
            return round(result, 4), None

        elif func_name == "concat":
            results = [eval_expression(p, line_number)[0] for p in parts[1:]]
            return "".join([str(r) for r in results]), None

        elif func_name == "uppercase":
            result, error = eval_expression(parts[1], line_number)
            if error:
                return None, error
            return str(result).upper(), None

        elif func_name == "lowercase":
            result, error = eval_expression(parts[1], line_number)
            if error:
                return None, error
            return str(result).lower(), None

        elif func_name == "replace":
            original, target, replacement = [eval_expression(p, line_number)[0] for p in parts[1:4]]
            return str(original).replace(str(target), str(replacement)), None

        elif func_name == "str":
            result, error = eval_expression(parts[1], line_number)
            if error:
                return None, error
            return str(result), None

        # Max and min functions for variable arguments
        elif func_name == "max":
            values = [eval_expression(p, line_number)[0] for p in parts[1:]]
            return max(values), None

        elif func_name == "min":
            values = [eval_expression(p, line_number)[0] for p in parts[1:]]
            return min(values), None

        else:
            return None, f"ERROR at line {line_number}: Unknown function '{func_name}'"

    except Exception as e:
        return None, f"ERROR at line {line_number}: {str(e)}"


@app.route('/lisp-parser', methods=['POST'])
def interpret():
    data = request.get_json()
    expressions = data.get('expressions', [])
    output = []
    
    for i, expression in enumerate(expressions):
        result, error = eval_expression(expression, i + 1)
        if result is not None:
            output.append(str(result))
        if error is not None:
            output.append(f"{error}")
            break  # Stop processing after the first error

    return jsonify({"output": output})


if __name__ == '__main__':
    app.run(debug=True)
