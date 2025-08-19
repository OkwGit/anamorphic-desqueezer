# DNG De-squeeze Tool

This tool processes DNG files in the `TEST_IMAGE` folder and applies a 1.33x horizontal stretch (de-squeeze factor) using exiftool.

## What it does

- Processes all `.dng` files in the `TEST_IMAGE` folder
- Applies a horizontal stretch of 1.33x (DefaultScale = 0.75 1.0)
- Saves processed files to `TEST_IMAGE/OUTPUT` with `_stretched` suffix
- Keeps original files unchanged
- Stops processing if any errors are encountered

## Usage

### Option 1: Run Python script directly
```bash
python desqueeze_dng.py
```

### Option 2: Run batch file (Windows)
```bash
run_desqueeze.bat
```

## File Structure

```
anamorphic-desqueezer/
├── TEST_IMAGE/
│   ├── DSC_2284.dng          # Original files
│   ├── DSC_2285.dng
│   ├── ...
│   └── OUTPUT/
│       ├── DSC_2284_stretched.dng  # Processed files
│       ├── DSC_2285_stretched.dng
│       └── ...
├── Lib/
│   └── exiftool-13.34_64/    # exiftool executable
├── desqueeze_dng.py          # Main script
├── run_desqueeze.bat         # Windows batch file
└── README.md                 # This file
```

## Requirements

- Python 3.6 or higher
- exiftool (included in Lib folder)
- DNG files in TEST_IMAGE folder

## Output

- Processed files are saved as `filename_stretched.dng` in `TEST_IMAGE/OUTPUT`
- The script will skip files that have already been processed
- Original files remain unchanged

## Error Handling

- The script stops immediately if any file processing fails
- Detailed error messages are displayed for troubleshooting
- Exit code 1 is returned if any errors occur 