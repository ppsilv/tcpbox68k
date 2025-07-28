import sys

def split_file_at_16_zero_bytes(input_file, output_file):
    """
    Reads a binary file and creates a new file with content up to the first
    16 consecutive zero bytes.

    Args:
        input_file (str): Path to input binary file
        output_file (str): Path to output binary file
    """

    # Size of the zero sequence we're looking for
    ZERO_SEQUENCE_LENGTH = 16
    zero_count = 0
    found_position = -1

    try:
        with open(input_file, 'rb') as f_in:
            # Read the file byte by byte
            data = f_in.read()

            # Search for 16 consecutive zeros
            for i, byte in enumerate(data):
                if byte == 0:
                    zero_count += 1
                    if zero_count == ZERO_SEQUENCE_LENGTH:
                        found_position = i - ZERO_SEQUENCE_LENGTH + 1
                        break
                else:
                    zero_count = 0

            if found_position >= 0:
                # Write data up to the zero sequence
                with open(output_file, 'wb') as f_out:
                    f_out.write(data[:found_position])
                print(f"Success! Created {output_file} with {found_position} bytes")
            else:
                print("No 16 consecutive zero bytes found in the file.")
                return False
        return True

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_binary.py <input_file> <output_file>")
        print("Example: python split_binary.py input.bin output.bin")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    if not split_file_at_16_zero_bytes(input_filename, output_filename):
        sys.exit(1)
