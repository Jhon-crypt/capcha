from seleniumbase import SB
import uuid
import os
import random
import time
import json
import string
import platform
import argparse
import re
from datetime import datetime, timedelta
import hashlib
import traceback
import glob
from seleniumbase import Driver
from seleniumbase.common.exceptions import NoSuchWindowException

# Create directories if they don't exist
for directory in ["screenshots", "cookies", "profiles"]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Constants
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0"
]

# Common search queries for establishing history
SEARCH_QUERIES = [
    "weather today",
    "news headlines",
    "recipe ideas",
    "vacation destinations",
    "movie reviews",
    "tech gadgets",
    "local restaurants",
    "fitness tips",
    "home improvement ideas",
    "book recommendations"
]

# Common websites to visit before target
COMMON_SITES = [
    "https://www.google.com",
    "https://www.wikipedia.org",
    "https://www.youtube.com",
    "https://www.reddit.com",
    "https://www.amazon.com",
    "https://www.nytimes.com",
    "https://www.github.com"
]

def human_like_delay(min_seconds=0.5, max_seconds=2.5):
    """Simulates human-like delay between actions"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def natural_mouse_movement(sb, target_element=None, num_points=15):
    """
    Simulates natural mouse movement with acceleration and deceleration
    If target_element is provided, moves to that element, otherwise moves randomly
    """
    # Get viewport size
    viewport_width = sb.execute_script("return window.innerWidth;")
    viewport_height = sb.execute_script("return window.innerHeight;")
    
    # Add micro-movements occasionally to simulate human indecision
    if random.random() < 0.3:  # 30% chance of micro-movements
        start_x = random.randint(0, viewport_width)
        start_y = random.randint(0, viewport_height)
        
        # Make 2-4 small movements in a small area
        for _ in range(random.randint(2, 4)):
            end_x = start_x + random.randint(-20, 20)
            end_y = start_y + random.randint(-20, 20)
            
            # Ensure we stay in viewport
            end_x = max(0, min(end_x, viewport_width))
            end_y = max(0, min(end_y, viewport_height))
            
            # Perform the micro-movement using JavaScript directly
            sb.driver.execute_script(
                f"""
                document.elementFromPoint({start_x}, {start_y}).dispatchEvent(
                    new MouseEvent('mousemove', {{clientX: {start_x}, clientY: {start_y}, bubbles: true}})
                );
                window.scrollBy({random.randint(-10, 10)}, {random.randint(-10, 10)});
                """
            )
            
            # Update start position for next micro-movement
            start_x, start_y = end_x, end_y
            
            # Small delay between micro-movements
            time.sleep(random.uniform(0.1, 0.3))
    
    # Starting position (random)
    start_x = random.randint(0, viewport_width)
    start_y = random.randint(0, viewport_height)
    
    # Target position
    if target_element:
        try:
            # Get element position 
            element_rect = sb.execute_script(
                "return arguments[0].getBoundingClientRect();", 
                target_element
            )
            end_x = element_rect['left'] + element_rect['width'] / 2
            end_y = element_rect['top'] + element_rect['height'] / 2
        except Exception as e:
            print(f"Error getting element position: {e}")
            # Fall back to random coordinates
            end_x = random.randint(0, viewport_width)
            end_y = random.randint(0, viewport_height)
    else:
        # Random target
        end_x = random.randint(0, viewport_width)
        end_y = random.randint(0, viewport_height)
    
    # Generate a natural curve between points with slight randomness
    points = []
    
    # Use a more natural curve (Bezier-like)
    for i in range(num_points):
        # Use bezier-like curve with randomness
        progress = i / (num_points - 1)
        
        # Add some randomness to the path - more in the middle, less at start/end
        randomness = 1 - abs(2 * progress - 1)  # More randomness in the middle
        random_offset_x = random.randint(-25, 25) * randomness
        random_offset_y = random.randint(-25, 25) * randomness
        
        # Bezier curve calculation (quadratic)
        control_x = (start_x + end_x) / 2 + random.randint(-100, 100)
        control_y = (start_y + end_y) / 2 + random.randint(-100, 100)
        
        t = progress
        x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x + random_offset_x
        y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y + random_offset_y
        
        # Ensure coordinates are within viewport
        x = max(0, min(viewport_width, x))
        y = max(0, min(viewport_height, y))
        
        points.append((x, y))
    
    # Move through the points with variable speed (slower at start and end)
    for i, (x, y) in enumerate(points):
        # Calculate delay - slower at beginning and end (ease in/out)
        progress = i / (num_points - 1)
        if progress < 0.2 or progress > 0.8:
            delay = random.uniform(0.01, 0.03)  # Slower
        else:
            delay = random.uniform(0.005, 0.01)  # Faster
            
        # Move mouse using JavaScript directly to avoid compatibility issues
        try:
            sb.driver.execute_script(
                f"""
                document.elementFromPoint({x}, {y}).dispatchEvent(
                    new MouseEvent('mousemove', {{clientX: {x}, clientY: {y}, bubbles: true}})
                );
                """
            )
            time.sleep(delay)
        except Exception as e:
            print(f"Error during mouse movement: {e}")
            continue
    
    # Optionally click if target_element was provided
    if target_element and random.random() > 0.3:
        try:
            # Sometimes double-click (rarely)
            if random.random() > 0.9:
                sb.double_click(target_element)
            else:
                sb.click(target_element)
        except Exception as e:
            print(f"Error clicking element: {e}")
    
    return True  # Indicate success

def natural_scroll(sb, min_pixels=100, max_pixels=500):
    """Performs natural scrolling to simulate human behavior"""
    # Get page height
    page_height = sb.execute_script("return document.body.scrollHeight;")
    viewport_height = sb.execute_script("return window.innerHeight;")
    
    # Current scroll position
    current_position = sb.execute_script("return window.pageYOffset;")
    
    # Determine scroll direction and amount
    if current_position < 100:
        # Near top, likely to scroll down
        direction = 1  # down
        probability_change_direction = 0.1
    elif current_position > page_height - viewport_height - 100:
        # Near bottom, likely to scroll up
        direction = -1  # up
        probability_change_direction = 0.1
    else:
        # Middle of page, could go either way
        direction = 1 if random.random() > 0.5 else -1
        probability_change_direction = 0.3
    
    # Small chance to change expected direction
    if random.random() < probability_change_direction:
        direction *= -1
    
    # Calculate scroll amount with some randomness
    base_amount = random.randint(min_pixels, max_pixels)
    scroll_amount = base_amount * direction
    
    # Execute scroll with a natural easing
    sb.execute_script(f"""
    (function() {{
        const duration = {random.randint(500, 1000)};
        const start = window.pageYOffset;
        const end = start + {scroll_amount};
        const startTime = performance.now();
        
        function easeInOutQuad(t) {{ 
            return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        }}
        
        function scroll() {{
            const elapsed = performance.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = easeInOutQuad(progress);
            const position = start + (end - start) * eased;
            
            window.scrollTo(0, position);
            
            if (progress < 1) {{
                requestAnimationFrame(scroll);
            }}
        }}
        
        requestAnimationFrame(scroll);
    }})();
    """)
    
    # Wait for scroll to complete
    human_like_delay(0.5, 1.5)

def simulate_reading(sb, min_time=5, max_time=15):
    """
    Simulates a human reading content on the page
    Uses only string-based selectors to avoid compatibility issues
    """
    # Calculate total reading time
    actual_time = random.uniform(min_time, max_time)
    start_time = time.time()
    
    # Use selector for text elements
    text_selector = "p, h1, h2, h3, h4, h5, h6, li, span, div:not(:empty)"
    
    try:
        # Count text elements first
        text_elements_count = len(sb.find_elements(text_selector))
        
        if text_elements_count == 0:
            print("No text elements found to read")
            time.sleep(actual_time)
            return
            
        # Determine how many elements to read
        elements_to_read = min(text_elements_count, max(3, int(actual_time / 2)))
        
        # Read some random elements
        for i in range(elements_to_read):
            # Check if we have reading time left
            if time.time() - start_time > actual_time:
                break
                
            # Pick a random element - using nth-child for direct CSS selection
            elem_idx = random.randint(1, text_elements_count)
            specific_text_selector = f"({text_selector}):nth-child({elem_idx})"
            
            # Check if element exists
            if not sb.is_element_present(specific_text_selector):
                # Try alternate approach using JavaScript
                try:
                    # Scroll to element using JavaScript
                    sb.execute_script(
                        f"""
                        var elements = document.querySelectorAll('{text_selector}');
                        if(elements.length >= {elem_idx}) {{
                            // Check if it has meaningful text
                            var text = elements[{elem_idx-1}].innerText.trim();
                            if(text.length > 15) {{
                                // Scroll with a slight offset
                                elements[{elem_idx-1}].scrollIntoView({{block: 'center'}});
                                // Small random scroll adjustment
                                window.scrollBy(0, {random.randint(-20, 20)});
                            }}
                        }}
                        """
                    )
                    
                    # Add some reading time
                    element_time = random.uniform(1.0, 3.0)
                    time.sleep(element_time)
                    
                    # Sometimes make small scroll adjustments while "reading"
                    if random.random() < 0.5:
                        sb.execute_script(f"window.scrollBy(0, {random.randint(-15, 15)});")
                        
                except Exception as e:
                    print(f"Error reading element via JavaScript: {e}")
                continue
                
            try:
                # Try to read using CSS selector
                # Scroll to element
                sb.scroll_to(specific_text_selector)
                
                # Small offset for more natural scrolling
                sb.execute_script(f"window.scrollBy(0, {random.randint(-20, 20)});")
                
                # Get element text length
                try:
                    text_length = len(sb.get_text(specific_text_selector))
                except:
                    text_length = 100  # Default if can't get text
                
                # Calculate reading time based on length
                reading_speed = random.uniform(3.0, 5.0)  # chars per second
                element_time = min(8.0, max(1.0, text_length / reading_speed))
                
                # Move mouse near text sometimes
                if random.random() < 0.6:
                    # Get element position for mouse movement
                    try:
                        # Just move mouse to element using built-in hover
                        sb.hover(specific_text_selector)
                    except:
                        pass
                
                # Actually "read" (wait)
                time.sleep(element_time)
                
                # Sometimes make small scroll adjustments while reading
                if random.random() < 0.7:
                    sb.execute_script(f"window.scrollBy(0, {random.randint(-20, 20)});")
                    time.sleep(0.5)
                
            except Exception as e:
                print(f"Error reading element {elem_idx}: {e}")
                continue
                
        # If there's remaining time, just wait
        remaining_time = actual_time - (time.time() - start_time)
        if remaining_time > 0:
            time.sleep(remaining_time)
            
    except Exception as e:
        print(f"Error during reading simulation: {e}")
        # Just wait the full time if there's an error
        remaining_time = actual_time - (time.time() - start_time)
        if remaining_time > 0:
            time.sleep(remaining_time)

def natural_typing(sb, selector, text, min_interval=0.05, max_interval=0.25):
    """Simulates natural typing with variable speed and occasional mistakes"""
    # Check if selector is a string or already a WebElement
    if isinstance(selector, str):
        element = sb.find_element(selector)
    else:
        # Already a WebElement
        element = selector
    
    sb.click(element)
    
    for char in text:
        # Occasionally make a typo and correct it
        if random.random() < 0.05:  # 5% chance of typo
            # Type a wrong character
            typo_char = random.choice(string.ascii_lowercase)
            sb.driver.execute_script(
                f"arguments[0].value += '{typo_char}';", element
            )
            human_like_delay(0.1, 0.3)
            
            # Delete the typo
            sb.driver.execute_script(
                "arguments[0].value = arguments[0].value.slice(0, -1);", element
            )
            human_like_delay(0.1, 0.3)
        
        # Type the correct character with variable speed
        sb.driver.execute_script(
            f"arguments[0].value += '{char}';", element
        )
        
        # Variable typing speed
        if char in ['.', ',', '!', '?', ' ']:
            # Pause longer after punctuation
            human_like_delay(max_interval, max_interval * 2)
        else:
            # Normal typing speed with variation
            human_like_delay(min_interval, max_interval)
            
        # Occasionally pause as if thinking
        if random.random() < 0.02:  # 2% chance
            human_like_delay(0.5, 1.5)

def save_cookies(sb, filename):
    """Saves browser cookies to a file"""
    try:
        cookies = sb.driver.get_cookies()
        
        # Organize cookies by domain for easier debugging
        current_url = sb.get_current_url()
        current_domain = current_url.split('//')[1].split('/')[0]
        
        # Add metadata to help with future loading
        cookie_data = {
            "metadata": {
                "saved_from_domain": current_domain,
                "saved_from_url": current_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_cookies": len(cookies)
            },
            "cookies": cookies
        }
        
        with open(filename, 'w') as f:
            json.dump(cookie_data, f, indent=2)
        
        print(f"Saved {len(cookies)} cookies to {filename}")
        return True
    except Exception as e:
        print(f"Error saving cookies: {e}")
        return False

def load_cookies(sb, cookies_file):
    """
    Load cookies from a file into the browser
    
    Args:
        sb: SeleniumBase instance
        cookies_file: Path to cookies file
        
    Returns:
        float: Score associated with the cookies, or None if not found
    """
    if not os.path.exists(cookies_file):
        print(f"Cookies file not found: {cookies_file}")
        return None
    
    try:
        with open(cookies_file, 'r') as f:
            cookie_data = json.load(f)
        
        # Extract score from metadata if available
        score = None
        if "metadata" in cookie_data and "score" in cookie_data["metadata"]:
            score = cookie_data["metadata"]["score"]
            print(f"Loading cookies with score: {score}")
        
        # Clear cookies first
        sb.delete_all_cookies()  # Clear existing cookies first
        
        # Add all cookies
        for cookie in cookie_data["cookies"]:
            try:
                sb.add_cookie(cookie)
            except Exception as e:
                print(f"Error adding cookie: {e}")
        
        print(f"Successfully loaded {len(cookie_data['cookies'])} cookies from {cookies_file}")
        return score
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return None

def modify_browser_fingerprint(sb):
    """Modifies the browser fingerprint to appear more human-like"""
    
    # JavaScript to set a realistic timezone
    js_timezone_script = """
        const timezone = 'America/New_York';
        Object.defineProperty(Intl, 'DateTimeFormat', {
            writable: true,
            configurable: true,
            value: new Proxy(Intl.DateTimeFormat, {
                construct(target, args) {
                    if (args.length > 0) {
                        const options = args[1] || {};
                        if (!options.timeZone) {
                            options.timeZone = timezone;
                            args[1] = options;
                        }
                    }
                    return Reflect.construct(target, args);
                }
            })
        });
        
        Object.defineProperty(Date.prototype, 'getTimezoneOffset', {
            writable: true,
            configurable: true,
            value: function() {
                // New York timezone offset is UTC-4 in summer (EDT) or UTC-5 in winter (EST)
                // Returns the offset in minutes
                // For EDT, this would be -240 (-4 hours * 60 minutes)
                return -240;
            }
        });
    """
    
    # JavaScript to modify WebGL fingerprint
    js_webgl_script = """
        // Override WebGL to make it more common
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            // Override common WebGL fingerprinting targets
            if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                return 'Google Inc. (NVIDIA)';
            }
            if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)';
            }
            return getParameter.apply(this, arguments);
        };
    """
    
    # JavaScript to modify Canvas fingerprint
    js_canvas_script = """
        // Override canvas methods to add subtle noise
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            if (type === 'image/png' && this.width > 0 && this.height > 0) {
                const context = this.getContext('2d');
                if (context) {
                    // Add subtle noise to the canvas
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    const data = imageData.data;
                    for (let i = 0; i < data.length; i += 4) {
                        // Add minor noise to color channels
                        data[i] = Math.max(0, Math.min(255, data[i] + Math.floor(Math.random() * 2)));
                        data[i+1] = Math.max(0, Math.min(255, data[i+1] + Math.floor(Math.random() * 2)));
                        data[i+2] = Math.max(0, Math.min(255, data[i+2] + Math.floor(Math.random() * 2)));
                    }
                    context.putImageData(imageData, 0, 0);
                }
            }
            return originalToDataURL.apply(this, arguments);
        };
    """
    
    try:
        print("Modifying timezone...")
        sb.execute_script(js_timezone_script)
        
        print("Modifying WebGL fingerprint...")
        sb.execute_script(js_webgl_script)
        
        print("Modifying canvas fingerprint...")
        sb.execute_script(js_canvas_script)
        
        print("Browser fingerprint modifications applied")
    except Exception as e:
        print(f"Error modifying browser fingerprint: {e}")
        traceback.print_exc()

def visit_google_and_search(sb):
    """Visit Google and perform a search to establish browsing history"""
    print("Visiting Google to establish browsing history...")
    sb.open("https://www.google.com")
    human_like_delay(1, 2)
    
    # Type a search query with realistic typing speed
    search_query = random.choice(SEARCH_QUERIES)
    
    try:
        # Try different possible selectors for Google search input
        search_input = None
        selectors = [
            'input[name="q"]',
            'textarea[name="q"]',  # Google sometimes uses textarea instead of input
            'input[title="Search"]',
            'textarea[title="Search"]',
            '.gLFyf'  # Class name sometimes used
        ]
        
        for selector in selectors:
            try:
                if sb.is_element_present(selector, timeout=2):
                    search_input = sb.find_element(selector)
                    break
            except:
                continue
        
        if search_input:
            # Type with realistic speed and patterns
            sb.click(search_input)
            for char in search_query:
                # Occasionally make a typo and correct it
                if random.random() < 0.05:  # 5% chance of typo
                    # Type a wrong character
                    typo_char = random.choice(string.ascii_lowercase)
                    sb.driver.execute_script(
                        f"arguments[0].value += '{typo_char}';", search_input
                    )
                    human_like_delay(0.1, 0.3)
                    
                    # Delete the typo
                    sb.driver.execute_script(
                        "arguments[0].value = arguments[0].value.slice(0, -1);", search_input
                    )
                    human_like_delay(0.1, 0.3)
                
                # Type the correct character with variable speed
                sb.driver.execute_script(
                    f"arguments[0].value += '{char}';", search_input
                )
                
                # Variable typing speed
                if char in ['.', ',', '!', '?', ' ']:
                    # Pause longer after punctuation
                    human_like_delay(0.2, 0.4)
                else:
                    # Normal typing speed with variation
                    human_like_delay(0.05, 0.2)
                    
                # Occasionally pause as if thinking
                if random.random() < 0.02:  # 2% chance
                    human_like_delay(0.5, 1.5)
            
            human_like_delay(0.5, 1)
            
            # Sometimes press Enter, sometimes click the search button
            if random.random() > 0.5:
                sb.press_enter()
            else:
                # Try to find search button with different selectors
                search_buttons = sb.find_elements('input[name="btnK"], button[name="btnK"], .gNO89b')
                if search_buttons:
                    natural_mouse_movement(sb, search_buttons[0])
                    sb.click(search_buttons[0])
                else:
                    # If button not found, just press enter
                    sb.press_enter()
            
            human_like_delay(2, 3)
            
            # Interact with search results
            search_results = sb.find_elements("xpath", "//div[@class='g']//a | //div[@class='yuRUbf']//a")
            if search_results:
                # Click on a random search result
                result_to_click = random.choice(search_results[:3])  # Usually people click top results
                natural_mouse_movement(sb, result_to_click)
                sb.click(result_to_click)
                
                # Spend some time on the page
                human_like_delay(3, 6)
                
                # Scroll and read
                for _ in range(random.randint(1, 3)):
                    natural_scroll(sb)
                    human_like_delay(1, 3)
                
                simulate_reading(sb)
                
                # Go back to Google
                sb.go_back()
                sb.wait_for_ready_state_complete()
                human_like_delay(1, 2)
        else:
            print("Could not find Google search input, skipping search")
    except Exception as e:
        print(f"Error during Google search: {e}")
        # Go back to Google homepage
        try:
            sb.open("https://www.google.com")
            human_like_delay(1, 2)
        except:
            pass

def build_browsing_history(sb, num_sites=2):
    """Build browsing history by visiting common sites"""
    sites_to_visit = random.sample(COMMON_SITES, min(num_sites, len(COMMON_SITES)))
    
    for site in sites_to_visit:
        try:
            print(f"Visiting {site} to build browsing history...")
            sb.open(site)
            sb.wait_for_ready_state_complete()
            human_like_delay(2, 4)
            
            # Scroll and interact
            for _ in range(random.randint(1, 3)):
                natural_scroll(sb)
                human_like_delay(1, 2)
            
            # Move mouse randomly
            for _ in range(random.randint(2, 4)):
                natural_mouse_movement(sb)
                human_like_delay(0.5, 1.5)
            
            # Simulate reading
            simulate_reading(sb)
            
            # Interact with random elements
            try:
                elements = sb.find_elements("a, button")
                if elements:
                    # Filter visible elements
                    visible_elements = [e for e in elements if sb.is_element_visible(e)]
                    if visible_elements:
                        # Click a random element
                        element = random.choice(visible_elements[:10])  # Limit to first 10 to avoid footers etc.
                        natural_mouse_movement(sb, element)
                        sb.click(element)
                        human_like_delay(2, 4)
                        
                        # Go back
                        sb.go_back()
                        sb.wait_for_ready_state_complete()
                        human_like_delay(1, 2)
            except:
                pass
                
        except Exception as e:
            print(f"Error visiting {site}: {e}")

def get_recaptcha_score(profile_name=None, build_history=True):
    """Main function to get reCAPTCHA score with human-like behavior"""
    # Generate a unique ID for this run
    run_id = str(uuid.uuid4())[:8]
    cookies_file = f"cookies/browser_cookies.json"
    
    # Use a specific profile if provided
    profile_dir = None
    if profile_name:
        profile_dir = os.path.join("profiles", profile_name)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
    
    # Configure SeleniumBase with more human-like settings
    with SB(uc=True, headless=False, user_data_dir=profile_dir) as sb:
        # Set window size to a common desktop resolution with slight randomness
        width = random.randint(1200, 1400)
        height = random.randint(750, 850)
        sb.set_window_size(width, height)
        
        # Modify browser fingerprint
        modify_browser_fingerprint(sb)
        
        # Build browsing history if enabled
        if build_history:
            # First visit Google and perform a search
            visit_google_and_search(sb)
            
            # Visit some common sites
            build_browsing_history(sb, num_sites=random.randint(1, 3))
            
            # Save cookies
            save_cookies(sb, cookies_file)
        
        # Now visit the target site
        target_url = 'https://antcpt.com/score_detector/'
        print(f'Opening target site: {target_url}')
        
        # Open the page normally
        sb.open(target_url)
        
        # Load cookies if available
        if os.path.exists(cookies_file):
            print("Loading saved cookies...")
            try:
                sb.driver.delete_all_cookies()  # Clear existing cookies first
                load_cookies(sb, cookies_file)
                sb.refresh()  # Refresh to apply cookies
                sb.wait_for_ready_state_complete()
            except Exception as e:
                print(f"Error loading cookies: {e}")
        
        # Wait for page to fully load
        sb.wait_for_ready_state_complete()
        print("Page loaded, now behaving like a human...")
        
        # Simulate human-like behavior
        human_like_delay(1, 3)
        
        # Simulate reading the page content
        simulate_reading(sb, 5, 12)
        
        # Perform some natural mouse movements
        for _ in range(random.randint(3, 5)):
            natural_mouse_movement(sb, num_points=random.randint(10, 20))
            human_like_delay(0.5, 1.5)
        
        # Scroll down and up naturally
        for _ in range(random.randint(2, 4)):
            natural_scroll(sb)
            human_like_delay(1, 2)
        
        # Interact with the page - find and hover over some elements
        try:
            elements = sb.find_elements("a, button, input")
            if elements:
                # Filter to visible elements
                visible_elements = [e for e in elements if sb.is_element_visible(e)]
                if visible_elements:
                    # Select a few random elements to interact with
                    num_to_interact = min(random.randint(2, 4), len(visible_elements))
                    elements_to_interact = random.sample(visible_elements, num_to_interact)
                    
                    for element in elements_to_interact:
                        # Hover over element
                        natural_mouse_movement(sb, element)
                        human_like_delay(0.5, 1.5)
                        
                        # Sometimes click non-essential elements
                        element_text = element.text.lower() if hasattr(element, 'text') else ""
                        if (random.random() > 0.7 and 
                            "refresh" not in element_text and 
                            "clear" not in element_text):
                            sb.click(element)
                            human_like_delay(2, 3)
                            # Go back if needed
                            if sb.get_current_url() != target_url:
                                sb.go_back()
                                sb.wait_for_ready_state_complete()
                                human_like_delay(1, 2)
        except Exception as e:
            print(f"Error during interaction: {e}")
        
        # Final wait to ensure score is calculated
        wait_time = random.randint(5, 10)
        print(f"Waiting final {wait_time} seconds for score calculation...")
        sb.sleep(wait_time)
        
        # Take screenshot
        screenshot_path = f"screenshots/score_detector_{run_id}.png"
        sb.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        
        # Try to extract the score
        try:
            score = extract_score(sb)
            if score and float(score) >= 0.7:
                print(f"High score achieved ({score})! Saving cookies for future use.")
                save_cookies(sb, f"cookies/high_score_cookies_{score}_{run_id}.json")
                
                # If using a profile, make a note of the high score
                if profile_name:
                    with open(os.path.join(profile_dir, "score_history.txt"), "a") as f:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"{timestamp}: Score {score} (Run ID: {run_id})\n")
            
            return score
        except Exception as e:
            print(f"Could not find score element: {e}")
        
        return None

def interact_with_page(sb, interaction_time=30):
    """
    Simulates a user naturally interacting with page elements
    Uses only string-based selectors to avoid compatibility issues
    """
    start_time = time.time()
    
    # Selectors for different element types
    button_selector = "button, .btn, input[type='button'], input[type='submit'], a.button"
    input_selector = "input[type='text'], input[type='email'], textarea"
    checkbox_selector = "input[type='checkbox']"
    link_selector = "a"
    
    # Count elements of each type
    try:
        buttons_count = len(sb.find_elements(button_selector))
        inputs_count = len(sb.find_elements(input_selector))
        checkboxes_count = len(sb.find_elements(checkbox_selector))
        links_count = len(sb.find_elements(link_selector))
        print(f"Found {buttons_count} buttons, {inputs_count} inputs, {checkboxes_count} checkboxes, {links_count} links")
    except Exception as e:
        print(f"Error counting page elements: {e}")
        buttons_count = inputs_count = checkboxes_count = links_count = 0
    
    # If no interactive elements, just scroll and move
    if buttons_count + inputs_count + checkboxes_count + links_count == 0:
        print("No interactive elements found, just scrolling")
        try:
            # Simple scrolling
            viewport_height = sb.execute_script("return window.innerHeight;")
            sb.execute_script(f"window.scrollBy(0, {viewport_height/2});")
            human_like_delay(1, 2)
            
            sb.execute_script(f"window.scrollBy(0, {viewport_height/2});")
            human_like_delay(1, 2)
            
            sb.execute_script(f"window.scrollBy(0, -{viewport_height/3});")
            human_like_delay(1, 2)
            
            # Simple mouse movements
            viewport_width = sb.execute_script("return window.innerWidth;")
            
            for _ in range(3):
                x = random.randint(0, viewport_width)
                y = random.randint(0, viewport_height)
                
                sb.execute_script(
                    f"document.elementFromPoint({x}, {y}).dispatchEvent("
                    f"new MouseEvent('mousemove', {{clientX: {x}, clientY: {y}, bubbles: true}}));"
                )
                human_like_delay(0.5, 1.5)
        except Exception as e:
            print(f"Error during simple page interaction: {e}")
        return
    
    # Try to interact with input fields (1-2 of them)
    if inputs_count > 0:
        print("Interacting with input fields")
        try:
            # Choose up to 2 random inputs
            max_inputs = min(2, inputs_count)
            for _ in range(max_inputs):
                # Only try if we have time left
                if time.time() - start_time > interaction_time * 0.7:
                    break
                
                # Generate a random index for an input element
                input_idx = random.randint(1, inputs_count)
                
                # Use CSS nth-child to get a specific input element
                # nth-child is 1-indexed
                specific_input_selector = f"({input_selector}):nth-child({input_idx})"
                
                # Check if element exists
                if not sb.is_element_present(specific_input_selector):
                    # Try alternate approach - get all and use JavaScript
                    try:
                        sb.execute_script(
                            f"""
                            var inputs = document.querySelectorAll('{input_selector}');
                            if(inputs.length >= {input_idx}) {{
                                inputs[{input_idx-1}].scrollIntoView({{block: 'center'}});
                            }}
                            """
                        )
                        human_like_delay(0.5, 1.0)
                        
                        # Try to fill via JavaScript
                        text = f"test input {random.randint(1000, 9999)}"
                        sb.execute_script(
                            f"""
                            var inputs = document.querySelectorAll('{input_selector}');
                            if(inputs.length >= {input_idx}) {{
                                inputs[{input_idx-1}].focus();
                                inputs[{input_idx-1}].value = '{text}';
                            }}
                            """
                        )
                        human_like_delay(1.0, 2.0)
                    except:
                        pass
                    continue
                
                # Try to interact with the specific input
                try:
                    # Scroll into view
                    sb.scroll_to(specific_input_selector)
                    human_like_delay(0.5, 1.0)
                    
                    # Click to focus
                    sb.click(specific_input_selector)
                    human_like_delay(0.5, 1.0)
                    
                    # Type some text
                    text = f"test input {random.randint(1000, 9999)}"
                    for char in text:
                        sb.send_keys(specific_input_selector, char)
                        human_like_delay(0.05, 0.2)
                    
                    human_like_delay(0.5, 1.5)
                except Exception as e:
                    print(f"Error interacting with input {input_idx}: {e}")
            
        except Exception as e:
            print(f"Error in input interaction section: {e}")
    
    # Try to interact with buttons (1-2 of them)
    if buttons_count > 0 and time.time() - start_time < interaction_time * 0.8:
        print("Interacting with buttons")
        try:
            # Choose 1-2 random buttons
            max_buttons = min(2, buttons_count)
            for _ in range(max_buttons):
                # Only try if we have time left
                if time.time() - start_time > interaction_time * 0.9:
                    break
                
                # Generate a random index for a button
                button_idx = random.randint(1, buttons_count)
                
                # Use CSS nth-child to get a specific button
                # Be careful as nth-child is 1-indexed
                specific_button_selector = f"({button_selector}):nth-child({button_idx})"
                
                # Check if element exists and is visible
                if not sb.is_element_present(specific_button_selector) or not sb.is_element_visible(specific_button_selector):
                    # Try alternate approach - direct JavaScript
                    try:
                        # Get button text via JavaScript to check if safe to click
                        button_text = sb.execute_script(
                            f"""
                            var buttons = document.querySelectorAll('{button_selector}');
                            if(buttons.length >= {button_idx}) {{
                                buttons[{button_idx-1}].scrollIntoView({{block: 'center'}});
                                return buttons[{button_idx-1}].textContent.toLowerCase();
                            }}
                            return '';
                            """
                        )
                        
                        # Check if safe to click
                        if any(keyword in button_text for keyword in ['delete', 'remove', 'logout', 'sign out']):
                            continue
                            
                        # Only click submit buttons at the end
                        if ('submit' in button_text or 'send' in button_text) and time.time() - start_time <= interaction_time * 0.9:
                            continue
                            
                        # Click the button
                        sb.execute_script(
                            f"""
                            var buttons = document.querySelectorAll('{button_selector}');
                            if(buttons.length >= {button_idx}) {{
                                buttons[{button_idx-1}].click();
                            }}
                            """
                        )
                        human_like_delay(1.0, 2.0)
                    except:
                        pass
                    continue
                
                # Try to interact with the specific button
                try:
                    # Check button text to avoid destructive actions
                    button_text = sb.get_text(specific_button_selector).lower()
                    if any(keyword in button_text for keyword in ['delete', 'remove', 'logout', 'sign out']):
                        continue
                    
                    # Skip submit buttons unless it's near the end of our interaction time
                    if ('submit' in button_text or 'send' in button_text) and time.time() - start_time <= interaction_time * 0.9:
                        continue
                    
                    # Scroll to button
                    sb.scroll_to(specific_button_selector)
                    human_like_delay(0.5, 1.0)
                    
                    # Click button
                    sb.click(specific_button_selector)
                    human_like_delay(1.0, 2.0)
                    
                except Exception as e:
                    print(f"Error interacting with button {button_idx}: {e}")
        except Exception as e:
            print(f"Error in button interaction section: {e}")
    
    # Try to interact with links (1 of them)
    if links_count > 0 and time.time() - start_time < interaction_time * 0.7:
        print("Interacting with links")
        try:
            # Choose 1 random link
            for _ in range(1):
                if time.time() - start_time > interaction_time * 0.8:
                    break
                
                # Generate a random index for a link
                link_idx = random.randint(1, links_count)
                
                # Use CSS nth-child to get a specific link
                specific_link_selector = f"({link_selector}):nth-child({link_idx})"
                
                # Check if element exists
                if not sb.is_element_present(specific_link_selector) or not sb.is_element_visible(specific_link_selector):
                    # Try alternate approach
                    try:
                        # Use JavaScript to check link safety
                        link_info = sb.execute_script(
                            f"""
                            var links = document.querySelectorAll('{link_selector}');
                            if(links.length >= {link_idx}) {{
                                links[{link_idx-1}].scrollIntoView({{block: 'center'}});
                                return {{
                                    text: links[{link_idx-1}].textContent.toLowerCase(),
                                    href: links[{link_idx-1}].href || ''
                                }};
                            }}
                            return null;
                            """
                        )
                        
                        if link_info:
                            # Skip unsafe links
                            if any(keyword in link_info['text'] or keyword in link_info['href'] 
                                   for keyword in ['logout', 'sign out', 'delete']):
                                continue
                                
                            # Click the link
                            sb.execute_script(
                                f"""
                                var links = document.querySelectorAll('{link_selector}');
                                if(links.length >= {link_idx}) {{
                                    // Store URL to check if we navigate away
                                    var currentUrl = window.location.href;
                                    links[{link_idx-1}].click();
                                }}
                                """
                            )
                            
                            # Wait to see if page changed
                            human_like_delay(2.0, 3.0)
                            
                            # Go back if we navigated away
                            current_url = sb.get_current_url()
                            if "antcpt.com/score_detector" not in current_url:
                                sb.go_back()
                                sb.wait_for_ready_state_complete()
                                human_like_delay(1.0, 2.0)
                    except:
                        pass
                    continue
                
                # Try to interact with the specific link
                try:
                    # Check link text and href
                    link_text = sb.get_text(specific_link_selector).lower()
                    link_href = sb.get_attribute(specific_link_selector, "href")
                    
                    # Skip unsafe links
                    if any(keyword in link_text or (link_href and keyword in link_href) 
                           for keyword in ['logout', 'sign out', 'delete']):
                        continue
                    
                    # Scroll to link
                    sb.scroll_to(specific_link_selector)
                    human_like_delay(0.5, 1.0)
                    
                    # Click link
                    sb.click(specific_link_selector)
                    human_like_delay(2.0, 3.0)
                    
                    # Go back if we navigated away
                    current_url = sb.get_current_url()
                    if "antcpt.com/score_detector" not in current_url:
                        sb.go_back()
                        sb.wait_for_ready_state_complete()
                        human_like_delay(1.0, 2.0)
                        
                except Exception as e:
                    print(f"Error interacting with link {link_idx}: {e}")
        except Exception as e:
            print(f"Error in link interaction section: {e}")
    
    # Try to interact with checkboxes
    if checkboxes_count > 0 and time.time() - start_time < interaction_time * 0.9:
        print("Interacting with checkboxes")
        try:
            # Try to interact with 1 checkbox
            for _ in range(1):
                # Generate a random index
                checkbox_idx = random.randint(1, checkboxes_count)
                
                # Use CSS nth-child to get specific checkbox
                specific_checkbox_selector = f"({checkbox_selector}):nth-child({checkbox_idx})"
                
                # Check if element exists
                if not sb.is_element_present(specific_checkbox_selector) or not sb.is_element_visible(specific_checkbox_selector):
                    # Try alternate approach
                    try:
                        # Toggle checkbox via JavaScript
                        sb.execute_script(
                            f"""
                            var checkboxes = document.querySelectorAll('{checkbox_selector}');
                            if(checkboxes.length >= {checkbox_idx}) {{
                                checkboxes[{checkbox_idx-1}].scrollIntoView({{block: 'center'}});
                                checkboxes[{checkbox_idx-1}].click();
                            }}
                            """
                        )
                        human_like_delay(0.5, 1.0)
                    except:
                        pass
                    continue
                
                # Try to interact with specific checkbox
                try:
                    # Scroll to checkbox
                    sb.scroll_to(specific_checkbox_selector)
                    human_like_delay(0.5, 1.0)
                    
                    # Check if it's already checked
                    is_checked = sb.is_selected(specific_checkbox_selector)
                    
                    # Toggle checkbox (favor checking)
                    if random.random() < 0.7:  # 70% chance to check
                        if not is_checked:
                            sb.click(specific_checkbox_selector)
                    else:
                        # Toggle current state
                        sb.click(specific_checkbox_selector)
                        
                    human_like_delay(0.5, 1.0)
                    
                except Exception as e:
                    print(f"Error interacting with checkbox {checkbox_idx}: {e}")
                    
        except Exception as e:
            print(f"Error in checkbox interaction section: {e}")
    
    # Add some scrolling at the end
    try:
        viewport_height = sb.execute_script("return window.innerHeight;")
        
        # Scroll down
        sb.execute_script(f"window.scrollBy(0, {viewport_height * 0.6});")
        human_like_delay(1.0, 1.5)
        
        # Scroll up a bit
        sb.execute_script(f"window.scrollBy(0, -{viewport_height * 0.3});")
        human_like_delay(0.5, 1.0)
    except Exception as e:
        print(f"Error during final scrolling: {e}")
    
    # Final mouse movement
    try:
        viewport_width = sb.execute_script("return window.innerWidth;")
        viewport_height = sb.execute_script("return window.innerHeight;")
        
        # Random coordinates
        x = random.randint(0, viewport_width)
        y = random.randint(0, viewport_height)
        
        # Move mouse
        sb.execute_script(
            f"document.elementFromPoint({x}, {y}).dispatchEvent("
            f"new MouseEvent('mousemove', {{clientX: {x}, clientY: {y}, bubbles: true}}));"
        )
    except Exception as e:
        print(f"Error during final mouse movement: {e}")

def simulate_browser_history(sb, num_sites=3, min_time=3, max_time=8):
    """
    Visits common websites briefly to simulate normal browsing history
    before going to the target site.
    
    Args:
        sb: SeleniumBase instance
        num_sites: Number of sites to visit (default 3)
        min_time: Minimum time to spend on each site in seconds
        max_time: Maximum time to spend on each site in seconds
    """
    common_sites = [
        "https://www.wikipedia.org",
        "https://www.weather.com",
        "https://www.reddit.com",
        "https://www.nytimes.com",
        "https://www.theguardian.com",
        "https://www.bbc.com/news",
        "https://www.cnn.com",
        "https://www.amazon.com",
        "https://www.youtube.com",
        "https://www.imdb.com"
    ]
    
    # Randomly select a few sites to visit
    sites_to_visit = random.sample(common_sites, min(num_sites, len(common_sites)))
    
    print(f"Simulating browser history by visiting {num_sites} sites...")
    for site in sites_to_visit:
        try:
            print(f"Visiting {site}")
            sb.open(site)
            
            # Simulate some scrolling and reading
            visit_time = random.uniform(min_time, max_time)
            natural_scrolling(sb, scroll_count=random.randint(2, 5))
            time.sleep(visit_time)
            
            # Maybe click something (low probability)
            if random.random() < 0.3:
                try:
                    links = sb.find_elements("tag name", "a")
                    if links and len(links) > 0:
                        link = random.choice(links)
                        link_href = link.get_attribute("href")
                        # Only click if it's on the same domain to avoid getting lost
                        if link_href and site in link_href:
                            natural_mouse_movement(sb, target_element=link, should_click=True)
                            time.sleep(random.uniform(min_time/2, max_time/2))
                            sb.go_back()
                except Exception as e:
                    print(f"Error clicking link: {e}")
        except Exception as e:
            print(f"Error visiting {site}: {e}")
            continue
    
    print("Finished browser history simulation")

def run_score_detector(profile_name=None, build_history=True, headless=False):
    """Runs the reCAPTCHA score detector with the specified options"""
    run_id = hashlib.md5(f"{datetime.now()}".encode()).hexdigest()[:8]
    
    # Create profile directory if it doesn't exist
    if profile_name:
        profile_dir = os.path.join("profiles", profile_name)
        os.makedirs(profile_dir, exist_ok=True)
    else:
        profile_dir = None
    
    sb = None
    try:
        # Start a SeleniumBase browser
        sb = init_browser(profile_dir=profile_dir, headless=headless)
        
        # Modify browser fingerprint to make it more human-like
        modify_browser_fingerprint(sb)
        
        # Load any existing high-score cookies
        cookies_file = find_best_cookies(profile_dir) if profile_dir else None
        if cookies_file:
            prev_score = load_cookies(sb, cookies_file)
            print(f"Loaded cookies from {cookies_file} (score: {prev_score})")
        
        # Simulate browser history before going to the target site
        if build_history:
            simulate_browser_history(sb, num_sites=random.randint(2, 4))
        
        # Visit the reCAPTCHA test site
        print("Visiting reCAPTCHA test site...")
        sb.open("https://antcpt.com/score_detector/")
        
        # Wait for page to load
        print("Waiting for page to load...")
        sb.wait_for_element_present("body", timeout=10)
        
        # Add some "thinking" time before interacting
        human_like_delay(1, 3)
        
        # Interact with the page to make behavior look natural
        print("Simulating natural browsing behavior...")
        
        # Simulate natural reading
        print("Simulating reading...")
        simulate_reading(sb)
        
        # Interact with elements on the page
        print("Interacting with page elements...")
        interact_with_page(sb)
        
        # Wait for results
        print("Waiting for results...")
        sb.sleep(5)  # Let any animations complete
        
        # Try to extract the score
        try:
            score = extract_score(sb)
            if score and float(score) >= 0.7:
                print(f"High score achieved ({score})! Saving cookies for future use.")
                save_cookies(sb, f"cookies/high_score_cookies_{score}_{run_id}.json")
                
                # If using a profile, make a note of the high score
                if profile_name:
                    with open(os.path.join(profile_dir, "score_history.txt"), "a") as f:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"{timestamp}: Score {score} (Run ID: {run_id})\n")
            
            return score
        except Exception as e:
            print(f"Could not find score element: {e}")
            return None
    
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return None
    
    finally:
        # Always take a screenshot at the end
        try:
            if sb:
                sb.save_screenshot(f"screenshots/final_{run_id}.png", folder="")
        except Exception as e:
            print(f"Error taking screenshot: {e}")
        
        # Close the browser properly
        try:
            if sb:
                sb.quit()  # Using quit() directly on the Driver object
        except Exception as e:
            print(f"Error closing browser: {e}")
            pass

def save_browser_cookies(sb):
    """Saves all browser cookies to a file"""
    try:
        cookies_file = "cookies/browser_cookies.json"
        cookies = sb.get_cookies()
        
        # Organize cookies by domain for easier debugging
        current_url = sb.get_current_url()
        current_domain = current_url.split('//')[1].split('/')[0]
        
        # Add metadata to help with future loading
        cookie_data = {
            "metadata": {
                "saved_from_domain": current_domain,
                "saved_from_url": current_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_cookies": len(cookies)
            },
            "cookies": cookies
        }
        
        with open(cookies_file, 'w') as f:
            json.dump(cookie_data, f, indent=2)
        
        print(f"Saved {len(cookies)} cookies to {cookies_file}")
        return True
    except Exception as e:
        print(f"Error saving browser cookies: {e}")
        return False

def save_high_score_cookies(sb, score, run_id):
    """Saves cookies when a high score is achieved"""
    try:
        cookies_file = f"cookies/high_score_cookies_{score}_{run_id}.json"
        cookies = sb.get_cookies()
        
        # Organize cookies by domain
        current_url = sb.get_current_url()
        current_domain = current_url.split('//')[1].split('/')[0]
        
        # Add metadata
        cookie_data = {
            "metadata": {
                "saved_from_domain": current_domain,
                "saved_from_url": current_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "score": score,
                "run_id": run_id,
                "total_cookies": len(cookies)
            },
            "cookies": cookies
        }
        
        with open(cookies_file, 'w') as f:
            json.dump(cookie_data, f, indent=2)
        
        print(f"Saved {len(cookies)} cookies to {cookies_file}")
        return True
    except Exception as e:
        print(f"Error saving high score cookies: {e}")
        return False

def extract_score(sb):
    """Extracts the reCAPTCHA score from the page using multiple methods"""
    try:
        # Method 1: Try to find score via the standard element
        print("Looking for score via standard element...")
        found_score = False
        
        # Try different XPath expressions
        score_xpaths = [
            "//div[contains(text(), 'Your score is:')]",
            "//div[contains(., 'Your score is:')]",
            "//p[contains(text(), 'Your score is:')]",
            "//p[contains(., 'Your score is:')]",
            "//span[contains(text(), 'Your score is:')]",
            "//*[contains(text(), 'Your score is:')]"
        ]
        
        for xpath in score_xpaths:
            try:
                if sb.is_element_present(xpath):
                    score_element = sb.find_element(xpath)
                    score_text = sb.get_text(xpath)
                    print(f"Found score element with text: {score_text}")
                    
                    # Extract numeric score
                    if "Your score is: " in score_text:
                        score_str = score_text.split("Your score is: ")[1].strip()
                        try:
                            score_value = float(score_str)
                            print(f"Extracted score: {score_value}")
                            return score_value
                        except:
                            print(f"Failed to convert '{score_str}' to float")
                    
                    found_score = True
                    break
            except Exception as e:
                print(f"Error with xpath {xpath}: {e}")
                continue
        
        # Method 2: Try to find it via JavaScript
        print("Looking for score via JavaScript...")
        try:
            js_result = sb.execute_script("""
            // Try to find any element containing the score text
            const elements = Array.from(document.querySelectorAll('*'));
            for (const element of elements) {
                if (element.innerText && element.innerText.includes('Your score is:')) {
                    return element.innerText;
                }
            }
            return null;
            """)
            
            if js_result:
                print(f"Found score text via JavaScript: {js_result}")
                # Extract the score with regex
                score_match = re.search(r"Your score is:\s*([\d\.]+)", js_result)
                if score_match:
                    try:
                        score = float(score_match.group(1))
                        print(f"Extracted score from JS: {score}")
                        return score
                    except:
                        print(f"Failed to convert JS result to float")
        except Exception as e:
            print(f"Error with JavaScript extraction: {e}")
        
        # Method 3: Check the page source
        print("Looking for score in page source...")
        page_source = sb.get_page_source()
        
        # Look for the score in a few different formats
        score_patterns = [
            r"Your score is:\s*([\d\.]+)",
            r"score is:\s*([\d\.]+)",
            r"score:\s*([\d\.]+)",
            r"score\s*=\s*([\d\.]+)",
        ]
        
        for pattern in score_patterns:
            score_match = re.search(pattern, page_source)
            if score_match:
                try:
                    score = float(score_match.group(1))
                    print(f"Found score in page source: {score}")
                    return score
                except:
                    continue
        
        # Method 4: Try to screenshot the page for manual inspection
        print("Taking additional screenshot for score detection...")
        unique_id = str(uuid.uuid4())[:8]
        sb.save_screenshot(f"screenshots/score_debug_{unique_id}.png", folder="")
        
        # Look for any floating point number in the source
        print("Looking for any likely score values...")
        likely_scores = re.findall(r"0\.[1-9][0-9]?", page_source)
        if likely_scores:
            print(f"Possible score values found: {likely_scores}")
            # Return the highest score found as a guess
            highest_score = max([float(s) for s in likely_scores])
            print(f"Highest likely score: {highest_score}")
            return highest_score
            
        print("Could not find score using any method")
        return None
    except Exception as e:
        print(f"Error extracting score: {e}")
        return None

def load_best_cookies():
    """
    Loads the best high score cookies found in cookies directory
    Returns the cookies from the file with the highest score
    """
    try:
        # Find all high score cookie files
        cookie_files = [f for f in os.listdir("cookies") if f.startswith("high_score_cookies_")]
        
        if not cookie_files:
            print("No high score cookies found")
            return None
            
        # Find the file with the highest score
        best_file = None
        best_score = 0.0
        
        for file in cookie_files:
            try:
                # Extract score from filename
                score_part = file.split("_")[3]  # high_score_cookies_0.9_runid.json
                score = float(score_part)
                
                if score > best_score:
                    best_score = score
                    best_file = file
            except:
                continue
                
        if best_file:
            print(f"Loading cookies from highest score file: {best_file} (score: {best_score})")
            with open(os.path.join("cookies", best_file), 'r') as f:
                data = json.load(f)
                
            # Handle both old and new format
            if isinstance(data, dict) and "cookies" in data:
                cookies = data["cookies"]
                metadata = data.get("metadata", {})
                if metadata:
                    print(f"Cookies saved from: {metadata.get('saved_from_domain', 'unknown')} on {metadata.get('timestamp', 'unknown date')}")
            else:
                cookies = data
                
            return cookies
        
        return None
    except Exception as e:
        print(f"Error loading best cookies: {e}")
        return None

def natural_scrolling(sb, scroll_amount=None, direction="down", scroll_count=None):
    """
    Performs natural scrolling with human-like acceleration and deceleration
    """
    # Get page height
    page_height = sb.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
    viewport_height = sb.execute_script("return window.innerHeight;")
    max_scroll = page_height - viewport_height
    
    # If no scroll amount provided, calculate a reasonable one based on page size
    if scroll_amount is None:
        # More variable scroll amounts to appear more natural
        scroll_amount = random.randint(int(viewport_height * 0.3), int(viewport_height * 0.7))
    
    # If no scroll count provided, determine a reasonable number
    if scroll_count is None:
        # Add more randomness to scroll count
        if page_height > viewport_height * 3:
            scroll_count = random.randint(3, 7)  # More scrolls for longer pages
        else:
            scroll_count = random.randint(1, 3)  # Fewer scrolls for shorter pages
    
    # Convert string direction to multiple directions if "random"
    if direction == "random":
        directions = ["down", "up"]
    else:
        directions = [direction] * scroll_count
    
    for i in range(scroll_count):
        # Choose direction for this scroll
        if direction == "random":
            current_direction = random.choice(directions)
        else:
            current_direction = direction
            
        # Direction multiplier
        dir_multiplier = 1 if current_direction == "down" else -1
        
        # Execute the scroll with easing
        sb.execute_script(f"""
        (function() {{
            const duration = {random.randint(500, 1200)};
            const scrollAmount = {scroll_amount * dir_multiplier};
            const start = window.pageYOffset;
            const end = Math.max(0, Math.min({max_scroll}, start + scrollAmount));
            const startTime = performance.now();
            
            function easeInOutQuad(t) {{ 
                return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
            }}
            
            function scroll() {{
                const elapsed = performance.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = easeInOutQuad(progress);
                const position = start + (end - start) * eased;
                
                window.scrollTo(0, position);
                
                if (progress < 1) {{
                    requestAnimationFrame(scroll);
                }}
            }}
            
            requestAnimationFrame(scroll);
        }})();
        """)
        
        # Wait for scroll to complete with human-like delay
        human_like_delay(0.8, 2.0)
    
    # Sometimes scroll back up a bit as humans often do after scrolling down
    if direction == "down" and random.random() < 0.4:  # 40% chance
        scroll_back_amount = random.randint(int(viewport_height * 0.1), int(viewport_height * 0.3))
        sb.execute_script(f"""
        window.scrollBy(0, {-scroll_back_amount});
        """)
        human_like_delay(0.5, 1.0)

def init_browser(profile_dir=None, headless=False):
    """
    Initialize and return a SeleniumBase browser instance
    
    Args:
        profile_dir (str): Path to browser profile directory (or None)
        headless (bool): Whether to run in headless mode
        
    Returns:
        sb: SeleniumBase instance
    """
    from seleniumbase import Driver
    from seleniumbase.common.exceptions import NoSuchWindowException
    
    # Configure options
    kwargs = {
        "uc": True,
        "headless": headless,
    }
    
    if profile_dir:
        kwargs["user_data_dir"] = profile_dir
    
    # Create a browser directly using Driver instead of SB context manager
    browser = Driver(**kwargs)
    
    try:
        # Set user agent if not using a profile
        if not profile_dir:
            random_user_agent = random.choice(USER_AGENTS)
            browser.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random_user_agent
            })
            print(f"Using user agent: {random_user_agent}")
    except Exception as e:
        print(f"Error setting user agent: {e}")
    
    return browser

def find_best_cookies(profile_dir):
    """
    Find the cookie file with the highest score in the specified profile directory
    
    Args:
        profile_dir (str): Path to the profile directory
        
    Returns:
        str: Path to the best cookie file, or None if no files found
    """
    if not profile_dir or not os.path.exists(profile_dir):
        return None
        
    # Look for cookie files in the cookies directory
    cookie_files = glob.glob(os.path.join("cookies", "high_score_cookies_*.json"))
    
    if not cookie_files:
        return None
    
    # Extract scores from filenames
    best_file = None
    best_score = 0.0
    
    for file_path in cookie_files:
        # Extract score from filename (format: high_score_cookies_X.Y_ZZZZZZZZ.json)
        match = re.search(r"high_score_cookies_(\d+\.\d+)_", os.path.basename(file_path))
        if match:
            try:
                score = float(match.group(1))
                if score > best_score:
                    best_score = score
                    best_file = file_path
            except:
                continue
    
    return best_file

def main():
    """Main function to run the reCAPTCHA score detector"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='reCAPTCHA v3 Score Detector')
    parser.add_argument('--profile', type=str, help='Browser profile name to use/create')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--no-history', action='store_true', help='Skip building browsing history')
    parser.add_argument('--pause', action='store_true', help='Pause before closing browser')
    parser.add_argument('--runs', type=int, default=1, help='Number of runs to perform')
    
    args = parser.parse_args()
    
    scores = []
    for i in range(args.runs):
        if args.runs > 1:
            print(f"\n=== Run {i+1}/{args.runs} ===\n")
            # Wait between runs to avoid detection
            if i > 0:
                wait_time = random.randint(30, 60)
                print(f"Waiting {wait_time} seconds before next run...")
                time.sleep(wait_time)
        
        score = run_score_detector(
            profile_name=args.profile,
            build_history=not args.no_history,
            headless=args.headless
        )
        
        if score is not None:
            scores.append(score)
    
    # Print summary if multiple runs
    if len(scores) > 1:
        avg_score = sum(scores) / len(scores)
        print(f"\n=== Summary ===")
        print(f"Runs completed: {len(scores)}/{args.runs}")
        print(f"Average score: {avg_score:.2f}")
        print(f"Best score: {max(scores):.2f}")
        print(f"Worst score: {min(scores):.2f}")

if __name__ == "__main__":
    main() 