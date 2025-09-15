from flask import Flask, render_template, request, jsonify
from num2words import num2words
from text2digits import text2digits
import base64
import re

app = Flask(__name__)

def text_to_number(text):
    """Convert English text number to integer"""
    # Clean and normalize the input
    text = re.sub(r'[^a-zA-Z\s-]', '', text.lower().strip())

    # Handle empty input
    if not text:
        raise ValueError("Unable to convert text to number")

    # Special case for zero
    if text in ['zero', 'nil']:
        return 0

    # Try using text2digits for complex numbers like "twenty-one", "one hundred"
    try:
        t2d = text2digits.Text2Digits()
        converted_text = t2d.convert(text)
        # If conversion happened, extract the number
        if converted_text != text:
            # Extract digits from the converted text
            numbers = re.findall(r'\d+', converted_text)
            if numbers:
                return int(numbers[0])
    except:
        pass

    # Fallback to basic dictionary for simple numbers
    number_words = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
        'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20
    }

    if text in number_words:
        return number_words[text]

    raise ValueError("Unable to convert text to number")

def number_to_text(number):
    """Convert integer to English text"""
    try:
        return num2words(number)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Unable to convert number to text: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error converting number to text: {str(e)}")

def base64_to_number(b64_str):
    """Convert base64 to integer"""
    try:
        # Decode base64 to bytes, then convert bytes to integer using little-endian
        decoded_bytes = base64.b64decode(b64_str)
        return int.from_bytes(decoded_bytes, byteorder='little')
    except Exception:
        raise ValueError("Invalid base64 input")

def number_to_base64(number):
    """Convert integer to base64"""
    try:
        # Handle negative numbers
        if number < 0:
            raise ValueError("Cannot convert negative numbers to base64")

        # Handle zero case - bit_length() of 0 is 0, need at least 1 byte
        if number == 0:
            byte_count = 1
        else:
            byte_count = (number.bit_length() + 7) // 8

        # Convert integer to bytes using little-endian (Windows/Mac default)
        number_bytes = number.to_bytes(byte_count, byteorder='little')
        return base64.b64encode(number_bytes).decode('utf-8')
    except ValueError:
        raise
    except Exception:
        raise ValueError("Unable to convert to base64")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()

        # Validate JSON structure
        if not data:
            raise ValueError("Invalid JSON: No data provided")

        if 'input' not in data:
            raise ValueError("Missing required field: 'input'")
        if 'inputType' not in data:
            raise ValueError("Missing required field: 'inputType'")
        if 'outputType' not in data:
            raise ValueError("Missing required field: 'outputType'")

        input_value = data['input']
        input_type = data['inputType']
        output_type = data['outputType']

        # Validate input is not None or empty string for most types
        if input_value is None or (isinstance(input_value, str) and input_value.strip() == ''):
            raise ValueError("Input value cannot be empty")
        
        # Convert input to integer based on input type
        if input_type == 'text':
            number = text_to_number(input_value)
        elif input_type == 'binary':
            number = int(input_value, 2)
        elif input_type == 'octal':
            number = int(input_value, 8)
        elif input_type == 'decimal':
            number = int(input_value)
        elif input_type == 'hexadecimal':
            number = int(input_value, 16)
        elif input_type == 'base64':
            number = base64_to_number(input_value)
        else:
            raise ValueError("Invalid input type")
            
        # Convert integer to output type
        if output_type == 'text':
            result = number_to_text(number)
        elif output_type == 'binary':
            result = bin(number)[2:]  # Remove '0b' prefix
        elif output_type == 'octal':
            result = oct(number)[2:]  # Remove '0o' prefix
        elif output_type == 'decimal':
            result = str(number)
        elif output_type == 'hexadecimal':
            result = hex(number)[2:]  # Remove '0x' prefix
        elif output_type == 'base64':
            result = number_to_base64(number)
        else:
            raise ValueError("Invalid output type")
            
        return jsonify({'result': result, 'error': None})
    except Exception as e:
        return jsonify({'result': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
