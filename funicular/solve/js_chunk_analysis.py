#!/usr/bin/env python3
"""
Analyze JavaScript chunks from the funicular app for hidden flags
Based on chunks seen in RSC response
"""
import requests
import re
import base64
import json

HOST = "funicular-gm2cxozn.alfactf.ru"
BASE_URL = f"https://{HOST}"

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

# JS chunks we saw in RSC response
CHUNKS = [
    "42879de7b8087bc9.js",  # 28KB layout/boundary components
    "47901a36162cd061.js",  # 2.8KB dispatch panel
    "a4403f826d0efc9f.js",  # 300KB React + Next runtime
    "ee23c10f124185e0.js",  # 90KB React DOM internals
    "fd5f064b2a3f9309.js",  # 13KB Next.js client router
    "turbopack-4dfba6ec099a9d31.js",  # 9.8KB Turbopack runtime
    "a6dad97d9634a72d.js",  # 112KB polyfills
]

def download_and_analyze_chunk(chunk_name):
    """Download and analyze a JS chunk for flags"""
    url = f"{BASE_URL}/_next/static/chunks/{chunk_name}"

    print(f"\n[+] Analyzing {chunk_name}...")
    print(f"    URL: {url}")

    try:
        session = requests.Session()
        session.verify = False
        resp = session.get(url, timeout=10)

        if resp.status_code != 200:
            print(f"    Status: {resp.status_code} - Failed to download")
            return False

        content = resp.text
        print(f"    Size: {len(content)} bytes")

        # Look for direct flags
        direct_flags = re.findall(r'alfa\{[^}]+\}', content, re.IGNORECASE)
        if direct_flags:
            print(f"    [!] DIRECT FLAGS: {direct_flags}")
            return True

        # Look for base64 encoded flags
        b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', content)
        flag_found = False
        for pattern in b64_patterns[:20]:  # Check first 20 base64-like strings
            try:
                decoded = base64.b64decode(pattern).decode('utf-8', errors='ignore')
                if 'alfa{' in decoded.lower():
                    print(f"    [!] BASE64 FLAG: {pattern} -> {decoded}")
                    flag_found = True
            except:
                pass

        # Look for hex encoded flags
        hex_patterns = re.findall(r'[0-9a-fA-F]{40,}', content)
        for pattern in hex_patterns[:20]:
            try:
                decoded = bytes.fromhex(pattern).decode('utf-8', errors='ignore')
                if 'alfa{' in decoded.lower():
                    print(f"    [!] HEX FLAG: {pattern} -> {decoded}")
                    flag_found = True
            except:
                pass

        # Look for suspicious strings
        suspicious = [
            'flag', 'secret', 'password', 'key', 'token',
            'курагу', 'друзьям', 'кубани', 'recovery', 'restore'
        ]

        for word in suspicious:
            if word.lower() in content.lower():
                # Get context around the word
                for match in re.finditer(re.escape(word), content, re.IGNORECASE):
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]
                    print(f"    Found '{word}': ...{context}...")

        # Look for React action definitions (recovery-related)
        action_patterns = [
            r'recoveryAction\s*[=:]\s*["\']([^"\']+)["\']',
            r'recovery["\']?\s*[:\s]*["\']?([^"\',:}]+)',
            r'restore["\']?\s*[:\s]*["\']?([^"\',:}]+)',
        ]

        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                print(f"    Action pattern: {match}")
                if 'alfa{' in match.lower():
                    print(f"    [!] ACTION FLAG: {match}")
                    flag_found = True

        return flag_found

    except Exception as e:
        print(f"    Error: {e}")
        return False

def analyze_main_page():
    """Analyze the main page HTML for any client-side flags"""
    print(f"\n[+] Analyzing main page HTML...")

    try:
        session = requests.Session()
        session.verify = False
        resp = session.get(BASE_URL, timeout=10)

        if resp.status_code != 200:
            print(f"    Status: {resp.status_code} - Failed to download")
            return False

        content = resp.text

        # Look for flags in HTML
        direct_flags = re.findall(r'alfa\{[^}]+\}', content, re.IGNORECASE)
        if direct_flags:
            print(f"    [!] DIRECT FLAGS IN HTML: {direct_flags}")
            return True

        # Look for base64 in script tags or data attributes
        script_content = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        for script in script_content:
            b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', script)
            for pattern in b64_patterns[:10]:
                try:
                    decoded = base64.b64decode(pattern).decode('utf-8', errors='ignore')
                    if 'alfa{' in decoded.lower():
                        print(f"    [!] BASE64 FLAG IN SCRIPT: {pattern} -> {decoded}")
                        return True
                except:
                    pass

        # Look for data attributes that might contain flags
        data_attrs = re.findall(r'data-[^=]+=["\']([^"\']+)["\']', content)
        for attr in data_attrs:
            if 'alfa{' in attr.lower():
                print(f"    [!] FLAG IN DATA ATTR: {attr}")
                return True

        # Look for JSON data that might contain flags
        json_patterns = re.findall(r'\{[^{}]{20,}\}', content)
        for json_str in json_patterns[:10]:
            try:
                parsed = json.loads(json_str)
                json_text = json.dumps(parsed)
                if 'alfa{' in json_text.lower():
                    print(f"    [!] FLAG IN JSON: {json_text}")
                    return True
            except:
                pass

        print("    No flags found in main page HTML")
        return False

    except Exception as e:
        print(f"    Error: {e}")
        return False

def main():
    print("=" * 80)
    print("JavaScript Chunk and Client-Side Analysis")
    print("=" * 80)

    flag_found = False

    # Analyze main page first
    if analyze_main_page():
        flag_found = True

    # Analyze each JS chunk
    for chunk in CHUNKS:
        if download_and_analyze_chunk(chunk):
            flag_found = True

    if not flag_found:
        print("\n" + "=" * 80)
        print("No flags found in client-side code.")
        print("The flag may be:")
        print("1. Server-side only and requires successful recovery")
        print("2. Hidden in a different static resource (CSS, images)")
        print("3. Generated dynamically after proper authorization")
        print("4. In a chunk/resource we haven't identified")

        print("\nNext steps:")
        print("- Try CSS files analysis")
        print("- Look at other static resources")
        print("- Check if flag is in buildId or other metadata")
    else:
        print(f"\n[!] CLIENT-SIDE ANALYSIS COMPLETE - FLAG FOUND!")

if __name__ == "__main__":
    main()