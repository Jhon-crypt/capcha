from seleniumbase import SB
import uuid
import os
import random
import time
import json
from datetime import datetime, timedelta
import re

# Create directory for screenshots if it doesn't exist
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# Create directory for cookies if it doesn't exist
if not os.path.exists("cookies"):
    os.makedirs("cookies")

def human_like_delay(min_seconds=0.5, max_seconds=2.5):
    """Simulates human-like delay between actions"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def natural_mouse_movement(sb, target_element=None, num_points=10):
    """
    Simulates natural mouse movement with acceleration and deceleration
    If target_element is provided, moves to that element, otherwise moves randomly
    """
    # Get viewport size
    viewport_width = sb.execute_script("return window.innerWidth;")
    viewport_height = sb.execute_script("return window.innerHeight;")
    
    # Starting position (random or current)
    start_x = random.randint(0, viewport_width)
    start_y = random.randint(0, viewport_height)
    
    # Target position
    if target_element:
        try:
            # Handle both string selectors and WebElement objects
            if isinstance(target_element, str):
                # It's a selector string
                element = sb.find_element(target_element)
                element_rect = sb.execute_script(
                    "return arguments[0].getBoundingClientRect();", 
                    element
                )
            else:
                # It's already a WebElement
                element_rect = sb.execute_script(
                    "return arguments[0].getBoundingClientRect();", 
                    target_element
                )
            
            end_x = element_rect['left'] + element_rect['width'] / 2
            end_y = element_rect['top'] + element_rect['height'] / 2
        except Exception as e:
            print(f"Error getting element position: {e}")
            # Fall back to random movement
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
        random_offset_x = random.randint(-20, 20) * randomness
        random_offset_y = random.randint(-20, 20) * randomness
        
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
            
        # Move mouse - using a safer approach that checks if element exists
        try:
            sb.execute_script("""
            var element = document.elementFromPoint(arguments[0], arguments[1]);
            if (element) {
                var event = new MouseEvent('mousemove', {
                    clientX: arguments[0],
                    clientY: arguments[1],
                    bubbles: true
                });
                element.dispatchEvent(event);
            }
            """, x, y)
        except Exception as e:
            print(f"Mouse movement error (non-critical): {e}")
        
        time.sleep(delay)
    
    # Optionally click if target_element was provided
    if target_element and random.random() > 0.3:
        try:
            if isinstance(target_element, str):
                sb.click(target_element)
            else:
                # For WebElement objects, use JavaScript click for reliability
                sb.execute_script("arguments[0].click();", target_element)
        except Exception as e:
            print(f"Error clicking element: {e}")

def random_scroll(sb, min_pixels=100, max_pixels=500):
    """Performs random scrolling to simulate human behavior"""
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

def simulate_reading(sb, min_time=3, max_time=8):
    """Simulates a user reading the page content"""
    # Find all text elements
    text_elements = sb.find_elements("xpath", "//p | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //span | //div")
    
    if not text_elements:
        return
    
    # Filter to visible elements with content
    visible_text_elements = []
    for elem in text_elements:
        try:
            if sb.is_element_visible(elem) and elem.text.strip():
                visible_text_elements.append(elem)
        except:
            continue
    
    if not visible_text_elements:
        return
    
    # Select a few random elements to "read"
    num_to_read = min(random.randint(2, 5), len(visible_text_elements))
    elements_to_read = random.sample(visible_text_elements, num_to_read)
    
    for elem in elements_to_read:
        try:
            # Scroll element into view if needed
            sb.scroll_to(elem)
            human_like_delay(0.5, 1.0)
            
            # Move mouse to the element to simulate reading
            natural_mouse_movement(sb, elem)
            
            # Calculate reading time based on text length
            text_length = len(elem.text)
            reading_time = min(max_time, max(min_time, text_length / 100))
            time.sleep(reading_time)
        except:
            continue

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

def load_cookies(sb, filename):
    """Loads cookies from file into browser"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Handle both old and new cookie format
            if isinstance(data, dict) and "cookies" in data:
                # New format with metadata
                cookies = data["cookies"]
                metadata = data.get("metadata", {})
                print(f"Loading cookies saved from {metadata.get('saved_from_domain', 'unknown domain')}")
            else:
                # Old format (just a list of cookies)
                cookies = data
            
            # Add cookies to browser
            current_url = sb.get_current_url()
            current_domain = current_url.split('//')[1].split('/')[0]
            
            loaded_count = 0
            for cookie in cookies:
                try:
                    # Handle expiry conversion
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    
                    # Skip cookies with domain mismatch
                    cookie_domain = cookie.get('domain', '')
                    if cookie_domain and not current_domain.endswith(cookie_domain.lstrip('.')) and not cookie_domain.lstrip('.').endswith(current_domain):
                        continue
                    
                    # Only add cookies for the current domain
                    if 'domain' in cookie:
                        # Make sure domain is compatible with current site
                        if cookie['domain'].startswith('.'):
                            # Some domains start with a dot
                            if not current_domain.endswith(cookie['domain'][1:]):
                                continue
                        elif not current_domain.endswith(cookie['domain']):
                            continue
                    
                    # Add the cookie
                    try:
                        sb.driver.add_cookie(cookie)
                        loaded_count += 1
                    except Exception as e:
                        # Skip problematic cookies
                        continue
                except:
                    continue
            
            print(f"Loaded {loaded_count} compatible cookies")
            return loaded_count > 0
        except Exception as e:
            print(f"Error loading cookies: {e}")
    return False

def modify_browser_fingerprint(sb):
    """Modifies browser fingerprint to appear more human-like"""
    # Set a common user agent
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ]
    
    # Use the user agent that matches the user's OS (Mac)
    sb.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": user_agents[0],
        "platform": "macOS"
    })
    
    # Add common browser plugins
    sb.execute_script("""
    // Simulate common plugins
    Object.defineProperty(navigator, 'plugins', {
        get: function() {
            return [
                {
                    name: 'Chrome PDF Plugin',
                    filename: 'internal-pdf-viewer',
                    description: 'Portable Document Format'
                },
                {
                    name: 'Chrome PDF Viewer',
                    filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                    description: 'Portable Document Format'
                },
                {
                    name: 'Native Client',
                    filename: 'internal-nacl-plugin',
                    description: ''
                }
            ];
        }
    });
    """)
    
    # Set common screen properties
    sb.execute_script("""
    // Override screen properties
    Object.defineProperty(window, 'screen', {
        get: function() {
            return {
                availHeight: 1050,
                availLeft: 0,
                availTop: 25,
                availWidth: 1680,
                colorDepth: 24,
                height: 1080,
                pixelDepth: 24,
                width: 1920
            };
        }
    });
    """)
    
    # Add WebGL fingerprint randomization
    sb.execute_script("""
    // Override WebGL fingerprint
    const getParameterProxyHandler = {
        apply: function(target, ctx, args) {
            const param = args[0];
            
            // UNMASKED_VENDOR_WEBGL or UNMASKED_RENDERER_WEBGL
            if (param === 37445) {
                return 'Intel Inc.';
            }
            if (param === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            
            return Reflect.apply(target, ctx, args);
        }
    };
    
    // Apply the proxy to WebGL getParameter
    if (WebGLRenderingContext.prototype.getParameter) {
        WebGLRenderingContext.prototype.getParameter = new Proxy(
            WebGLRenderingContext.prototype.getParameter, 
            getParameterProxyHandler
        );
    }
    """)
    
    # Add canvas fingerprint randomization
    sb.execute_script("""
    // Override Canvas fingerprint
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type) {
        // Call the original function
        const result = originalToDataURL.apply(this, arguments);
        
        // Only modify if it's being used for fingerprinting (small canvas)
        if (this.width <= 16 && this.height <= 16) {
            // Add slight noise to the canvas data
            return result.replace(/[A-Za-z0-9+/=]{10}/, function(m) {
                const chars = m.split('');
                // Change 1-2 characters slightly
                const idx = Math.floor(Math.random() * chars.length);
                chars[idx] = String.fromCharCode(chars[idx].charCodeAt(0) + 1);
                return chars.join('');
            });
        }
        
        return result;
    };
    """)
    
    # Disable automation flags
    sb.execute_script("""
    // Remove automation flags
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // Override navigator.webdriver flag
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false
    });
    
    // Override chrome driver presence
    const originalQuery = document.querySelector;
    document.querySelector = function() {
        if (arguments[0] === '[chromedriver]' || 
            arguments[0] === '[selenium]' || 
            arguments[0] === '[webdriver]') {
            return null;
        }
        return originalQuery.apply(this, arguments);
    };
    """)
    
    # Add language and platform info
    sb.execute_script("""
    // Set navigator properties
    Object.defineProperty(navigator, 'language', {
        get: function() {
            return 'en-US';
        }
    });
    
    Object.defineProperty(navigator, 'languages', {
        get: function() {
            return ['en-US', 'en'];
        }
    });
    
    Object.defineProperty(navigator, 'platform', {
        get: function() {
            return 'MacIntel';
        }
    });
    """)
    
    # Add hardware concurrency and device memory
    sb.execute_script("""
    // Set hardware properties
    Object.defineProperty(navigator, 'hardwareConcurrency', {
        get: function() {
            return 8;
        }
    });
    
    if ('deviceMemory' in navigator) {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: function() {
                return 8;
            }
        });
    }
    
    // Add connection property
    if ('connection' in navigator) {
        Object.defineProperty(navigator.connection, 'rtt', {
            get: function() {
                return 50;
            }
        });
        
        Object.defineProperty(navigator.connection, 'downlink', {
            get: function() {
                return 10;
            }
        });
        
        Object.defineProperty(navigator.connection, 'effectiveType', {
            get: function() {
                return '4g';
            }
        });
    }
    """)
    
    # Add permissions API mocking
    sb.execute_script("""
    // Mock permissions API
    if ('permissions' in navigator) {
        navigator.permissions.query = function(parameters) {
            return Promise.resolve({
                state: 'granted',
                onchange: null
            });
        };
    }
    """)
    
    # Add more advanced anti-detection techniques
    sb.execute_script("""
    // Override toString methods to hide proxy behavior
    const originalToString = Function.prototype.toString;
    Function.prototype.toString = function() {
        if (this === Function.prototype.toString) return originalToString.call(this);
        if (this === navigator.permissions.query) {
            return "function query() { [native code] }";
        }
        return originalToString.call(this);
    };
    
    // Override getTimezoneOffset to return a consistent value
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function() {
        return -420; // Consistent timezone (UTC-7)
    };
    
    // Override performance API
    if (window.performance && window.performance.now) {
        const originalNow = window.performance.now;
        let startTime = Date.now();
        window.performance.now = function() {
            return Date.now() - startTime;
        };
    }
    
    // Override Notification API
    if ('Notification' in window) {
        Object.defineProperty(Notification, 'permission', {
            get: function() {
                return 'granted';
            }
        });
    }
    
    // Override media devices
    if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
        navigator.mediaDevices.enumerateDevices = function() {
            return Promise.resolve([
                {
                    deviceId: 'default',
                    kind: 'audioinput',
                    label: 'Default Audio Device',
                    groupId: 'default'
                },
                {
                    deviceId: 'default',
                    kind: 'audiooutput',
                    label: 'Default Audio Output',
                    groupId: 'default'
                },
                {
                    deviceId: 'default',
                    kind: 'videoinput',
                    label: 'FaceTime HD Camera',
                    groupId: 'default'
                }
            ]);
        };
    }
    """)

def get_recaptcha_score(use_proxy=False, proxy_server=None):
    """Main function to get reCAPTCHA score with human-like behavior"""
    # Generate a unique ID for this run
    run_id = str(uuid.uuid4())[:8]
    cookies_file = f"cookies/browser_cookies.json"
    
    # Ensure screenshots directory exists
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    # Configure SeleniumBase with more human-like settings
    with SB(uc=True, headless=False, incognito=False, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36") as sb:
        try:
            # Set window size to a common desktop resolution with slight randomness
            width = random.randint(1200, 1400)
            height = random.randint(750, 850)
            sb.set_window_size(width, height)
            
            # Modify browser fingerprint
            modify_browser_fingerprint(sb)
            
            # Visit multiple sites to establish browsing history
            sites_to_visit = [
                "https://www.google.com",
                "https://www.youtube.com",
                "https://www.wikipedia.org",
                "https://www.reddit.com",
                "https://www.nytimes.com"
            ]
            
            # Visit 2-3 sites randomly
            sites_to_visit = random.sample(sites_to_visit, random.randint(2, 3))
            
            for site in sites_to_visit:
                print(f"Visiting {site} to build browsing history...")
                sb.open(site)
                sb.wait_for_ready_state_complete()
                human_like_delay(2, 4)
                
                # Scroll and interact naturally
                for _ in range(random.randint(2, 4)):
                    random_scroll(sb)
                    human_like_delay(1, 2)
                
                # Try to click on something if it's not the last site
                if site != sites_to_visit[-1]:
                    try:
                        links = sb.find_elements("a")
                        visible_links = []
                        for link in links[:20]:
                            try:
                                if sb.is_element_visible(link):
                                    visible_links.append(link)
                            except:
                                continue
                        
                        if visible_links:
                            link = random.choice(visible_links)
                            # Use JavaScript to click
                            sb.execute_script("arguments[0].click();", link)
                            human_like_delay(3, 5)
                            
                            # Interact with the new page
                            random_scroll(sb)
                            human_like_delay(2, 4)
                            
                            # Go back
                            sb.go_back()
                            sb.wait_for_ready_state_complete()
                    except Exception as e:
                        print(f"Error clicking link: {e}")
            
            # Save cookies
            save_cookies(sb, cookies_file)
            
            # Now directly visit the target site
            target_url = 'https://antcpt.com/score_detector/'
            print(f'Opening target site: {target_url}')
            
            # Open the page normally
            sb.open(target_url)
            
            # Wait for page to fully load
            sb.wait_for_ready_state_complete()
            print("Page loaded, now behaving like a human...")
            
            # Simulate human-like behavior
            human_like_delay(3, 5)
            
            # Simple mouse movements first (safer)
            print("Moving mouse naturally...")
            for _ in range(3):
                x = random.randint(100, 500)
                y = random.randint(100, 400)
                sb.execute_script(f"window.scrollTo(0, {y - 100});")
                human_like_delay(0.5, 1)
            
            # Simulate reading the page content
            print("Simulating reading...")
            simulate_reading(sb, 8, 15)  # Longer reading time
            
            # Scroll down and up naturally
            print("Scrolling naturally...")
            for _ in range(3):
                random_scroll(sb)
                human_like_delay(1, 2)
            
            # Interact with the page using direct JavaScript
            print("Interacting with page elements...")
            sb.execute_script("""
            // Find all links and buttons
            var elements = document.querySelectorAll('a, button');
            
            // Function to simulate mouse movement and click
            function simulateInteraction(element) {
                if (element && element.getBoundingClientRect) {
                    var rect = element.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        // Only interact with visible elements
                        var x = rect.left + rect.width / 2;
                        var y = rect.top + rect.height / 2;
                        
                        // Create and dispatch mousemove event
                        var moveEvent = new MouseEvent('mousemove', {
                            clientX: x,
                            clientY: y,
                            bubbles: true
                        });
                        element.dispatchEvent(moveEvent);
                        
                        // Don't click on refresh or clear buttons
                        var text = element.textContent.toLowerCase();
                        if (text.indexOf('refresh') === -1 && text.indexOf('clear') === -1) {
                            // Create and dispatch mousedown event
                            var downEvent = new MouseEvent('mousedown', {
                                clientX: x,
                                clientY: y,
                                bubbles: true
                            });
                            element.dispatchEvent(downEvent);
                            
                            // Create and dispatch mouseup event
                            var upEvent = new MouseEvent('mouseup', {
                                clientX: x,
                                clientY: y,
                                bubbles: true
                            });
                            element.dispatchEvent(upEvent);
                        }
                    }
                }
            }
            
            // Interact with 2-3 random elements
            if (elements.length > 0) {
                for (var i = 0; i < Math.min(3, elements.length); i++) {
                    var randomIndex = Math.floor(Math.random() * elements.length);
                    simulateInteraction(elements[randomIndex]);
                }
            }
            """)
            
            # Final wait to ensure score is calculated - much longer wait
            wait_time = random.randint(20, 30)
            print(f"Waiting final {wait_time} seconds for score calculation...")
            sb.sleep(wait_time)
            
            # Take screenshot
            screenshot_path = f"screenshots/score_detector_{run_id}.png"
            try:
                print(f"Taking screenshot and saving to {screenshot_path}...")
                sb.save_screenshot(screenshot_path)
                print(f"Screenshot saved successfully to {screenshot_path}")
            except Exception as e:
                print(f"Error saving screenshot: {e}")
                # Try alternative method
                try:
                    sb.driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved using alternative method")
                except Exception as e2:
                    print(f"Failed to save screenshot using alternative method: {e2}")
            
            # Try to extract the score
            try:
                # Try different possible selectors for the score
                score_selectors = [
                    "//div[contains(text(), 'Your score is:')]",
                    "//div[contains(@class, 'score')]",
                    "//div[contains(text(), 'score is:')]",
                    "//div[contains(text(), 'score')]"
                ]
                
                score_element = None
                for selector in score_selectors:
                    try:
                        if sb.is_element_present(selector, timeout=3):
                            score_element = sb.find_element(selector)
                            break
                    except:
                        continue
                
                if score_element:
                    score_text = score_element.text
                    print(f"Found score: {score_text}")
                    
                    # Save successful cookies
                    if "0.7" in score_text or "0.8" in score_text or "0.9" in score_text or "1.0" in score_text:
                        print("High score achieved! Saving cookies for future use.")
                        save_cookies(sb, f"cookies/high_score_cookies_{run_id}.json")
                else:
                    print("Could not find score element, checking page source")
                    # Try to extract score from page source as a fallback
                    page_source = sb.get_page_source()
                    score_match = re.search(r'Your score is:\s*(\d+\.\d+)', page_source)
                    if score_match:
                        score = score_match.group(1)
                        print(f"Found score in page source: {score}")
                        
                        # Save successful cookies if high score
                        if float(score) >= 0.7:
                            print(f"High score achieved ({score})! Saving cookies for future use.")
                            save_cookies(sb, f"cookies/high_score_cookies_{score}_{run_id}.json")
            except Exception as e:
                print(f"Could not find score element: {e}")
        
        except Exception as e:
            print(f"Critical error in main execution: {e}")
            # Take screenshot even if there was an error
            try:
                error_screenshot = f"screenshots/error_{run_id}.png"
                sb.save_screenshot(error_screenshot)
                print(f"Error screenshot saved to {error_screenshot}")
            except:
                pass

if __name__ == "__main__":
    get_recaptcha_score()