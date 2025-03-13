#!/bin/bash

# reCAPTCHA v3 Score Detector - Advanced Runner Script
# This script makes it easier to run the advanced score detector with common options

# Default values
PROFILE="default_profile"
RUNS=1
BUILD_HISTORY=true

# Display help message
show_help() {
    echo "reCAPTCHA v3 Score Detector - Advanced Runner"
    echo ""
    echo "Usage: ./run_advanced.sh [options]"
    echo ""
    echo "Options:"
    echo "  -p, --profile NAME    Use/create a browser profile with the specified name"
    echo "                        (default: default_profile)"
    echo "  -r, --runs N          Number of runs to perform (default: 1)"
    echo "  -n, --no-history      Skip building browsing history"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_advanced.sh"
    echo "  ./run_advanced.sh --profile my_profile --runs 3"
    echo "  ./run_advanced.sh -p test_profile -r 2 -n"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--profile)
            PROFILE="$2"
            shift 2
            ;;
        -r|--runs)
            RUNS="$2"
            shift 2
            ;;
        -n|--no-history)
            BUILD_HISTORY=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Prepare command
CMD="python advanced_score_detector.py --profile $PROFILE --runs $RUNS"

if [ "$BUILD_HISTORY" = false ]; then
    CMD="$CMD --no-history"
fi

# Display command
echo "Running: $CMD"
echo "Press Ctrl+C to cancel or Enter to continue..."
read -r

# Run the command
eval "$CMD" 