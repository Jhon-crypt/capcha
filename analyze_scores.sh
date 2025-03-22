#!/bin/bash

# Default profile
PROFILE="high_score_profile"

# Parse command line options
while [[ $# -gt 0 ]]; do
    case $1 in
        --profile=*)
            PROFILE="${1#*=}"
            shift
            ;;
        --help)
            echo "reCAPTCHA Score Analyzer"
            echo "Usage: ./analyze_scores.sh [options]"
            echo ""
            echo "Options:"
            echo "  --profile=NAME    Browser profile to analyze (default: high_score_profile)"
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
echo "=== reCAPTCHA Score Analyzer ==="
echo "Analyzing profile: $PROFILE"
echo "==========================="

# Check if the profile exists
PROFILE_DIR="profiles/$PROFILE"
if [ ! -d "$PROFILE_DIR" ]; then
    echo "Profile directory not found: $PROFILE_DIR"
    exit 1
fi

# Check for score history file
HISTORY_FILE="$PROFILE_DIR/score_history.txt"
if [ -f "$HISTORY_FILE" ]; then
    echo "Score history found:"
    echo "-----------------"
    cat "$HISTORY_FILE"
    echo "-----------------"
    
    # Count runs and calculate average
    TOTAL_RUNS=$(wc -l < "$HISTORY_FILE")
    echo "Total runs: $TOTAL_RUNS"
    
    # Extract scores and calculate average
    SCORES=$(grep -o "Score [0-9]\.[0-9]\+" "$HISTORY_FILE" | cut -d' ' -f2)
    
    # Calculate statistics if scores are found
    if [ -n "$SCORES" ]; then
        # Calculate average
        SUM=0
        COUNT=0
        MAX=0
        MIN=1
        
        for SCORE in $SCORES; do
            SUM=$(echo "$SUM + $SCORE" | bc)
            COUNT=$((COUNT + 1))
            
            # Update max and min
            if (( $(echo "$SCORE > $MAX" | bc -l) )); then
                MAX=$SCORE
            fi
            
            if (( $(echo "$SCORE < $MIN" | bc -l) )); then
                MIN=$SCORE
            fi
        done
        
        # Calculate average
        if [ $COUNT -gt 0 ]; then
            AVG=$(echo "scale=2; $SUM / $COUNT" | bc)
            echo "Average score: $AVG"
            echo "Highest score: $MAX"
            echo "Lowest score: $MIN"
        fi
    else
        echo "No score values found in the history file."
    fi
else
    echo "No score history file found: $HISTORY_FILE"
fi

# Check for cookie files
COOKIE_FILES=$(find cookies -name "high_score_cookies_*_*.json" | wc -l)
echo "Found $COOKIE_FILES high score cookie files."

# Display best score cookie
BEST_COOKIE=$(find cookies -name "high_score_cookies_*_*.json" | sort -r | head -1)
if [ -n "$BEST_COOKIE" ]; then
    BEST_SCORE=$(echo "$BEST_COOKIE" | grep -o "[0-9]\.[0-9]\+")
    echo "Best score cookie file: $BEST_COOKIE (Score: $BEST_SCORE)"
fi

echo "==========================="
echo "Analysis completed." 