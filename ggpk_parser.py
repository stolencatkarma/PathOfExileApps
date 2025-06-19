import os
import struct
import io
import warnings
from typing import Dict, Union, List, Optional

class GGPKException(Exception):
    pass

class InvalidTagException(GGPKException):
    pass

class BaseRecord:
    """
    Base class for GGPK records
    """
    tag = None

    def __init__(self, container, length: int, offset: int):
        self.container = container
        self.length = length
        self.offset = offset

    def read(self, ggpkfile: io.BufferedReader):
        """
        Read record data from GGPK file
        """
        pass

class GGPKRecord(BaseRecord):
    """
    Master record of the GGPK file
    """
    tag = b'GGPK'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.version = 0
        self.offsets = []

    def read(self, ggpkfile: io.BufferedReader):
        self.version = struct.unpack('<i', ggpkfile.read(4))[0]
        self.offsets = [
            struct.unpack('<q', ggpkfile.read(8))[0],
            struct.unpack('<q', ggpkfile.read(8))[0]
        ]

class DirectoryRecordEntry:
    """
    Entry in a directory record
    """
    def __init__(self, hash: int, offset: int):
        self.hash = hash
        self.offset = offset

class DirectoryRecord(BaseRecord):
    """
    Represents a directory in the GGPK file
    """
    tag = b'PDIR'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ""
        self.name_length = 0
        self.entries_length = 0
        self.hash = b''
        self.entries = []

    def read(self, ggpkfile: io.BufferedReader):
        self.name_length = struct.unpack('<i', ggpkfile.read(4))[0]
        self.entries_length = struct.unpack('<i', ggpkfile.read(4))[0]
        self.hash = ggpkfile.read(32)
        
        # Determine character width based on GGPK version
        wchar_width = 4 if self.container.version == 4 else 2
        encoding = 'utf-32-le' if self.container.version == 4 else 'utf-16-le'
        
        # Read and decode name
        name_bytes = ggpkfile.read(wchar_width * (self.name_length - 1))
        self.name = name_bytes.decode(encoding)
        ggpkfile.seek(wchar_width, os.SEEK_CUR)  # Skip null terminator
        
        # Read directory entries
        self.entries = []
        for _ in range(self.entries_length):
            entry_hash = struct.unpack('<I', ggpkfile.read(4))[0]
            entry_offset = struct.unpack('<q', ggpkfile.read(8))[0]
            self.entries.append(DirectoryRecordEntry(entry_hash, entry_offset))

class FileRecord(BaseRecord):
    """
    Represents a file in the GGPK file
    """
    tag = b'FILE'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = ""
        self.name_length = 0
        self.hash = b''
        self.data_start = 0
        self.data_length = 0

    def read(self, ggpkfile: io.BufferedReader):
        self.name_length = struct.unpack('<i', ggpkfile.read(4))[0]
        self.hash = ggpkfile.read(32)
        
        # Determine character width based on GGPK version
        wchar_width = 4 if self.container.version == 4 else 2
        encoding = 'utf-32-le' if self.container.version == 4 else 'utf-16-le'
        
        # Read and decode name
        name_bytes = ggpkfile.read(wchar_width * (self.name_length - 1))
        self.name = name_bytes.decode(encoding)
        ggpkfile.seek(wchar_width, os.SEEK_CUR)  # Skip null terminator
        
        # Calculate data position and length
        self.data_start = ggpkfile.tell()
        self.data_length = self.length - 44 - self.name_length * wchar_width
        ggpkfile.seek(self.data_length, os.SEEK_CUR)

    def extract(self, ggpkfile: io.BufferedReader) -> bytes:
        """
        Extract file content from GGPK
        """
        current_pos = ggpkfile.tell()
        ggpkfile.seek(self.data_start)
        data = ggpkfile.read(self.data_length)
        ggpkfile.seek(current_pos)
        return data

class FreeRecord(BaseRecord):
    """
    Represents free space in the GGPK file
    """
    tag = b'FREE'

    def read(self, ggpkfile: io.BufferedReader):
        self.next_free = struct.unpack('<q', ggpkfile.read(8))[0]
        ggpkfile.seek(self.length - 16, os.SEEK_CUR)

class DirectoryNode:
    """
    Node in the GGPK directory tree
    """
    def __init__(self, name: str, is_directory: bool, record: BaseRecord, parent: Optional['DirectoryNode'] = None):
        self.name = name
        self.is_directory = is_directory
        self.record = record
        self.parent = parent
        self.children = {}
        self.hash = None

    def add_child(self, node: 'DirectoryNode'):
        self.children[node.name] = node

    def get_path(self) -> str:
        """
        Get full path of the node
        """
        if self.parent:
            return os.path.join(self.parent.get_path(), self.name)
        return self.name

class GGPKParser:
    """
    Main GGPK parser class
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.records = {}
        self.root = None
        self.version = 0

    def parse(self):
        """
        Parse the GGPK file and build directory tree
        """
        with open(self.file_path, 'rb') as f:
            # Read all records - the first record should be a GGPKRecord
            self._read_records(f)
            
            # Get the first record (should be at offset 0)
            ggpk_record = self.records.get(0)
            if not isinstance(ggpk_record, GGPKRecord):
                raise GGPKException("First record is not a GGPKRecord")
                
            self.version = ggpk_record.version
            if not ggpk_record.offsets:
                raise GGPKException("GGPKRecord has no directory pointers")
                
            # Use the first offset as the directory pointer
            dir_pointer = ggpk_record.offsets[0]
            
            # Build directory tree starting from root
            self.root = self._build_directory_tree(dir_pointer, None)

    def _read_records(self, f: io.BufferedReader):
        """
        Read all records in the GGPK file with improved error handling
        """
        f.seek(0)
        size = os.fstat(f.fileno()).st_size
        offset = 0
        chunk_size = 1048576  # 1MB chunks for error recovery
        
        # Progress reporting for large files
        print(f"Reading {size:,} bytes...")
        last_report = 0
        
        while offset < size:
            # Report progress every 10%
            if offset - last_report > size // 10:
                print(f"  Progress: {offset/size:.0%}")
                last_report = offset
                
            try:
                # Read record length and tag
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    break
                    
                length = struct.unpack('<I', length_bytes)[0]
                tag = f.read(4)
                
                # Validate length
                if length < 8 or offset + length > size:
                    warnings.warn(f"Invalid record length {length} at offset {offset}")
                    offset += 4  # Skip this length field and try next
                    f.seek(offset)
                    continue
                
                # Create appropriate record type
                if tag == b'GGPK':
                    record = GGPKRecord(self, length, offset)
                elif tag == b'PDIR':
                    record = DirectoryRecord(self, length, offset)
                elif tag == b'FILE':
                    record = FileRecord(self, length, offset)
                elif tag == b'FREE':
                    record = FreeRecord(self, length, offset)
                else:
                    raise InvalidTagException(f"Invalid tag: {tag} at offset {offset}")
                
                # Read record content and store
                record.read(f)
                self.records[offset] = record
                offset = f.tell()
                
            except Exception as e:
                warnings.warn(f"Error reading record at offset {offset}: {str(e)}")
                # Attempt to find next valid record in larger chunks
                f.seek(offset)
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                    
                # Look for next valid tag in larger chunk
                found = False
                for tag in (b'GGPK', b'PDIR', b'FILE', b'FREE'):
                    pos = chunk.find(tag)
                    if pos != -1:
                        new_offset = offset + pos - 4  # Position before tag
                        # Validate potential length field
                        f.seek(new_offset)
                        len_bytes = f.read(4)
                        if len(len_bytes) == 4:
                            try:
                                potential_len = struct.unpack('<I', len_bytes)[0]
                                if 8 <= potential_len <= size - new_offset:
                                    offset = new_offset
                                    f.seek(offset)
                                    found = True
                                    break
                            except:
                                pass
                
                if not found:
                    # Skip ahead by chunk size if nothing found
                    offset += chunk_size - 4
                    f.seek(offset)

    def _build_directory_tree(self, offset: int, parent: Optional[DirectoryNode]) -> DirectoryNode:
        """
        Recursively build directory tree from records
        """
        record = self.records.get(offset)
        if not record:
            raise GGPKException(f"Missing record at offset {offset}")
            
        if isinstance(record, DirectoryRecord):
            node = DirectoryNode(record.name, True, record, parent)
            for entry in record.entries:
                child_node = self._build_directory_tree(entry.offset, node)
                node.add_child(child_node)
            return node
            
        elif isinstance(record, FileRecord):
            return DirectoryNode(record.name, False, record, parent)
            
        else:
            raise GGPKException(f"Unexpected record type at offset {offset}: {type(record).__name__}")

    def extract_file(self, node: DirectoryNode) -> bytes:
        """
        Extract file content from a file node
        """
        if not isinstance(node.record, FileRecord):
            raise ValueError("Node is not a file")
            
        with open(self.file_path, 'rb') as f:
            return node.record.extract(f)
    
    def get_node_by_path(self, path: str) -> Optional[DirectoryNode]:
        """
        Get a node in the directory tree by its path.
        
        :param path: Path relative to GGPK root (use '/' as separator)
        :return: DirectoryNode or None if not found
        """
        if not path or path == '/':
            return self.root
            
        parts = [p for p in path.split('/') if p]
        current = self.root
        
        for part in parts:
            if not current or not current.is_directory:
                return None
            if part not in current.children:
                return None
            current = current.children[part]
        return current

    def list_directory(self, path: str) -> list:
        """
        List contents of a directory in the GGPK file system.
        
        :param path: Path relative to GGPK root
        :return: List of (name, type) tuples where type is 'dir' or 'file'
        """
        node = self.get_node_by_path(path)
        if not node:
            raise FileNotFoundError(f"Directory not found: {path}")
        if not node.is_directory:
            raise NotADirectoryError(f"Not a directory: {path}")
            
        return [(name, 'dir' if child.is_directory else 'file')
                for name, child in node.children.items()]

    def read_file(self, path: str) -> bytes:
        """
        Read file contents from the GGPK.
        
        :param path: Full path to file in GGPK
        :return: File contents as bytes
        """
        node = self.get_node_by_path(path)
        if not node:
            raise FileNotFoundError(f"File not found: {path}")
        if node.is_directory:
            raise IsADirectoryError(f"Path is a directory: {path}")
            
        return self.extract_file(node)

    def print_tree(self, node: Optional[DirectoryNode] = None, indent: int = 0):
        """
        Print directory tree structure
        """
        if node is None:
            node = self.root
            
        prefix = ' ' * indent
        if node.is_directory:
            print(f"{prefix}[{node.name}]")
            for child in node.children.values():
                self.print_tree(child, indent + 2)
        else:
            print(f"{prefix}{node.name}")

if __name__ == '__main__':
    try:
        parser = GGPKParser('Content.ggpk')
        parser.parse()
        
        print("GGPK file structure:")
        parser.print_tree()
        
        print("\nFirst 5 files:")
        count = 0
        for node in parser.root.children.values():
            if count >= 5:
                break
            if not node.is_directory:
                print(f"  - {node.name}")
                count += 1
                
    except Exception as e:
        print(f"Error parsing GGPK file: {e}")
        raise