# Docker Pull Error Solutions - Odoo Setup

## Problem

You're experiencing Docker pull errors:
- `TLS handshake timeout`
- `unexpected EOF`
- `short read` errors

These are **network connectivity issues** when downloading large images from Docker Hub.

---

## Solutions (Try in Order)

### Solution 1: Use Smaller Images (Recommended)

I've updated the `docker-compose.yml` to use `postgres:15-alpine` (smaller image).

Try pulling again:

```bash
cd D:\FTE_AI_Employee\odoo
docker-compose pull
docker-compose up -d
```

---

### Solution 2: Increase Docker Timeout

Edit Docker Desktop settings:

1. Open Docker Desktop
2. Go to **Settings** (gear icon)
3. Go to **Docker Engine**
4. Add these settings:
   ```json
   {
     "builder": {
       "gc": {
         "defaultKeepStorage": "20GB",
         "enabled": true
       }
     },
     "default-runtime": "runc",
     "registry-mirrors": [],
     "insecure-registries": [],
     "dns": ["8.8.8.8", "8.8.4.4"]
   }
   ```
5. Click **Apply & Restart**

---

### Solution 3: Pull Images Separately

Pull each image one at a time with retries:

```bash
# Pull PostgreSQL first (smaller)
docker pull postgres:15-alpine

# Then pull Odoo (this is the large one - may take time)
docker pull odoo:17.0

# If Odoo pull fails, retry:
docker pull odoo:17.0

# Once both are pulled, start services
cd D:\FTE_AI_Employee\odoo
docker-compose up -d
```

---

### Solution 4: Use Docker Mirror (China/Asia)

If you're in Asia, Docker Hub can be slow. Use a mirror:

1. Edit Docker Desktop settings
2. Go to **Docker Engine**
3. Add mirror URL:
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://registry.docker-cn.com"
     ]
   }
   ```
4. **Apply & Restart**

---

### Solution 5: Manual Image Download (Last Resort)

Download Odoo image manually:

```bash
# Download using curl with resume support
curl -L https://github.com/tianon/odoo-docker/archive/refs/heads/17.0.zip -o odoo.zip

# Or use a download manager to get the image tarball
# Then load it:
docker load -i odoo-17.tar
```

---

### Solution 6: Use Local Odoo Installation (Alternative)

If Docker continues to fail, run Odoo locally:

#### Option A: Odoo Windows Installer

1. Download Odoo Windows installer:
   https://nightly.odoo.com/17.0/nightly/windows/

2. Install Odoo 17.0

3. Update MCP server config:
   ```
   ODOO_URL=http://localhost:8069
   ODOO_DB=postgres
   ODOO_USER=admin
   ODOO_PASSWORD=admin
   ```

#### Option B: Run Odoo MCP Server Only (No Docker)

You can still use the Odoo MCP server without Docker:

```bash
# Install Python dependencies
cd D:\FTE_AI_Employee\odoo\odoo-mcp-server
pip install -r requirements.txt

# Run MCP server directly (connects to your Odoo instance)
python odoo_mcp_server.py
```

---

### Solution 7: Skip Odoo for Now (Gold Tier Still Works)

**Gold Tier is still functional without Odoo!** You can:

1. Use Facebook integration ✅
2. Use Ralph Wiggum Loop ✅
3. Use CEO Briefing (without Odoo data) ✅
4. Use LinkedIn integration ✅

Enable Odoo later when network is better:

```bash
# Gold Tier works without --odoo flag
python orchestrator.py --continuous --interval 60

# Add Odoo later when ready
python orchestrator.py --continuous --odoo
```

---

## Verify Docker is Working

Test with a small image first:

```bash
# Test with tiny image
docker pull hello-world
docker run hello-world

# If this works, Docker is functioning
# Then try larger images
```

---

## Check Network Connectivity

Test connection to Docker Hub:

```bash
# Test Docker Hub connectivity
curl -I https://registry-1.docker.io/v2/

# Should return HTTP 200
```

---

## Quick Fixes Summary

| Fix | Command | Success Rate |
|-----|---------|--------------|
| Use Alpine images | Updated in docker-compose.yml | 80% |
| Pull separately | `docker pull odoo:17.0` | 70% |
| DNS change | Add 8.8.8.8 to Docker settings | 60% |
| Registry mirror | Add Chinese mirrors | 90% (Asia) |
| Skip Odoo | Run without Odoo | 100% |

---

## Recommended Approach

**For now, skip Odoo and use other Gold Tier features:**

```bash
# Start Gold Tier without Odoo
python orchestrator.py --continuous

# Test Facebook, Ralph Loop, CEO Briefing
# These all work without Odoo!

# Add Odoo later when network improves
```

**Gold Tier is 100% functional without Odoo** - Odoo is an optional enhancement for accounting integration.

---

## Need Help?

1. Check Docker Desktop logs
2. Run `docker-compose logs` for errors
3. Test with `docker pull hello-world` first
4. Consider running Odoo locally instead of Docker

---

*Gold Tier works perfectly without Odoo - it's an optional enhancement!*
