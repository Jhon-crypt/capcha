#!/usr/bin/env python3
"""
reCAPTCHA v3 Score Analyzer

This script analyzes the score history from profile directories
and provides insights on what factors lead to higher scores.
"""

import os
import re
import glob
import json
import argparse
from datetime import datetime

def parse_score_history(file_path):
    """Parse a score history file and extract scores with timestamps"""
    scores = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                # Extract timestamp and score using regex
                match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}): Score (\d+\.\d+)', line)
                if match:
                    timestamp_str, score_str = match.groups()
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    score = float(score_str)
                    scores.append((timestamp, score))
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return scores

def analyze_cookies(cookie_file):
    """Analyze a cookie file to extract useful information"""
    try:
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)
            
        # Count cookies by domain
        domains = {}
        for cookie in cookies:
            domain = cookie.get('domain', 'unknown')
            domains[domain] = domains.get(domain, 0) + 1
            
        return {
            'total_cookies': len(cookies),
            'domains': domains
        }
    except Exception as e:
        print(f"Error analyzing {cookie_file}: {e}")
        return None

def analyze_high_score_factors(scores, threshold=0.7):
    """Analyze factors that might contribute to high scores"""
    if not scores:
        return {}
    
    high_scores = [s for s in scores if s[1] >= threshold]
    low_scores = [s for s in scores if s[1] < threshold]
    
    # Time of day analysis
    high_score_hours = [s[0].hour for s in high_scores]
    low_score_hours = [s[0].hour for s in low_scores]
    
    # Group into time periods
    time_periods = {
        'morning': (5, 11),    # 5 AM - 11 AM
        'afternoon': (12, 17), # 12 PM - 5 PM
        'evening': (18, 22),   # 6 PM - 10 PM
        'night': (23, 4)       # 11 PM - 4 AM
    }
    
    high_score_periods = {}
    for period, (start, end) in time_periods.items():
        if start < end:
            high_score_periods[period] = len([h for h in high_score_hours if start <= h <= end])
        else:  # Handle night period that crosses midnight
            high_score_periods[period] = len([h for h in high_score_hours if h >= start or h <= end])
    
    # Day of week analysis
    high_score_days = [s[0].weekday() for s in high_scores]
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    high_score_weekdays = {day_names[i]: high_score_days.count(i) for i in range(7)}
    
    return {
        'total_scores': len(scores),
        'high_scores': len(high_scores),
        'high_score_percentage': len(high_scores) / len(scores) * 100 if scores else 0,
        'average_score': sum(s[1] for s in scores) / len(scores) if scores else 0,
        'time_periods': high_score_periods,
        'weekdays': high_score_weekdays
    }

def main():
    parser = argparse.ArgumentParser(description='Analyze reCAPTCHA v3 scores')
    parser.add_argument('--profile', type=str, help='Profile directory to analyze')
    
    args = parser.parse_args()
    
    # Find all profile directories if no specific profile is provided
    if args.profile:
        profile_dirs = [os.path.join('profiles', args.profile)]
    else:
        profile_dirs = glob.glob('profiles/*')
    
    all_scores = []
    
    for profile_dir in profile_dirs:
        if not os.path.isdir(profile_dir):
            continue
            
        profile_name = os.path.basename(profile_dir)
        print(f"\nAnalyzing profile: {profile_name}")
        
        # Find score history file
        history_file = os.path.join(profile_dir, 'score_history.txt')
        if os.path.exists(history_file):
            scores = parse_score_history(history_file)
            all_scores.extend(scores)
            
            if scores:
                print(f"Found {len(scores)} score entries")
                print(f"Latest score: {scores[-1][1]}")
                print(f"Average score: {sum(s[1] for s in scores) / len(scores):.2f}")
                
                # Analyze high score factors
                factors = analyze_high_score_factors(scores)
                print(f"High score percentage: {factors['high_score_percentage']:.1f}%")
                
                # Show best time periods
                if factors['time_periods']:
                    best_period = max(factors['time_periods'].items(), key=lambda x: x[1])
                    print(f"Best time period: {best_period[0]} ({best_period[1]} high scores)")
                
                # Show best weekdays
                if factors['weekdays']:
                    best_day = max(factors['weekdays'].items(), key=lambda x: x[1])
                    print(f"Best weekday: {best_day[0]} ({best_day[1]} high scores)")
            else:
                print("No scores found in history file")
        else:
            print(f"No score history file found in {profile_dir}")
        
        # Analyze cookies
        cookie_files = glob.glob(os.path.join('cookies', f'high_score_cookies_*_{profile_name}.json'))
        if cookie_files:
            print(f"Found {len(cookie_files)} high score cookie files")
            latest_cookie_file = max(cookie_files, key=os.path.getmtime)
            cookie_info = analyze_cookies(latest_cookie_file)
            if cookie_info:
                print(f"Latest high score cookies: {cookie_info['total_cookies']} cookies from {len(cookie_info['domains'])} domains")
    
    if not all_scores:
        print("\nNo scores found in any profile. Run the script a few times to generate score data.")

if __name__ == "__main__":
    main() 