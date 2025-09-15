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


class TestBoundaryValues:
    """Test boundary values and edge cases"""

    def test_maximum_safe_integer(self, client):
        """Test JavaScript's maximum safe integer"""
        max_safe_int = 9007199254740991  # 2^53 - 1

        response = client.post('/convert',
            json={
                'input': str(max_safe_int),
                'inputType': 'decimal',
                'outputType': 'binary'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        if data['error'] is None:
            # Verify roundtrip
            binary_result = data['result']
            assert int(binary_result, 2) == max_safe_int

    def test_very_large_numbers(self, client):
        """Test very large numbers"""
        large_numbers = [
            '18446744073709551615',  # 2^64 - 1 (max 64-bit unsigned)
            '340282366920938463463374607431768211455',  # 2^128 - 1
        ]

        for num in large_numbers:
            response = client.post('/convert',
                json={
                    'input': num,
                    'inputType': 'decimal',
                    'outputType': 'hexadecimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            # These may or may not work depending on implementation limits

    def test_single_bit_numbers(self, client):
        """Test powers of 2 (single bit set)"""
        powers_of_2 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]

        for num in powers_of_2:
            response = client.post('/convert',
                json={
                    'input': str(num),
                    'inputType': 'decimal',
                    'outputType': 'binary'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['error'] is None
            # Verify the binary representation has exactly one '1'
            assert data['result'].count('1') == 1

    def test_all_bits_set(self, client):
        """Test numbers with all bits set (2^n - 1)"""
        all_bits_numbers = [1, 3, 7, 15, 31, 63, 127, 255, 511, 1023]

        for num in all_bits_numbers:
            response = client.post('/convert',
                json={
                    'input': str(num),
                    'inputType': 'decimal',
                    'outputType': 'binary'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['error'] is None
            # Verify the binary representation has only '1's
            assert all(bit == '1' for bit in data['result'])


class TestInputSanitization:
    """Test input sanitization and edge cases"""

    def test_leading_zeros(self, client):
        """Test inputs with leading zeros"""
        test_cases = [
            ('decimal', '042', '42'),  # Leading zero in decimal
            ('binary', '00101010', '101010'),  # Leading zeros in binary
            ('octal', '052', '52'),  # Leading zero in octal (should be same)
            ('hexadecimal', '002a', '2a'),  # Leading zeros in hex
        ]

        for input_type, input_val, expected_output in test_cases:
            response = client.post('/convert',
                json={
                    'input': input_val,
                    'inputType': input_type,
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            if data['error'] is None:
                # Convert expected to int and back to string to normalize
                expected_int = int(expected_output) if input_type != 'binary' else int(expected_output, 2)
                assert int(data['result']) == expected_int

    def test_whitespace_handling(self, client):
        """Test various whitespace scenarios"""
        whitespace_cases = [
            ' 42 ',      # Leading and trailing spaces
            '\t42\t',    # Tabs
            '\n42\n',    # Newlines
            '  42  ',    # Multiple spaces
        ]

        for input_val in whitespace_cases:
            response = client.post('/convert',
                json={
                    'input': input_val,
                    'inputType': 'decimal',
                    'outputType': 'binary'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            # May or may not handle whitespace properly

    def test_case_sensitivity(self, client):
        """Test case sensitivity in various formats"""
        # Hexadecimal case sensitivity
        hex_cases = [
            ('deadbeef', 'deadbeef'),
            ('DEADBEEF', 'deadbeef'),
            ('DeAdBeEf', 'deadbeef'),
        ]

        for input_hex, expected_lower in hex_cases:
            response = client.post('/convert',
                json={
                    'input': input_hex,
                    'inputType': 'hexadecimal',
                    'outputType': 'hexadecimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            if data['error'] is None:
                assert data['result'].lower() == expected_lower

    def test_special_characters(self, client):
        """Test inputs with special characters"""
        special_cases = [
            ('42!', 'decimal'),
            ('42.0', 'decimal'),
            ('42,000', 'decimal'),
            ('$42', 'decimal'),
            ('42%', 'decimal'),
            ('0x2a', 'hexadecimal'),  # Common hex prefix
            ('0b101010', 'binary'),   # Common binary prefix
            ('0o52', 'octal'),        # Common octal prefix
        ]

        for input_val, input_type in special_cases:
            response = client.post('/convert',
                json={
                    'input': input_val,
                    'inputType': input_type,
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            # These may fail depending on implementation


class TestBase64EdgeCases:
    """Test edge cases specific to base64 conversion"""

    def test_base64_padding(self, client):
        """Test base64 strings with different padding"""
        # Create base64 strings with different padding scenarios
        test_numbers = [0, 1, 42, 255, 256, 65535, 65536]

        for num in test_numbers:
            # Convert number to base64 using little-endian byte order
            if num == 0:
                byte_count = 1
            else:
                byte_count = (num.bit_length() + 7) // 8

            try:
                number_bytes = num.to_bytes(byte_count, byteorder='little')
                b64_str = base64.b64encode(number_bytes).decode('utf-8')

                # Test the base64 string
                response = client.post('/convert',
                    json={
                        'input': b64_str,
                        'inputType': 'base64',
                        'outputType': 'decimal'
                    }
                )
                assert response.status_code == 200
                data = response.get_json()
                if data['error'] is None:
                    assert int(data['result']) == num
            except (OverflowError, ValueError):
                # Expected for negative numbers or zero edge cases
                pass

    def test_malformed_base64(self, client):
        """Test malformed base64 inputs"""
        malformed_cases = [
            'A',          # Too short
            'AB',         # Invalid length
            'A===',       # Too much padding
            'A B',        # Space in middle
            'A\nB',       # Newline in middle
            'A!B',        # Invalid character
            '====',       # Only padding
        ]

        for case in malformed_cases:
            response = client.post('/convert',
                json={
                    'input': case,
                    'inputType': 'base64',
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['error'] is not None

    def test_empty_base64(self, client):
        """Test empty base64 input"""
        response = client.post('/convert',
            json={
                'input': '',
                'inputType': 'base64',
                'outputType': 'decimal'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['error'] is not None


class TestTextConversionEdgeCases:
    """Test edge cases for text conversion"""

    def test_compound_numbers(self, client):
        """Test compound number words that should fail with current implementation"""
        compound_numbers = [
            'twenty-one',
            'thirty-two',
            'forty-five',
            'one hundred',
            'two thousand',
            'one million',
        ]

        for text in compound_numbers:
            response = client.post('/convert',
                json={
                    'input': text,
                    'inputType': 'text',
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            # These should fail with current limited implementation
            assert data['error'] is not None

    def test_text_with_numbers(self, client):
        """Test text mixed with numbers"""
        mixed_cases = [
            'one2',
            '2one',
            'o1ne',
            'tw0',
        ]

        for text in mixed_cases:
            response = client.post('/convert',
                json={
                    'input': text,
                    'inputType': 'text',
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['error'] is not None

    def test_ordinal_numbers(self, client):
        """Test ordinal numbers"""
        ordinal_cases = [
            'first',
            'second',
            'third',
            'fourth',
            'fifth',
        ]

        for text in ordinal_cases:
            response = client.post('/convert',
                json={
                    'input': text,
                    'inputType': 'text',
                    'outputType': 'decimal'
                }
            )
            assert response.status_code == 200
            data = response.get_json()
            # Should fail with current implementation
            assert data['error'] is not None


class TestRoundTripConversions:
    """Test round-trip conversions to ensure consistency"""

    def test_all_format_roundtrips(self, client):
        """Test converting through all formats and back"""
        test_numbers = [0, 1, 2, 5, 10, 42, 255, 256, 1000]
        formats = ['decimal', 'binary', 'octal', 'hexadecimal']

        for num in test_numbers:
            for start_format in formats:
                for intermediate_format in formats:
                    if start_format == intermediate_format:
                        continue

                    # Convert number to start format string
                    if start_format == 'decimal':
                        start_value = str(num)
                    elif start_format == 'binary':
                        start_value = bin(num)[2:]
                    elif start_format == 'octal':
                        start_value = oct(num)[2:]
                    elif start_format == 'hexadecimal':
                        start_value = hex(num)[2:]

                    # Convert to intermediate format
                    response1 = client.post('/convert',
                        json={
                            'input': start_value,
                            'inputType': start_format,
                            'outputType': intermediate_format
                        }
                    )
                    assert response1.status_code == 200
                    data1 = response1.get_json()

                    if data1['error'] is None:
                        # Convert back to start format
                        response2 = client.post('/convert',
                            json={
                                'input': data1['result'],
                                'inputType': intermediate_format,
                                'outputType': start_format
                            }
                        )
                        assert response2.status_code == 200
                        data2 = response2.get_json()

                        if data2['error'] is None:
                            # Verify we got back the original value
                            assert data2['result'] == start_value

    def test_base64_roundtrip_edge_cases(self, client):
        """Test base64 round-trip with edge case numbers"""
        edge_numbers = [0, 1, 255, 256, 65535, 65536]

        for num in edge_numbers:
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

                if data2['error'] is None:
                    assert int(data2['result']) == num


class TestConcurrency:
    """Test concurrent requests to the API"""

    def test_multiple_simultaneous_requests(self, client):
        """Test that multiple requests can be handled"""
        import threading

        results = []
        errors = []

        def make_request():
            try:
                response = client.post('/convert',
                    json={
                        'input': '42',
                        'inputType': 'decimal',
                        'outputType': 'binary'
                    }
                )
                results.append(response.get_json())
            except Exception as e:
                errors.append(e)

        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all requests completed successfully
        assert len(errors) == 0
        assert len(results) == 10

        # Verify all results are correct
        for result in results:
            if result['error'] is None:
                assert result['result'] == '101010'


class TestPerformance:
    """Test performance with various input sizes"""

    def test_large_input_strings(self, client):
        """Test very long input strings"""
        # Test very long binary string
        long_binary = '1' * 1000  # 1000-bit number

        response = client.post('/convert',
            json={
                'input': long_binary,
                'inputType': 'binary',
                'outputType': 'decimal'
            }
        )
        assert response.status_code == 200
        # May timeout or fail due to size

    def test_base64_large_data(self, client):
        """Test base64 with large data"""
        # Create a large number and convert to base64
        large_num = 2 ** 1000  # Very large number

        response = client.post('/convert',
            json={
                'input': str(large_num),
                'inputType': 'decimal',
                'outputType': 'base64'
            }
        )
        assert response.status_code == 200
        # May fail due to implementation limits