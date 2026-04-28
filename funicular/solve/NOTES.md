# Funicular Solve Progress Log

## Current Status: Combining React2Shell with H2 Trailers

Based on investigation, we have:
1. ✅ **Working WAF bypass**: HTTP/2 trailers for Next-Action header
2. ✅ **Action execution**: Action runs but returns `recovery-offline`  
3. ✅ **React2Shell payload**: Downloaded CVE-2025-55182 exploit
4. ❌ **RCE not working**: Need to adapt React2Shell payload format

## Key Findings

### Action Signature Analysis
- Action ID: `4082c44f4a6a9cc400f0e6b45ed1c06c10f100aad2`
- infoByte: `0x40` = only arg 0 used → `recoveryAction(formData)`
- Only `["$K1"]` gives `recovery-offline`, all other payloads give error digests

### Payload Testing Results
- `["$K1"]` → recovery-offline (normal action execution)
- React2Shell multipart → ERROR digest:2699797941 (different from baseline)
- Other FormData attempts → ERROR digest:4263110034 (standard FormData error)

### Working Transport
```python
# HTTP/2 trailers bypass WAF successfully
header_block = encode_headers_without_next_action()
send_headers_frame(NO_END_STREAM)
send_data_frame(NO_END_STREAM) 
send_trailer_headers_frame(next_action=ACTION_ID, END_STREAM)
```

## Next Steps

The issue seems to be that React2Shell payload needs adaptation:

1. **Original React2Shell uses**: multipart form with prototype pollution
2. **Funicular action expects**: FormData object as `["$K1"]` reference
3. **Need to combine**: RCE payload that works through FormData reference

Two possible approaches:
A) Modify React2Shell to work with FormData reference format
B) Find the correct FormData content that triggers RCE via prototype pollution

## Current Hypothesis

The action is legitimate recovery function but vulnerable to prototype pollution when FormData contains malicious `__proto__` chains. Need to craft FormData that:
1. Passes action signature validation (appears as valid FormData)
2. Contains prototype pollution payload
3. Triggers RCE through Node.js process execution

Will continue with hybrid approach combining our H2 trailer transport with adapted React2Shell RCE payload.