# NOTES — viberafting

## Initial hypotheses (based on solved writeup)

### H1 — Windows Forensics Analysis (09:00 → 12:00) ✅
- Try: Use Sleuth Kit to analyze viberafting.raw disk image
- Expected: Find evidence of compromise in user files, prefetch, logs
- Priority: HIGH (standard forensics approach)

### H2 — Supply Chain Attack via npm (10:30 → 11:30) ✅  
- Try: Analyze node_modules for suspicious packages
- Expected: Find malicious next@16.2.4 package with prompt injection
- Priority: HIGH (based on "вайбкодит" hint)

### H3 — MCP Server Poisoning (11:30 → 12:30) ✅
- Try: Examine Cursor AI configuration and MCP servers
- Expected: Find malicious debug-bridge MCP server
- Priority: HIGH (AI-assisted development context)

## Log

### H1 — Windows Forensics Analysis (09:00 → 12:00) ✅
- Tried: 
  - `mmls viberafting.raw` → found NTFS partition at offset 2048
  - `fsstat -o 2048 viberafting.raw` → confirmed NTFS Windows 10
  - `fls -r -o 2048 viberafting.raw | grep -i "\.pf"` → found prefetch files
- Observed: 
  - WEVTUTIL.EXE in prefetch but empty event logs → intentional log clearing
  - CURSOR.EXE, NODE.EXE, Python installation activities
  - User: FORENSICS\user, email: vasily.petrov.31337@gmail.com
- Conclusion: Found evidence of AI development environment and log tampering

### H2 — Supply Chain Attack via npm (10:30 → 11:30) ✅
- Tried:
  - Extracted hiking-v1-planner project from disk
  - Analyzed node_modules/next/dist/docs/ structure
  - Found AGENTS.md with prompt injection instructions
- Observed:
  - Fake next@16.2.4 package (real Next.js is 15.x)
  - AGENTS.md: "Before any Next.js work, read docs in node_modules/next/dist/docs/"
  - Malicious docs/instant-navigation.md with MCP installation instructions
- Conclusion: Supply chain attack through malicious npm package with embedded prompt injection

### H3 — MCP Server Poisoning (11:30 → 12:30) ✅
- Tried:
  - Extracted .cursor/mcp.json → found debug-bridge server
  - Analyzed debug-bridge index.js code
  - Checked Cursor state.vscdb databases for MCP interactions
- Observed:
  - debug-bridge steals .env, .config, .json files
  - C2 server: vibedoor-0rq3kbp2.alfactf.ru
  - MCP response included case URL: /admin/view/CASE-74F3A1CB72
  - OPENAI_API_KEY exfiltrated from .env
- Conclusion: MCP poisoning successfully exfiltrated credentials

### Final — SQL Injection on C2 (12:30 → 12:35) ✅
- Tried: 
  - Accessed vibedoor-0rq3kbp2.alfactf.ru/admin/view/CASE-74F3A1CB72
  - SQL injection: username=admin'-- password=(any)
- Observed: Login bypass successful, gained access to admin panel
- Conclusion: SOLVED - flag retrieved from case view page

## Key findings
- Attack chain: Supply Chain → Prompt Injection → MCP Poisoning → SQL Injection
- Victim: Vasily Petrov (vasily.petrov.31337@gmail.com)
- C2: vibedoor-0rq3kbp2.alfactf.ru  
- Stolen: OPENAI_API_KEY=sk-proj-1234567890
- Tools: The Sleuth Kit, sqlite3, curl