# reCAPTCHA v3 Score Detector

This tool helps you achieve high reCAPTCHA v3 scores (0.8-0.9) by simulating human-like browsing behavior. It uses advanced techniques to make your browser appear more legitimate to Google's reCAPTCHA system.

## Features

- Simulates natural browsing behavior with realistic mouse movements and scrolling
- Builds browsing history by visiting common websites
- Modifies browser fingerprint to appear more human-like
- Saves and reuses successful cookie profiles
- Supports multiple runs with configurable options
- Takes screenshots for debugging and verification
- Cross-platform support for Linux, macOS, and Windows with appropriate user agents

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- Required Python packages:
  ```
  seleniumbase
  ```

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd capcha
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Create the required directories (automatically created by the script on first run):
   ```bash
   mkdir -p screenshots cookies profiles
   ```

## Usage

### Basic Usage

Run the script with default settings:
```bash
python advanced_score_detector.py
```

or 

```bash
python advanced_score_detector.py --profile high_score_profile --runs 1
```

### Advanced Options

```bash
python advanced_score_detector.py [options]

Options:
  --profile PROFILE_NAME    Use/create a persistent browser profile
  --headless              Run in headless mode (no visible browser)
  --no-history            Skip building browsing history
  --pause                 Pause before closing browser
  --runs NUMBER           Number of runs to perform (default: 1)
```

### Examples

1. Run with a persistent profile:
   ```bash
   python advanced_score_detector.py --profile high_score_profile
   ```

2. Run multiple times with the same profile:
   ```bash
   python advanced_score_detector.py --profile high_score_profile --runs 3
   ```

3. Run in headless mode:
   ```bash
   python advanced_score_detector.py --profile high_score_profile --headless
   ```

### Using Shell Scripts

For convenience, two shell scripts are provided:

1. **run_detector.sh** - Run the detector with various options:
   ```bash
   # Make executable (first time only)
   chmod +x run_detector.sh
   
   # Run with default settings
   ./run_detector.sh
   
   # Run with custom options
   ./run_detector.sh --profile=my_profile --runs=3
   
   # Show help
   ./run_detector.sh --help
   ```

2. **analyze_scores.sh** - Analyze score history from previous runs:
   ```bash
   # Make executable (first time only)
   chmod +x analyze_scores.sh
   
   # Analyze default profile
   ./analyze_scores.sh
   
   # Analyze specific profile
   ./analyze_scores.sh --profile=my_profile
   ```

## How It Works

1. **Browser Profile Management**
   - Creates persistent browser profiles to maintain consistent behavior
   - Saves and reuses successful cookie profiles

2. **Human-like Behavior Simulation**
   - Natural mouse movements with acceleration/deceleration
   - Realistic scrolling patterns
   - Variable typing speeds and patterns
   - Random delays between actions

3. **Browser Fingerprint Modification**
   - Modifies WebGL and Canvas fingerprints
   - Sets realistic timezone and geolocation
   - Adds common browser plugins
   - Maintains consistent browser properties

4. **Browsing History Building**
   - Visits common websites before the target site
   - Performs natural interactions on each site
   - Simulates reading and scrolling behavior

## Tips for High Scores

1. **Use Persistent Profiles**
   - Always use the `--profile` option to maintain consistent behavior
   - High scores (0.8-0.9) are more likely with established profiles

2. **Timing**
   - Wait at least 5 minutes between runs
   - Run at different times of day
   - Don't run too frequently

3. **IP Address**
   - Use a residential IP address with good reputation
   - Avoid VPNs or proxy servers

4. **Browser Settings**
   - Don't use headless mode for best results
   - Allow cookies and JavaScript
   - Use a modern Chrome version
   - The script automatically uses platform-appropriate user agents (Linux, macOS, or Windows)

## Directory Structure

```
capcha/
├── advanced_score_detector.py  # Main script
├── cookies/                    # Directory for saved cookies
├── profiles/                   # Directory for browser profiles
└── screenshots/                # Directory for debug screenshots
```

## Troubleshooting

1. **Score Not Improving**
   - Try using a different IP address
   - Wait longer between runs
   - Check if your browser profile is being saved correctly

2. **Script Errors**
   - Check the screenshots directory for error screenshots
   - Ensure Chrome is up to date
   - Try clearing the profiles directory and starting fresh

3. **Browser Issues**
   - Make sure Chrome is installed and accessible
   - Check if any antivirus software is blocking the script
   - Try running without headless mode

4. **Context Manager Error**
   - If you see an error like `'_GeneratorContextManager' object has no attribute 'execute_script'`
   - This is related to how SeleniumBase initializes the browser
   - Make sure you're using the latest version of the script which handles browser initialization correctly
   - You can update with `pip install -U seleniumbase` to get the latest SeleniumBase version
   - If you still encounter this error, you might need to update the `init_browser` function to use `Driver` instead of `SB` class

5. **Driver Issue with seleniumbase>=4.19.2**
   - If using the latest version of seleniumbase causes driver issues
   - Try using: `pip install seleniumbase==4.18.1` to install a more stable version
   - You may need to adjust the `init_browser` function accordingly

## Notes

- The script is designed to work with reCAPTCHA v3
- Scores above 0.7 are considered good
- The script may take several minutes to complete each run
- Some websites may block automated access
- Use responsibly and in accordance with terms of service
