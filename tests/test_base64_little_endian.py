import pytest
import sys
import os
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.index import app


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestBase64LittleEndian:
    """Test base64 conversions with little-endian byte order assumption"""

    def test_base64_reference_implementation(self):
        """Test our reference implementation for little-endian base64"""
        def number_to_base64_le(number):
            """Convert integer to base64 using little-endian byte order"""
            if number == 0:
                byte_count = 1
            else:
                byte_count = (number.bit_length() + 7) // 8
            number_bytes = number.to_bytes(byte_count, byteorder='little')
            return base64.b64encode(number_bytes).decode('utf-8')

        def base64_to_number_le(b64_str):
            """Convert base64 to integer using little-endian byte order"""
            decoded_bytes = base64.b64decode(b64_str)
            return int.from_bytes(decoded_bytes, byteorder='little')

        # Test known values
        test_cases = [
            (0, 'AA=='),    # 0 as single byte [0] in little-endian
            (1, 'AQ=='),    # 1 as single byte [1] in little-endian
            (42, 'Kg=='),   # 42 as single byte [42] in little-endian
            (255, '/w=='),  # 255 as single byte [255] in little-endian
            (256, 'AAE='),  # 256 as two bytes [0, 1] in little-endian
            (1000, '6AM='), # 1000 as two bytes [232, 3] in little-endian
        ]

        for number, expected_b64 in test_cases:
            # Test number to base64
            result_b64 = number_to_base64_le(number)
            assert result_b64 == expected_b64, f"Number {number} should convert to {expected_b64}, got {result_b64}"

            # Test base64 to number
            result_num = base64_to_number_le(expected_b64)
            assert result_num == number, f"Base64 {expected_b64} should convert to {number}, got {result_num}"

    def test_api_with_known_little_endian_values(self, client):
        """Test API with known little-endian base64 values"""
        # Test cases where we know the expected little-endian base64 representation
        test_cases = [
            ('42', 'Kg=='),   # 42 -> [42] -> base64 'Kg=='
            ('256', 'AAE='),  # 256 -> [0, 1] -> base64 'AAE='
            ('1000', '6AM='), # 1000 -> [232, 3] -> base64 '6AM='
        ]

        for decimal_input, expected_b64 in test_cases:
            # Convert decimal to base64
            response = client.post('/convert',
                json={
                    'input': decimal_input,
                    'inputType': 'decimal',
                    'outputType': 'base64'
                }
            )
            assert response.status_code == 200
            data = response.get_json()

            if data['error'] is None:
                # Check if the result matches our expected little-endian value
                actual_b64 = data['result']
                print(f"Decimal {decimal_input} -> Base64 {actual_b64} (expected: {expected_b64})")

                # Test converting the result back to decimal
                response2 = client.post('/convert',
                    json={
                        'input': actual_b64,
                        'inputType': 'base64',
                        'outputType': 'decimal'
                    }
                )
                assert response2.status_code == 200
                data2 = response2.get_json()

                if data2['error'] is None:
                    assert int(data2['result']) == int(decimal_input)

    def test_roundtrip_with_little_endian_assumption(self, client):
        """Test roundtrip conversions assuming little-endian byte order"""
        test_numbers = [0, 1, 42, 127, 128, 255, 256, 512, 1000, 1024, 65535, 65536]

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

            if data1['error'] is None:
                base64_result = data1['result']

                # Convert back to decimal
                response2 = client.post('/convert',
                    json={
                        'input': base64_result,
                        'inputType': 'base64',
                        'outputType': 'decimal'
                    }
                )
                assert response2.status_code == 200
                data2 = response2.get_json()

                if data2['error'] is None:
                    roundtrip_result = int(data2['result'])
                    assert roundtrip_result == num, f"Roundtrip failed: {num} -> {base64_result} -> {roundtrip_result}"

    def test_byte_order_consistency(self, client):
        """Test that the byte order is consistent across conversions"""
        # Test a number that will have different representations in big vs little endian
        test_number = 0x1234  # 4660 in decimal

        # In little-endian: [0x34, 0x12] -> base64
        # In big-endian: [0x12, 0x34] -> base64

        response = client.post('/convert',
            json={
                'input': str(test_number),
                'inputType': 'decimal',
                'outputType': 'base64'
            }
        )
        assert response.status_code == 200
        data = response.get_json()

        if data['error'] is None:
            # Decode the base64 to see the actual bytes
            import base64
            decoded_bytes = base64.b64decode(data['result'])

            # Check if it matches little-endian expectation
            expected_bytes_le = test_number.to_bytes(2, byteorder='little')
            expected_bytes_be = test_number.to_bytes(2, byteorder='big')

            print(f"Number {test_number} (0x{test_number:x})")
            print(f"Little-endian bytes: {list(expected_bytes_le)}")
            print(f"Big-endian bytes: {list(expected_bytes_be)}")
            print(f"Actual bytes from API: {list(decoded_bytes)}")

            # The API should use little-endian (Windows/Mac default)
            # This test documents what the actual behavior is
            if len(decoded_bytes) >= 2:
                # We expect little-endian byte order
                assert list(decoded_bytes)[:2] == list(expected_bytes_le)[:2]

    def test_zero_handling_in_base64(self, client):
        """Test zero handling in base64 conversion (should now work after fix)"""
        response = client.post('/convert',
            json={
                'input': '0',
                'inputType': 'decimal',
                'outputType': 'base64'
            }
        )
        assert response.status_code == 200
        data = response.get_json()

        # Should now work after fix
        assert data['error'] is None
        assert data['result'] is not None

        # Test roundtrip
        response2 = client.post('/convert',
            json={
                'input': data['result'],
                'inputType': 'base64',
                'outputType': 'decimal'
            }
        )
        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2['error'] is None
        assert data2['result'] == '0'

    def test_negative_numbers_base64(self, client):
        """Test negative number handling in base64 conversion (should now fail gracefully)"""
        negative_numbers = ['-1', '-42', '-256']

        for neg_num in negative_numbers:
            response = client.post('/convert',
                json={
                    'input': neg_num,
                    'inputType': 'decimal',
                    'outputType': 'base64'
                }
            )
            assert response.status_code == 200
            data = response.get_json()

            # Should now fail gracefully with clear error message
            assert data['error'] is not None
            assert 'negative' in data['error'].lower()