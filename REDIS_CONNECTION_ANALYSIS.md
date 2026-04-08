# Redis Connection Issue Analysis - AWS App Runner

## Problem Summary

AWS App Runner is **unable to connect to Upstash Redis** (`mighty-midge-73983.upstash.io:6379`), causing the application to crash when trying to cache data.

## Error Details

```
TimeoutError: [Errno 110] Connection timed out
redis.exceptions.TimeoutError: Timeout connecting to server
```

**Affected endpoints:**
- `/api/models_and_providers/openrouter/models`
- `/api/models_and_providers/openrouter/providers`

**Stack trace location:**
```
File "/app/backend/api/core/cache.py", line 60, in get
    raw = self._get_client().get(key)
```

## Root Cause

**AWS App Runner's network restrictions** are blocking outbound connections to external Redis servers. By default, App Runner has limited egress connectivity that prevents connections to services outside AWS infrastructure.

## Solutions

### ✅ Solution 1: Make Redis Optional (IMPLEMENTED)

I've updated the error handling to catch **all exceptions** (not just `ConnectionError` and `TimeoutError`) so the app gracefully degrades when Redis is unavailable:

**Files modified:**
- `backend/api/core/cache.py` - Updated `get()`, `set()`, `delete()` methods
- `backend/api/core/redis_client.py` - Updated `set_eval_progress()`, `get_eval_progress()`, `clear_eval_progress()`

**Result:** The app will now log warnings but continue functioning without cache.

### 🔧 Solution 2: Configure VPC Egress for App Runner (RECOMMENDED)

To allow App Runner to connect to Upstash:

1. Create a VPC connector for App Runner
2. Configure egress settings in `apprunner.yaml`:

```yaml
network:
  egress-configuration: VPC
  vpc-connector-arn: arn:aws:apprunner:us-east-2:xxx:vpcconnector/xxx
```

**Pros:** Enables full Redis functionality
**Cons:** More complex infrastructure setup

### 🔄 Solution 3: Use AWS ElastiCache Instead

Replace Upstash with AWS ElastiCache Redis:

1. Create ElastiCache cluster in same VPC as App Runner
2. Update `REDIS_URL` to point to ElastiCache endpoint
3. Configure App Runner with VPC connector

**Pros:** Better AWS integration, lower latency
**Cons:** Higher cost, more infrastructure management

### 🔍 Solution 4: Check Upstash IP Allowlist

Verify Upstash allows connections from AWS App Runner's IP ranges:

1. Go to Upstash dashboard
2. Check IP allowlist settings
3. Add AWS us-east-2 App Runner IP ranges if restricted

## Verification Steps

1. Deploy the updated code
2. Monitor App Runner logs:
```bash
aws logs filter-log-events \
  --log-group-name /aws/apprunner/evalhub-api-runner-github/fe1712786167499f8d695706dd0f5cb4/application \
  --region us-east-2 \
  --start-time $(date -u +%s)000
```

3. Look for warnings instead of crashes:
```
WARNING: Redis GET failed for key xxx: <error>
```

## Current Status

✅ **Immediate fix applied** - App will no longer crash due to Redis connection failures
⚠️ **Cache disabled** - Performance may be impacted for cached endpoints
🔧 **Next step** - Choose long-term solution (VPC egress or ElastiCache)

## Logs Summary

From the past 12 hours, the application repeatedly failed with:
- Multiple `TimeoutError` when trying to connect to Redis
- Errors occurred when fetching OpenRouter models/providers
- Health checks passing but API requests failing
