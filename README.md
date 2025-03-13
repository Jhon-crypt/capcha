# reCAPTCHA v3 Score Detector

This tool helps you achieve high reCAPTCHA v3 scores (0.8-0.9) by simulating human-like browsing behavior. It uses advanced techniques to make your browser appear more legitimate to Google's reCAPTCHA system.

## Features

- Simulates natural browsing behavior with realistic mouse movements and scrolling
- Builds browsing history by visiting common websites
- Modifies browser fingerprint to appear more human-like
- Saves and reuses successful cookie profiles
- Supports multiple runs with configurable options
- Takes screenshots for debugging and verification

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

## Notes

- The script is designed to work with reCAPTCHA v3
- Scores above 0.7 are considered good
- The script may take several minutes to complete each run
- Some websites may block automated access
- Use responsibly and in accordance with terms of service

## License

[Your chosen license]

## Contributing

[Your contribution guidelines]
