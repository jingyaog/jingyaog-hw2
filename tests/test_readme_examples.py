import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.index import app


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestReadmeExamples:
    """Test the specific examples mentioned in README.md"""

    def test_readme_example_decimal_to_binary(self, client):
        """Test: Convert decimal to binary: Input "42" with input type "decimal" and output type "binary" """
        response = client.post('/convert',
            json={
                'input': '42',
                'inputType': 'decimal',
                'outputType': 'binary'
            }
        )
        assert response.status_code == 200
        data = response.get_json()

        # This should work - basic decimal to binary conversion
        assert data['error'] is None
        assert data['result'] == '101010'  # 42 in binary

    def test_readme_example_text_to_decimal(self, client):
        """Test: Convert text to decimal: Input "forty two" with input type "text" and output type "decimal" """
        response = client.post('/convert',
            json={
                'input': 'forty two',
                'inputType': 'text',
                'outputType': 'decimal'
            }
        )
        assert response.status_code == 200
        data = response.get_json()

        # This should now work with our text2digits fix, or fail with clear error
        if data['error'] is not None:
            # If it fails, document that this README example doesn't work
            pytest.fail(f"README example 'forty two' to decimal failed: {data['error']}")
        else:
            assert data['result'] == '42'

    def test_readme_example_hex_to_text(self, client):
        """Test: Convert hexadecimal to text: Input "2a" with input type "hexadecimal" and output type "text" """
        response = client.post('/convert',
            json={
                'input': '2a',
                'inputType': 'hexadecimal',
                'outputType': 'text'
            }
        )
        assert response.status_code == 200
        data = response.get_json()

        # This should work - hex 2a = 42 decimal = "forty-two" text
        assert data['error'] is None
        # num2words converts 42 to "forty-two"
        assert data['result'] == 'forty-two'


class TestWellFormedInputExamples:
    """Test additional well-formed input examples to ensure comprehensive coverage"""

    def test_basic_number_conversions(self, client):
        """Test basic number conversions that should always work"""
        test_cases = [
            # Basic decimal conversions
            ('decimal', 'binary', '0', '0'),
            ('decimal', 'binary', '1', '1'),
            ('decimal', 'binary', '10', '1010'),
            ('decimal', 'binary', '255', '11111111'),

            # Basic binary conversions
            ('binary', 'decimal', '0', '0'),
            ('binary', 'decimal', '1', '1'),
            ('binary', 'decimal', '1010', '10'),
            ('binary', 'decimal', '11111111', '255'),

            # Basic octal conversions
            ('octal', 'decimal', '0', '0'),
            ('octal', 'decimal', '10', '8'),
            ('octal', 'decimal', '377', '255'),

            # Basic hex conversions
            ('hexadecimal', 'decimal', '0', '0'),
            ('hexadecimal', 'decimal', 'a', '10'),
            ('hexadecimal', 'decimal', 'ff', '255'),
            ('hexadecimal', 'decimal', 'FF', '255'),  # Case insensitive

            # Decimal to other formats
            ('decimal', 'octal', '8', '10'),
            ('decimal', 'octal', '255', '377'),
            ('decimal', 'hexadecimal', '10', 'a'),
            ('decimal', 'hexadecimal', '255', 'ff'),
        ]

        for input_type, output_type, input_val, expected in test_cases:
            response = client.post('/convert',
                json={
                    'input': input_val,
                    'inputType': input_type,
                    'outputType': output_type
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['error'] is None, f"Unexpected error for {input_val} ({input_type} to {output_type}): {data['error']}"
            assert data['result'] == expected, f"Expected {expected}, got {data['result']} for {input_val} ({input_type} to {output_type})"

    def test_basic_text_conversions(self, client):
        """Test basic text conversions that should work with our fixes"""
        test_cases = [
            # Simple numbers that should work
            ('text', 'decimal', 'zero', '0'),
            ('text', 'decimal', 'one', '1'),
            ('text', 'decimal', 'two', '2'),
            ('text', 'decimal', 'five', '5'),
            ('text', 'decimal', 'ten', '10'),

            # With our expanded dictionary
            ('text', 'decimal', 'eleven', '11'),
            ('text', 'decimal', 'twelve', '12'),
            ('text', 'decimal', 'twenty', '20'),
        ]

        for input_type, output_type, input_val, expected in test_cases:
            response = client.post('/convert',
                json={
                    'input': input_val,
                    'inputType': input_type,
                    'outputType': output_type
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['error'] is None, f"Text conversion failed for '{input_val}': {data['error']}"
            assert data['result'] == expected

    def test_number_to_text_conversions(self, client):
        """Test number to text conversions"""
        test_cases = [
            ('decimal', 'text', '0', 'zero'),
            ('decimal', 'text', '1', 'one'),
            ('decimal', 'text', '5', 'five'),
            ('decimal', 'text', '10', 'ten'),
            ('decimal', 'text', '21', 'twenty-one'),
            ('decimal', 'text', '42', 'forty-two'),
            ('decimal', 'text', '100', 'one hundred'),
        ]

        for input_type, output_type, input_val, expected in test_cases:
            response = client.post('/convert',
                json={
                    'input': input_val,
                    'inputType': input_type,
                    'outputType': output_type
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['error'] is None, f"Number to text failed for {input_val}: {data['error']}"
            assert data['result'] == expected

    def test_base64_roundtrip_examples(self, client):
        """Test base64 conversions that should work after our fixes"""
        test_numbers = [0, 1, 5, 10, 42, 100, 255]

        for num in test_numbers:
            # Convert to base64
            response1 = client.post('/convert',
                json={
                    'input': str(num),
                    'inputType': 'decimal',
                    'outputType': 'base64'
                }
            )
            assert response1.status_code == 200
            data1 = response1.get_json()
            assert data1['error'] is None, f"Base64 conversion failed for {num}: {data1['error']}"

            # Convert back to decimal
            response2 = client.post('/convert',
                json={
                    'input': data1['result'],
                    'inputType': 'base64',
                    'outputType': 'decimal'
                }
            )
            assert response2.status_code == 200
            data2 = response2.get_json()
            assert data2['error'] is None, f"Base64 roundtrip failed for {num}: {data2['error']}"
            assert int(data2['result']) == num

    def test_cross_format_conversions(self, client):
        """Test conversions between different number formats"""
        # All represent the number 42
        format_values = {
            'decimal': '42',
            'binary': '101010',
            'octal': '52',
            'hexadecimal': '2a',
        }

        # Test all combinations
        for from_format, from_value in format_values.items():
            for to_format, to_value in format_values.items():
                if from_format != to_format:
                    response = client.post('/convert',
                        json={
                            'input': from_value,
                            'inputType': from_format,
                            'outputType': to_format
                        }
                    )
                    assert response.status_code == 200
                    data = response.get_json()
                    assert data['error'] is None, f"Conversion failed from {from_format} to {to_format}: {data['error']}"
                    assert data['result'] == to_value


class TestKnownFailingExamples:
    """Test examples that are expected to fail and document why"""

    def test_complex_text_that_should_fail(self, client):
        """Test complex text that may not be supported"""
        failing_cases = [
            'one hundred twenty three',
            'two thousand',
            'negative five',
            'first',  # ordinal
            'dozen',  # non-standard
        ]

        for text in failing_cases:
            response = client.post('/convert',
                json={
                    'input': text,
                    'inputType': 'text',
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()

            # Document that these fail
            if data['error'] is not None:
                # Expected to fail - document in test output
                print(f"Expected failure for '{text}': {data['error']}")
            else:
                # If it works, that's great!
                print(f"Unexpected success for '{text}': {data['result']}")

    def test_negative_base64_should_fail(self, client):
        """Test that negative numbers to base64 fail gracefully"""
        response = client.post('/convert',
            json={
                'input': '-42',
                'inputType': 'decimal',
                'outputType': 'base64'
            }
        )
        assert response.status_code == 200
        data = response.get_json()

        # Should fail with clear error message
        assert data['error'] is not None
        assert 'negative' in data['error'].lower()

    def test_invalid_format_inputs_should_fail(self, client):
        """Test invalid inputs for each format"""
        invalid_cases = [
            ('binary', '102'),  # '2' not valid in binary
            ('octal', '89'),    # '8' and '9' not valid in octal
            ('hexadecimal', 'zz'),  # 'z' not valid in hex
            ('decimal', 'abc'),     # letters not valid in decimal
            ('base64', 'invalid!'), # invalid base64 characters
        ]

        for input_type, invalid_input in invalid_cases:
            response = client.post('/convert',
                json={
                    'input': invalid_input,
                    'inputType': input_type,
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()

            # Should fail with error
            assert data['error'] is not None, f"Expected error for invalid {input_type} input '{invalid_input}'"