# Numeric Converter - cs1060-hw2-base

A web-based application that converts numbers between different formats including:
- English text (e.g., "one hundred twenty-three")
- Binary
- Octal
- Decimal
- Hexadecimal
- Base64

The application is deployed at: **https://jingyaog-hw2.vercel.app/**

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

### **Zero Base64 Conversion Bug**
Fixed a critical bug where converting the number 0 to base64 would crash with an `OverflowError`. The issue was that `number.bit_length()` returns 0 for zero, causing `to_bytes(0, ...)` to fail. The fix ensures at least 1 byte is used for zero values.

**Before:** `0 → base64` would crash
**After:** `0 → base64` works correctly (returns `'AA=='` in little-endian)

### **Negative Number Base64 Handling**
Added proper validation for negative numbers in base64 conversion. Previously, negative numbers would cause cryptic `OverflowError` messages. Now they fail gracefully with clear error messages.

**Before:** `-42 → base64` would crash with unclear error
**After:** `-42 → base64` returns clear error: "Cannot convert negative numbers to base64"

### **Enhanced Text Number Parsing**
Improved text-to-number conversion by properly utilizing the imported `text2digits` library and expanding the basic number dictionary. Now supports more number words beyond the original 1-10 range.

**Before:** Only supported "one" through "ten", "zero", "nil"
**After:** Also supports "eleven" through "twenty" and attempts compound numbers like "twenty one"

### **Better Error Handling and Validation**
Replaced bare `except:` clauses with specific exception handling and added comprehensive JSON request validation. This provides clearer error messages and prevents silent failures.

**Improvements:**
- JSON field validation with specific missing field messages
- Empty input validation
- More descriptive error messages throughout the application
- Proper exception chaining to preserve debug information

### **Little-Endian Base64 Consistency**
Changed base64 conversion from big-endian to little-endian byte order for consistency with Windows and Mac default byte ordering. This ensures predictable behavior across platforms.

**Technical change:** `byteorder='big'` → `byteorder='little'` in base64 conversion functions

### Test Coverage
- All README examples tested and validated
- 36 input/output type combinations covered
- Edge cases and boundary conditions tested
- Error handling and invalid input validation
- Base64 roundtrip testing with little-endian byte order

See `tests/README.md` for detailed test documentation.

# Deploying

## Live Demo
The application is deployed at: **https://jingyaog-hw2.vercel.app/**

## Deploy Your Own
The application should deploy to [Vercel](https://vercel.com?utm_source=github&utm_medium=readme&utm_campaign=vercel-examples)
out of the box.

Just Add New... > Project, import the Git repository, and off you go.
Note that Vercel's Hobby plan means your private repository needs to be
in your personal GitHub account, not the organizational account.
