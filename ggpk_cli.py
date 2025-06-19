import argparse
from ggpk_filesystem import GGPKFileSystem
from ggpk_parser import GGPKParser

def main():
    parser = argparse.ArgumentParser(description='GGPK File System Explorer')
    parser.add_argument('ggpk_file', help='Path to Content.ggpk file')
    args = parser.parse_args()

    try:
        # Initialize parser and file system
        print(f"Loading GGPK file: {args.ggpk_file}")
        ggpk_parser = GGPKParser(args.ggpk_file)
        ggpk_parser.parse()
        fs = GGPKFileSystem(ggpk_parser)
        print("GGPK loaded successfully!\n")

        # Interactive shell
        while True:
            command_str = input(f"GGPK:{fs.current_path}> ").strip()
            if not command_str:
                continue

            if command_str.lower() in ['exit', 'quit']:
                break

            parts = command_str.split()
            command = parts[0].lower()
            cmd_args = parts[1:]

            try:
                if command == 'ls':
                    target_path = cmd_args[0] if cmd_args else fs.current_path
                    abs_path = fs.abspath(target_path)
                    if not fs.isdir(abs_path):
                        print(f"Error: Not a directory - {abs_path}")
                        continue
                        
                    entries = fs.listdir(abs_path)
                    for entry in entries:
                        entry_path = fs.join(abs_path, entry)
                        print(f"  - {entry} {'(dir)' if fs.isdir(entry_path) else ''}")
                
                elif command == 'cd':
                    if not cmd_args:
                        fs.current_path = '/'
                    else:
                        new_path = cmd_args[0]
                        abs_path = fs.abspath(new_path)
                        if fs.isdir(abs_path):
                            fs.current_path = abs_path
                        else:
                            print(f"Directory not found: {new_path}")
                
                elif command == 'cat':
                    if not cmd_args:
                        print("Usage: cat <file_path>")
                        continue
                    
                    file_path = fs.abspath(cmd_args[0])
                    if not fs.isfile(file_path):
                        print(f"File not found: {file_path}")
                        continue
                    
                    data = fs.read_file(file_path)
                    try:
                        # Try to decode as text
                        print(data.decode('utf-8'))
                    except UnicodeDecodeError:
                        print(f"Binary file content ({len(data)} bytes)")
                
                elif command == 'pwd':
                    print(fs.current_path)
                
                elif command == 'size':
                    if not cmd_args:
                        print("Usage: size <file_path>")
                        continue
                    
                    file_path = fs.abspath(cmd_args[0])
                    if not fs.isfile(file_path):
                        print(f"File not found: {file_path}")
                        continue
                    
                    size = fs.get_size(file_path)
                    print(f"{file_path}: {size} bytes")
                
                elif command == 'help':
                    print("Available commands:")
                    print("  ls [path]       - List directory contents")
                    print("  cd [path]       - Change directory")
                    print("  cat <file>      - Show file contents")
                    print("  size <file>     - Show file size")
                    print("  pwd             - Show current path")
                    print("  exit/quit       - Exit the program")
                
                else:
                    print(f"Unknown command: {command}. Type 'help' for available commands.")
            
            except Exception as e:
                print(f"Error: {str(e)}")
    
    except Exception as e:
        print(f"Error loading GGPK: {str(e)}")

if __name__ == '__main__':
    main()