#!/bin/bash

# Default values
PROFILE="high_score_profile"
RUNS=1
HISTORY=true
HEADLESS=false

# Parse command line options
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile=*)
            PROFILE="${1#*=}"
            shift
            ;;
        --runs=*)
            RUNS="${1#*=}"
            shift
            ;;
        --no-history)
            HISTORY=false
            shift
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --help)
            echo "reCAPTCHA Score Detector Runner"
            echo "Usage: ./run_detector.sh [options]"
            echo ""
            echo "Options:"
            echo "  --profile=NAME    Browser profile to use (default: high_score_profile)"
            echo "  --runs=N          Number of runs to perform (default: 1)"
            echo "  --no-history      Skip building browsing history"
            echo "  --headless        Run in headless mode (not recommended for high scores)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Display settings
echo "=== reCAPTCHA Score Detector ==="
echo "Running with settings:"
echo "  Profile: $PROFILE"
echo "  Runs: $RUNS"
echo "  Build History: $HISTORY"
echo "  Headless: $HEADLESS"
echo "==========================="

# Build command
CMD="python advanced_score_detector.py --profile $PROFILE --runs $RUNS"

if [ "$HISTORY" = false ]; then
    CMD="$CMD --no-history"
fi

if [ "$HEADLESS" = true ]; then
    CMD="$CMD --headless"
fi

echo "Starting run at $(date)"
echo "Command: $CMD"

# Run the command
eval $CMD

# Check result
if [ $? -eq 0 ]; then
    echo "Run completed successfully at $(date)."
else
    echo "Run failed with error code $? at $(date)."
fi 