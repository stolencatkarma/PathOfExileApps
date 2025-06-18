from ggpk_parser import parse_ggpk, extract_dat_files
from dat_parser import parse_dat
import tempfile
import os

def main():
    # Parse the GGPK file to get the list of files (though now extract_dat_files handles DAT extraction)
    # This line may be redundant if extract_dat_files is handling the extraction
    # But kept for potential future use or metadata purposes
    ggpk_files = parse_ggpk('Content.ggpk')
    
    # Use a temporary directory to extract and process DAT files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract all DAT files to the temporary directory
        extract_dat_files('Content.ggpk', temp_dir)
        
        # Iterate over all files in the temporary directory and its subdirectories
        for root, dirs, files in os.walk(temp_dir):
            for filename in files:
                # Check if it's a DAT file
                if filename.endswith('.dat'):
                    dat_path = os.path.join(root, filename)
                    # Parse and print the DAT file contents
                    data = parse_dat(dat_path)
                    print(data)

if __name__ == '__main__':
    main()