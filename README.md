# Numeric Converter - cs1060-hw2-base

A web-based application that converts numbers between different formats including:
- English text (e.g., "one hundred twenty-three")
- Binary
- Octal
- Decimal
- Hexadecimal
- Base64

## Setup

1. Install the required dependencies. We recommend following the best Python practice of a virtual environment. (This assumes Python3.)
```bash
python3 -m venv "hw2-env"
. hw2-env/bin/activate
pip3 install -r requirements.txt
```

2. Run the application:
```bash
python api/index.py
```

3. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. Enter your input value in the text box
2. Select the input format from the dropdown menu
3. Select the desired output format from the second dropdown menu
4. Click "Convert" to see the result

## Examples

- Convert decimal to binary: Input "42" with input type "decimal" and output type "binary"
- Convert text to decimal: Input "forty two" with input type "text" and output type "decimal"
- Convert hexadecimal to text: Input "2a" with input type "hexadecimal" and output type "text"


## Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type edge
```

## Bug Fixes Implemented
- **Zero base64 conversion**: Fixed `bit_length()` bug that prevented converting 0 to base64
- **Negative number handling**: Added proper validation and error messages for negative base64 conversion
- **Enhanced text parsing**: Improved support for compound numbers using text2digits library
- **Better error handling**: Added JSON validation and more descriptive error messages
- **Little-endian base64**: Consistent byte order for Windows/Mac compatibility

### Test Coverage
- All README examples tested and validated
- 36 input/output type combinations covered
- Edge cases and boundary conditions tested
- Error handling and invalid input validation
- Base64 roundtrip testing with little-endian byte order

See `tests/README.md` for detailed test documentation.

# Deploying
The application should deploy to [Vercel](https://vercel.com?utm_source=github&utm_medium=readme&utm_campaign=vercel-examples) 
out of the box.

Just Add New... > Project, import the Git repository, and off you go.
Note that Vercel's Hobby plan means your private repository needs to be
in your personal GitHub account, not the organizational account.
