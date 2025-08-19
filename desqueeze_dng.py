#!/usr/bin/env python3
"""
DNG De-squeeze Tool

This script processes DNG files in the TEST_IMAGE folder and applies a 1.33x horizontal stretch
(DefaultScale = 0.75 1.0) using exiftool. The processed files are saved to TEST_IMAGE/OUTPUT
with "_stretched" suffix.
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def get_exiftool_path():
    """Get the path to exiftool executable."""
    # Look for exiftool in the Lib folder
    lib_path = Path("Lib/exiftool-13.34_64")
    exiftool_path = lib_path / "exiftool(-k).exe"
    
    if not exiftool_path.exists():
        print(f"Error: exiftool not found at {exiftool_path}")
        sys.exit(1)
    
    return str(exiftool_path)

def create_output_directory():
    """Create the OUTPUT directory if it doesn't exist."""
    output_dir = Path("TEST_IMAGE/OUTPUT")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def get_lens_info(exiftool_path, input_file):
    """Get lens information from DNG file."""
    try:
        cmd = [
            exiftool_path,
            "-LensModel",
            str(input_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        
        # Extract lens model from output (format: "Lens Model                      : SIRUI Z 20mm f/1.8S")
        if "Lens Model" in output:
            lens_model = output.split(":")[-1].strip()
            return lens_model
        else:
            return None
            
    except Exception as e:
        print(f"Warning: Could not read lens info for {input_file.name}: {e}")
        return None

def process_dng_file(exiftool_path, input_file, output_file):
    """Process a single DNG file with exiftool."""
    try:
        # Get lens information
        lens_model = get_lens_info(exiftool_path, input_file)
        print(f"Processing: {input_file.name}")
        
        if lens_model:
            print(f"  Lens: {lens_model}")
        
        # Check if it's the SIRUI anamorphic lens
        if lens_model == "SIRUI Z 20mm f/1.8S":
            print(f"  Applying anamorphic desqueeze (1.33x stretch)")
            
            # Command to apply DefaultScale = 1.33 1.0 (1.33x horizontal stretch)
            cmd = [
                exiftool_path,
                "-F",                       # Force overwrite without confirmation
                "-DefaultScale=1.33 1.0",  # Horizontal stretch by 1.33x
                "-o", str(output_file),     # Output file
                str(input_file)             # Input file
            ]
            
            # Run exiftool with automatic Enter input
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input='\n')  # Send Enter automatically
            result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
            
        else:
            print(f"  Copying file without desqueeze (not anamorphic lens)")
            
            # Command to just copy the file
            cmd = [
                exiftool_path,
                "-F",                       # Force overwrite without confirmation
                "-o", str(output_file),     # Output file
                str(input_file)             # Input file
            ]
            
            # Run exiftool with automatic Enter input
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate(input='\n')  # Send Enter automatically
            result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
        
        if result.returncode == 0:
            print(f"✓ Successfully processed: {output_file.name}")
            return True
        else:
            print(f"✗ Error processing {input_file.name}: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Error processing {input_file.name}: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error processing {input_file.name}: {e}")
        return False

def main():
    """Main function to process all DNG files."""
    print("DNG De-squeeze Tool")
    print("=" * 50)
    
    # Get exiftool path
    exiftool_path = get_exiftool_path()
    print(f"Using exiftool: {exiftool_path}")
    
    # Create output directory
    output_dir = create_output_directory()
    print(f"Output directory: {output_dir}")
    
    # Find all DNG files in TEST_IMAGE folder
    test_image_dir = Path("TEST_IMAGE")
    dng_files = list(test_image_dir.glob("*.dng"))
    
    if not dng_files:
        print("No DNG files found in TEST_IMAGE folder")
        sys.exit(1)
    
    print(f"Found {len(dng_files)} DNG file(s) to process")
    print()
    
    # Process each DNG file
    success_count = 0
    error_count = 0
    
    for dng_file in dng_files:
        # Create output filename with "_stretched" suffix
        output_filename = dng_file.stem + "_stretched.dng"
        output_file = output_dir / output_filename
        
        # Process the file
        if process_dng_file(exiftool_path, dng_file, output_file):
            success_count += 1
        else:
            error_count += 1
            print(f"Stopping due to error with file: {dng_file.name}")
            break
    
    print()
    print("=" * 50)
    print(f"Processing complete!")
    print(f"Successfully processed: {success_count} file(s)")
    if error_count > 0:
        print(f"Errors encountered: {error_count} file(s)")
        sys.exit(1)
    else:
        print("All files processed successfully!")

if __name__ == "__main__":
    main() 