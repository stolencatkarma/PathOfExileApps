from ggpk_parser import GGPKParser
import os

class GGPKFileSystem:
    """
    File system interface for GGPK files.
    Example usage:
        parser = GGPKParser('Content.ggpk')
        parser.parse()
        fs = GGPKFileSystem(parser)
        
        # List root directory
        print(fs.listdir('/'))
        
        # Read a file
        data = fs.read_file('/Metadata/QuestAchievements.dat')
    """
    def __init__(self, parser: GGPKParser):
        self.parser = parser
        self.current_path = '/'
        
    def listdir(self, path: str = None) -> list:
        """
        List contents of a directory in the GGPK file system.
        
        :param path: Path relative to GGPK root (use '/' as separator)
        :return: List of directory entry names
        """
        path = path or self.current_path
        node = self.parser.get_node_by_path(path)
        if not node:
            raise FileNotFoundError(f"Directory not found: {path}")
        if not node.is_directory:
            raise NotADirectoryError(f"Not a directory: {path}")
            
        return list(node.children.keys())
        
    def abspath(self, path: str) -> str:
        """Convert relative path to absolute path"""
        if path.startswith('/'):
            return path
        return os.path.normpath(os.path.join(self.current_path, path)).replace('\\', '/')
        
    def join(self, base: str, *paths) -> str:
        """Join path components using '/' separator"""
        path = base
        for p in paths:
            if p.startswith('/'):
                path = p
            else:
                path = path.rstrip('/') + '/' + p
        return path
    def isdir(self, path: str) -> bool:
        """
        Check if path is a directory.
        
        :param path: Path in GGPK file system
        :return: True if path is a directory
        """
        node = self.parser.get_node_by_path(path)
        return node and node.is_directory
        
    def isfile(self, path: str) -> bool:
        """
        Check if path is a file.
        
        :param path: Path in GGPK file system
        :return: True if path is a file
        """
        node = self.parser.get_node_by_path(path)
        return node and not node.is_directory
        
    def read_file(self, path: str) -> bytes:
        """
        Read file contents from the GGPK.
        
        :param path: Full path to file in GGPK
        :return: File contents as bytes
        """
        return self.parser.read_file(self.abspath(path))
        
    def get_size(self, path: str) -> int:
        """
        Get file size in bytes.
        
        :param path: Path to file in GGPK
        :return: File size in bytes
        """
        node = self.parser.get_node_by_path(self.abspath(path))
        if not node:
            raise FileNotFoundError(f"File not found: {path}")
        if node.is_directory:
            raise IsADirectoryError(f"Path is a directory: {path}")
            
        return node.record.data_length

if __name__ == '__main__':
    # Example usage
    parser = GGPKParser('Content.ggpk')
    parser.parse()
    fs = GGPKFileSystem(parser)
    
    print("Root directory contents:")
    for item in fs.listdir('/'):
        full_path = fs.join('/', item)
        print(f" - {item} {'(dir)' if fs.isdir(full_path) else ''}")