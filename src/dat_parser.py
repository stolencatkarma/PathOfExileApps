import struct
import pprint
from typing import Dict, List, Any, Tuple


class DatParser:
    """
    A parser for Grinding Gear Games .dat64 files.

    This class reads a .dat64 file, interprets its binary content based on a
    provided schema, and returns the data as a list of dictionaries.
    """

    def __init__(self, file_path: str, schema: Dict[str, Tuple[int, str]]):
        """
        Initializes the parser with the file path and schema.

        Args:
            file_path: The full path to the .dat64 file.
            schema: A dictionary defining the record structure.
                    Example: {'field_name': (offset, 'struct_format_char')}
        """
        self.file_path = file_path
        self.schema = self._process_schema(schema)
        self.record_width = self._calculate_record_width()
        self.field_names = list(self.schema.keys())
        self.format_string = '<' + ''.join(s[1] for s in self.schema.values())

    def _process_schema(self, schema: Dict[str, Tuple[int, str]]) -> Dict[str, Tuple[str]]:
        """Sorts the schema by offset and extracts format characters."""
        # Sort by offset (the first element in the tuple)
        sorted_items = sorted(schema.items(), key=lambda item: item[1][0])
        # Return a dictionary with just the format characters, maintaining order
        return {k: v[1] for k, v in sorted_items}

    def _calculate_record_width(self) -> int:
        """Calculates the total width of a single record from the schema."""
        # Use struct.calcsize on the full format string to get width
        format_string = '<' + ''.join(self.schema.values())
        return struct.calcsize(format_string)

    def parse(self) -> List[Dict[str, Any]]:
        """
        Executes the parsing of the .dat64 file.

        Returns:
            A list of dictionaries, where each dictionary represents a record.
            Returns an empty list if an error occurs.
        """
        records = []
        try:
            with open(self.file_path, 'rb') as f:
                # First 8 bytes are the record count (unsigned long long)
                record_count_bytes = f.read(8)
                if not record_count_bytes:
                    print(f"Warning: File '{self.file_path}' is empty.")
                    return []
                
                record_count = struct.unpack('<Q', record_count_bytes)[0]

                # Read the fixed-width record data block
                record_data_size = record_count * self.record_width
                record_data_block = f.read(record_data_size)

                # The rest of the file is the variable-length data block (for strings)
                variable_data_block = f.read()

                # Iterate through each record in the block
                for i in range(record_count):
                    offset = i * self.record_width
                    record_bytes = record_data_block[offset : offset + self.record_width]
                    
                    unpacked_data = struct.unpack(self.format_string, record_bytes)
                    
                    record_dict = {}
                    for j, field_name in enumerate(self.field_names):
                        value = unpacked_data[j]
                        field_format = self.schema[field_name]

                        # If the field is a pointer ('P'), resolve the string
                        if 'P' in field_format:
                            str_offset = value
                            # Find the null terminator for the string
                            end_of_string = variable_data_block.find(b'\x00', str_offset)
                            if end_of_string != -1:
                                value = variable_data_block[str_offset:end_of_string].decode('utf-8', errors='ignore')
                            else:
                                value = "" # Handle cases with bad pointers or no null terminator

                        record_dict[field_name] = value
                    
                    records.append(record_dict)

        except FileNotFoundError:
            print(f"❌ Error: The file at '{self.file_path}' was not found.")
            return []
        except struct.error as e:
            print(f"❌ Struct Error: Failed to unpack data. This often means the schema's record width "
                  f"({self.record_width} bytes) doesn't match the file's actual record width. Error: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []
            
        return records


# --- HOW TO USE ---

if __name__ == '__main__':
    # Step 1: Define the schema for the file you want to parse.
    # This is the most important step. You need to find the correct structure for each file.
    # The format is: 'field_name': (offset, 'struct_format_specifier')
    #
    # COMMON SPECIFIERS:
    # B: unsigned char (1 byte)      ?: bool (1 byte)
    # I: unsigned int (4 bytes)      f: float (4 bytes)
    # Q: unsigned long long (8 bytes) P: pointer (unsigned long long, 8 bytes)
    #
    # This example is a *hypothetical* structure for 'BaseItemTypes.dat64'.
    # The real schemas are maintained by the community (see link below).
    base_item_types_schema = {
        'id_ptr':           (0, 'P'),  # Pointer to the item's ID string
        'name_ptr':         (8, 'P'),  # Pointer to the item's name string
        'inventory_width':  (16, 'I'), # Inventory width as an unsigned int
        'inventory_height': (20, 'I'), # Inventory height as an unsigned int
    }

    # Step 2: Specify the path to your .dat64 file.
    # IMPORTANT: Update this path to your actual file location.
    file_to_parse = 'C:\\PathofExileData\\BaseItemTypes.dat64'

    # Step 3: Create a parser instance and run it.
    parser = DatParser(file_to_parse, base_item_types_schema)
    parsed_data = parser.parse()

    # Step 4: Process the results.
    if parsed_data:
        print(f"✅ Successfully parsed {len(parsed_data)} records from '{file_to_parse}'.")
        # Pretty-print the first 5 records as an example
        pprint.pprint(parsed_data[:5])
    else:
        print(f" DPC: पार्सिंग के दौरान एक त्रुटि हुई '{file_to_parse}'. ऊपर दिए गए त्रुटि संदेशों की समीक्षा करें।")