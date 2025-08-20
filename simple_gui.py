#!/usr/bin/env python3
"""
Simple GUI for DNG De-squeeze Tool (电影镜头DNG文件批量拉伸)

This GUI replicates the exact functionality of desqueeze_dng.py
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from pathlib import Path
from datetime import datetime

class DesqueezeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DNG De-squeeze Tool (电影镜头DNG文件批量拉伸)")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.processing = False
        self.output_text = None
        self.input_folder = tk.StringVar(value="TEST_IMAGE")
        self.output_folder = tk.StringVar(value="Original File Location")
        self.save_to_subfolder = tk.BooleanVar(value=True)
        self.subfolder_name = tk.StringVar(value="OUTPUT")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="DNG De-squeeze Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status labels
        self.status_label = ttk.Label(status_frame, text="Ready to process DNG files")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.file_count_label = ttk.Label(status_frame, text="")
        self.file_count_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Process button
        self.process_button = ttk.Button(button_frame, text="Process DNG Files", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear output button
        clear_button = ttk.Button(button_frame, text="Clear Output", command=self.clear_output)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open output folder button
        open_folder_button = ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder)
        open_folder_button.pack(side=tk.LEFT)
        
        # Output text area
        output_frame = ttk.LabelFrame(main_frame, text="Processing Output", padding="10")
        output_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Scrolled text widget for output
        self.output_text = scrolledtext.ScrolledText(output_frame, height=20, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial status check
        self.update_status()
        
    def update_status(self):
        """Update status information."""
        test_image_dir = Path("TEST_IMAGE")
        if test_image_dir.exists():
            dng_files = list(test_image_dir.glob("*.dng"))
            count = len(dng_files)
            if count > 0:
                self.file_count_label.config(text=f"Found {count} DNG file(s) in TEST_IMAGE folder")
            else:
                self.file_count_label.config(text="No DNG files found in TEST_IMAGE folder")
        else:
            self.file_count_label.config(text="TEST_IMAGE folder not found")
    
    def log_message(self, message, color="black"):
        """Add message to output text area."""
        if self.output_text:
            self.output_text.insert(tk.END, message + "\n")
            self.output_text.see(tk.END)
            self.root.update_idletasks()
    
    def clear_output(self):
        """Clear the output text area."""
        if self.output_text:
            self.output_text.delete(1.0, tk.END)
    
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        output_dir = Path("TEST_IMAGE/OUTPUT")
        if output_dir.exists():
            if sys.platform == "win32":
                os.startfile(str(output_dir))
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(output_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(output_dir)])
        else:
            messagebox.showinfo("Info", "Output folder does not exist yet.")
    
    def get_exiftool_path(self):
        """Get the path to exiftool executable."""
        lib_path = Path("Lib/exiftool-13.34_64")
        exiftool_path = lib_path / "exiftool(-k).exe"
        
        if not exiftool_path.exists():
            self.log_message("Error: exiftool not found at " + str(exiftool_path), "red")
            return None
        
        return str(exiftool_path)
    
    def create_output_directory(self):
        """Create the OUTPUT directory if it doesn't exist."""
        base_output_dir = Path("TEST_IMAGE/OUTPUT")
        
        # Check if OUTPUT directory exists and is not empty
        if base_output_dir.exists() and any(base_output_dir.iterdir()):
            # Create a new directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"TEST_IMAGE/OUTPUT_{timestamp}")
            self.log_message(f"Output 文件夹有东西. 创建新文件夹: {output_dir.name}")
        else:
            output_dir = base_output_dir
        
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def get_lens_info(self, exiftool_path, input_file):
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
            
            # Extract lens model from output
            if "Lens Model" in output:
                lens_model = output.split(":")[-1].strip()
                return lens_model
            else:
                return None
                
        except Exception as e:
            self.log_message(f"Warning: Could not read lens info for {input_file.name}: {e}", "orange")
            return None
    
    def process_dng_file(self, exiftool_path, input_file, output_file):
        """Process a single DNG file with exiftool."""
        try:
            # Get lens information
            lens_model = self.get_lens_info(exiftool_path, input_file)
            self.log_message(f"导入: {input_file.name}")
            
            if lens_model:
                self.log_message(f"  镜头: {lens_model}")
            
            # Check if it's the SIRUI anamorphic lens
            if lens_model == "SIRUI Z 20mm f/1.8S":
                self.log_message(f"  ➲是电影镜头——>启用反压缩anamorphic desqueeze (1.33x stretch)")
                
                # Command to apply DefaultScale = 1.33 1.0 (1.33x horizontal stretch)
                cmd = [
                    exiftool_path,
                    "-F",                       # Force overwrite without confirmation
                    "-DefaultScale=1.33 1.0",  # Horizontal stretch by 1.33x
                    "-o", str(output_file),     # Output file
                    str(input_file)             # Input file
                ]
                
            else:
                self.log_message(f"  ▶▶不是电影镜头——>不启用反压缩（anamorphic desqueeze） 直接复制文件")
                
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
                    os.chmod(output_file, 0o666)  # Set read/write permissions for all users
                    self.log_message(f"✓ 保存,并设为可读写: {output_file.name}")
                except Exception as e:
                    self.log_message(f"Warning: Could not set permissions for {output_file.name}: {e}", "orange")
                    self.log_message(f"✓ 保存,但无法设为可读写: {output_file.name}")
                return True
            else:
                self.log_message(f"✗ Error processing {input_file.name}: {result.stderr}", "red")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log_message(f"✗ Error processing {input_file.name}: {e}", "red")
            self.log_message(f"Command output: {e.stdout}", "red")
            self.log_message(f"Error output: {e.stderr}", "red")
            return False
        except Exception as e:
            self.log_message(f"✗ Unexpected error processing {input_file.name}: {e}", "red")
            return False
    
    def process_files(self):
        """Process all DNG files in a separate thread."""
        try:
            self.log_message("DNG De-squeeze Tool")
            self.log_message("=" * 50)
            
            # Get exiftool path
            exiftool_path = self.get_exiftool_path()
            if not exiftool_path:
                return
            
            self.log_message(f"Using exiftool: {exiftool_path}")
            
            # Create output directory
            output_dir = self.create_output_directory()
            self.log_message(f"Output directory: {output_dir}")
            
            # Find all DNG files in TEST_IMAGE folder
            test_image_dir = Path("TEST_IMAGE")
            dng_files = list(test_image_dir.glob("*.dng"))
            
            if not dng_files:
                self.log_message("No DNG files found in TEST_IMAGE folder")
                return
            
            self.log_message(f"Found {len(dng_files)} DNG file(s) to process")
            self.log_message("")
            
            # Process each DNG file
            success_count = 0
            error_count = 0
            
            for i, dng_file in enumerate(dng_files):
                # Update progress
                progress = (i / len(dng_files)) * 100
                self.progress_var.set(progress)
                self.status_label.config(text=f"Processing: {dng_file.name}")
                self.root.update_idletasks()
                
                # Create output filename with "_stretched" suffix
                output_filename = dng_file.stem + "_stretched.dng"
                output_file = output_dir / output_filename
                
                # Process the file
                if self.process_dng_file(exiftool_path, dng_file, output_file):
                    success_count += 1
                else:
                    error_count += 1
                    self.log_message(f"Stopping due to error with file: {dng_file.name}", "red")
                    break
            
            # Final progress update
            self.progress_var.set(100)
            
            self.log_message("")
            self.log_message("=" * 50)
            self.log_message("完成!")
            self.log_message(f"导出: {success_count} 张(s)")
            
            if error_count > 0:
                self.log_message(f"Errors encountered: {error_count} file(s)", "red")
                self.status_label.config(text=f"Completed with {error_count} error(s)")
            else:
                self.log_message("All files processed successfully!")
                self.status_label.config(text="Processing completed successfully!")
                
        except Exception as e:
            self.log_message(f"Unexpected error: {e}", "red")
            self.status_label.config(text="Processing failed")
        finally:
            self.processing = False
            self.process_button.config(text="Process DNG Files")
            self.process_button.config(state="normal")
    
    def start_processing(self):
        """Start the processing in a separate thread."""
        if self.processing:
            return
        
        self.processing = True
        self.process_button.config(text="Processing...")
        self.process_button.config(state="disabled")
        self.progress_var.set(0)
        self.status_label.config(text="Starting processing...")
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

def main():
    """Main function to start the GUI."""
    root = tk.Tk()
    app = DesqueezeGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
