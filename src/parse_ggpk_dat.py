import struct
from typing import Dict, List, Any

def parse_ggpk_dat(file_path: str, field_definitions: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Parses a Grinding Gear Games .dat64 file into a list of dictionaries.

    Args:
        file_path: The full path to the .dat64 file.
        field_definitions: A dictionary defining the names and struct format
                           specifiers for the fields in each record.

    Returns:
        A list of dictionaries, where each dictionary represents a record.
    """
    records = []
    try:
        with open(file_path, 'rb') as f:
            # The first 8 bytes of a .dat64 file typically contain the record count.
            record_count_bytes = f.read(8)
            if not record_count_bytes:
                return []  # File is empty
            
            record_count = struct.unpack('<Q', record_count_bytes)[0]
            
            # The next 8 bytes often contain the width of a single record.
            record_width_bytes = f.read(8)
            record_width = struct.unpack('<Q', record_width_bytes)[0]
            
            # The rest of the file before the variable-length data section contains the records.
            # This section's size is record_count * record_width.
            record_data_block = f.read(record_count * record_width)
            
            # The remainder is the variable-length data section (e.g., strings).
            variable_data_block = f.read()

            # Create the format string for struct.unpack from the field definitions
            format_string = '<' + ''.join(field_definitions.values())
            
            # Verify that the provided definitions match the record width
            if struct.calcsize(format_string) != record_width:
                raise ValueError(
                    f"Field definition size ({struct.calcsize(format_string)}) "
                    f"does not match file record width ({record_width})."
                )

            field_names = list(field_definitions.keys())

            for i in range(record_count):
                offset = i * record_width
                record_bytes = record_data_block[offset : offset + record_width]
                
                unpacked_data = struct.unpack(format_string, record_bytes)
                
                record_dict = {}
                for j, name in enumerate(field_names):
                    value = unpacked_data[j]
                    # 'P' format gives an offset into the variable_data_block
                    if field_definitions[name] == 'P':
                        # Read the null-terminated string from the variable data block
                        str_offset = value
                        end_of_string = variable_data_block.find(b'\x00', str_offset)
                        value = variable_data_block[str_offset:end_of_string].decode('utf-8')

                    record_dict[name] = value
                
                records.append(record_dict)

    except FileNotFoundError:
        print(f"❌ Error: The file at {file_path} was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
        
    return records