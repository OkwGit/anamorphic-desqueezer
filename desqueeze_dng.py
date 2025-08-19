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
    base_output_dir = Path("TEST_IMAGE/OUTPUT")
    
    # Check if OUTPUT directory exists and is not empty
    if base_output_dir.exists() and any(base_output_dir.iterdir()):
        # Create a new directory with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"TEST_IMAGE/OUTPUT_{timestamp}")
        print(f"\033[33mOutput 文件夹有东西. 创建新文件夹: {output_dir.name}\033[0m")
    else:
        output_dir = base_output_dir
    
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
        
        # Run exiftool with automatic Enter input
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input='\n')  # Send Enter automatically
        output = stdout.strip()
        
        # Extract lens model from output (format: "Lens Model                      : SIRUI Z 20mm f/1.8S")
        if "Lens Model" in output:
            lens_model = output.split(":")[-1].strip()
            return lens_model
        else:
            return None
            
    except Exception as e:
        print(f"\033[31mWarning: Could not read lens info for {input_file.name}: {e}\033[0m")
        return None

def process_dng_file(exiftool_path, input_file, output_file):
    """Process a single DNG file with exiftool."""
    try:
        # Get lens information
        lens_model = get_lens_info(exiftool_path, input_file)
        print(f"导入: {input_file.name}")
        
        if lens_model:
            print(f"  镜头: {lens_model}")
        
        # Check if it's the SIRUI anamorphic lens
        if lens_model == "SIRUI Z 20mm f/1.8S":
            print(f"  ➲是电影镜头——>启用反压缩anamorphic desqueeze (1.33x stretch)")
            
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
            print(f"  ▶▶不是电影镜头——>不启用反压缩（anamorphic desqueeze） 直接复制文件")
            
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
            # Ensure the output file has write permissions
            try:
                import os
                os.chmod(output_file, 0o666)  # Set read/write permissions for all users
                print(f"✓ 保存,并设为可读写: {output_file.name}")
            except Exception as e:
                print(f"\033[31mWarning: Could not set permissions for {output_file.name}: {e}\033[0m")
                print(f"✓ 保存,但无法设为可读写: {output_file.name}")
            return True
        else:
            print(f"\033[31m✗ Error processing {input_file.name}: {result.stderr}\033[0m")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\033[31m✗ Error processing {input_file.name}: {e}\033[0m")
        print(f"\033[31mCommand output: {e.stdout}\033[0m")
        print(f"\033[31mError output: {e.stderr}\033[0m")
        return False
    except Exception as e:
        print(f"\033[31m✗ Unexpected error processing {input_file.name}: {e}\033[0m")
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
            print(f"\033[31mStopping due to error with file: {dng_file.name}\033[0m")
            break
    
    print()
    print("=" * 50)
    print(f"\033[32m完成!\033[0m")
    print(f"\033[32m导出: {success_count} 张(s)\033[0m")
    if error_count > 0:
        print(f"\033[31mErrors encountered: {error_count} file(s)\033[0m")
        sys.exit(1)
    else:
        print(f"\033[32mAll files processed successfully!\033[0m")

if __name__ == "__main__":
    main() 