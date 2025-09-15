# Test Suite for Numeric Converter

This test suite provides comprehensive coverage of the numeric converter application, testing all conversion flows and error scenarios.

## Test Files

### `test_conversions.py` - Unit Tests
Tests the core conversion functions in isolation:
- `text_to_number()` - Text to number conversion
- `number_to_text()` - Number to text conversion
- `base64_to_number()` - Base64 to number conversion
- `number_to_base64()` - Number to base64 conversion
- Binary, octal, and hexadecimal conversions using built-in Python functions

**Key Test Areas:**
- Basic number conversions (0-10, common values)
- Edge cases (zero, large numbers, boundary values)
- Error handling (invalid inputs, malformed data)
- Roundtrip conversions (number -> format -> number)

### `test_api.py` - Integration Tests
Tests the Flask API endpoints and HTTP interface:
- `/` route (index page)
- `/convert` POST endpoint with all input/output type combinations
- JSON request/response handling
- HTTP method validation
- Content-Type verification

**Key Test Areas:**
- All conversion type combinations (6 input types × 6 output types = 36 combinations)
- Error responses for invalid data
- HTTP status codes and headers
- Request validation and sanitization

### `test_edge_cases.py` - Edge Case Tests
Tests boundary conditions and edge cases:
- Very large numbers and performance limits
- Malformed inputs and special characters
- Whitespace handling and input sanitization
- Concurrent request handling
- Case sensitivity testing

**Key Test Areas:**
- Boundary values (0, 1, 255, 256, 2^n-1, etc.)
- Input sanitization (leading zeros, whitespace, special chars)
- Performance testing with large inputs
- Concurrency and thread safety

### `test_base64_little_endian.py` - Base64 Specific Tests
Tests base64 conversions with little-endian byte order assumption:
- Known little-endian base64 values
- Byte order consistency verification
- Reference implementation comparison
- Platform-specific behavior documentation

**Key Test Areas:**
- Little-endian byte order verification (Windows/Mac default)
- Known value testing with expected base64 strings
- Roundtrip conversion verification
- Zero and negative number edge cases

### `test_readme_examples.py` - README Example Tests
Tests the specific examples mentioned in the README.md and comprehensive well-formed inputs:
- All README.md examples tested explicitly
- Comprehensive well-formed input combinations
- Known failing examples documented
- Cross-format conversion testing

**Key Test Areas:**
- README examples: "42" decimal to binary, "forty two" text to decimal, "2a" hex to text
- All basic number format conversions that should work
- Text conversion testing with improved text2digits support
- Base64 roundtrip testing for common values
- Known failing cases documented with expected failures

## Running Tests

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
python -m pytest tests/
# or
python run_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
python run_tests.py --type unit

# Integration tests only
python run_tests.py --type integration

# Edge case tests only
python run_tests.py --type edge

# API-specific tests
python run_tests.py --type api
```

### Run with Options
```bash
# Verbose output
python run_tests.py --verbose

# Stop on first failure
python run_tests.py --failfast

# Coverage reporting (requires pytest-cov)
python run_tests.py --coverage
```

### Run Individual Test Files
```bash
python -m pytest tests/test_conversions.py -v
python -m pytest tests/test_api.py -v
python -m pytest tests/test_edge_cases.py -v
python -m pytest tests/test_base64_little_endian.py -v
```

## Expected Test Results

Due to the bugs identified in the application, some tests are **expected to fail**:

### Expected Failures
1. **Zero to Base64 conversion** - Fails due to `bit_length()` bug
2. **Negative number to Base64** - Fails due to `to_bytes()` limitation
3. **Template rendering** - Index route fails due to missing template handling in Vercel
4. **Complex text numbers** - "twenty-one", "one hundred" etc. fail due to limited text parsing
5. **Base64 malformed input** - Some edge cases may not be handled gracefully

### Tests That Should Pass
1. **Basic conversions** - decimal, binary, octal, hex for positive integers
2. **Simple text numbers** - "one" through "ten", "zero"
3. **Roundtrip conversions** - For supported number ranges
4. **Error handling** - Invalid inputs should return proper error messages
5. **HTTP interface** - API should respond with correct status codes

## Test Configuration

- **pytest.ini**: Configures test discovery, output format, and markers
- **conftest.py**: Provides shared fixtures for Flask app testing
- **requirements.txt**: Updated with pytest dependencies

## Coverage Areas

The test suite covers:
- ✅ All 6 input types (text, binary, octal, decimal, hexadecimal, base64)
- ✅ All 6 output types (text, binary, octal, decimal, hexadecimal, base64)
- ✅ All 36 input/output type combinations
- ✅ Error handling and edge cases
- ✅ HTTP interface and API validation
- ✅ Platform-specific behavior (little-endian base64)
- ✅ Performance and concurrency considerations

## Notes

This test suite serves multiple purposes:
1. **Validation** - Verify working functionality
2. **Documentation** - Tests act as executable specifications
3. **Bug Detection** - Identify and document current issues
4. **Regression Prevention** - Ensure fixes don't break existing functionality
5. **Platform Verification** - Confirm little-endian base64 assumption

The tests are designed to be informative about both working features and known bugs, making them valuable for debugging and future development.