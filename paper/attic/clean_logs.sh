#!/bin/bash

# Change to the directory of the script
cd "$(dirname "$0")" || exit

echo "Cleaning up LaTeX log and auxiliary files based on .gitignore..."

# We read the .gitignore file to find the patterns of files to delete
while IFS= read -r pattern || [ -n "$pattern" ]; do
    # Remove carriage returns if they exist
    pattern=$(echo "$pattern" | tr -d '\r')
    
    # Ignore empty lines and comments
    if [[ -z "$pattern" ]] || [[ "$pattern" == \#* ]]; then
        continue
    fi
    
    # Keep PDFs
    if [[ "$pattern" == "*.pdf" ]]; then
        continue
    fi
    
    # Delete files matching the pattern in the current directory and subdirectories
    find . -type f -name "$pattern" -delete 2>/dev/null
    
done < .gitignore

echo "Cleanup complete! PDFs and other untracked source files remain."
