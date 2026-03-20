# Odoo Community Edition Setup Guide - Gold Tier

This guide walks you through setting up Odoo Community Edition for your AI Employee system.

## ⚠️ Troubleshooting Docker Pull Issues

If you're experiencing Docker pull errors (TLS handshake timeout, unexpected EOF, etc.):

1. **Run the helper script** (recommended):
   ```bash
   cd D:\FTE_AI_Employee\odoo
   pull-docker-images.bat
   ```

2. **See detailed troubleshooting**: [`DOCKER_TROUBLEBLSHOOTING.md`](DOCKER_TROUBLEBLSHOOTING.md)

3. **Skip Odoo for now** - Gold Tier works without Odoo!
   ```bash
   python orchestrator.py --continuous
   ```

---

Odoo is a comprehensive ERP/CRM system that provides:
- **Accounting**: Invoicing, payments, financial reporting
- **CRM**: Customer relationship management
- **Inventory**: Stock management
- **Sales**: Quotations, orders
- **Projects**: Task management
- **And more**: 30+ business apps available

## Prerequisites

- Docker Desktop for Windows (or Docker Engine + Docker Compose)
- At least 4GB RAM available for Odoo
- 10GB free disk space
- Python 3.11+ (for local MCP server)

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Navigate to the Odoo directory**:
```bash
cd D:\FTE_AI_Employee\odoo
```

2. **Start Odoo with Docker Compose**:
```bash
docker-compose up -d
```

3. **Wait for Odoo to initialize** (2-3 minutes):
```bash
docker-compose logs -f odoo
```

4. **Access Odoo web interface**:
   - URL: http://localhost:8069
   - Master password: `odoo_secure_password_123`
   - Create your first database

5. **Create database**:
   - Go to http://localhost:8069/web/database/manager
   - Click "Create Database"
   - Master password: `odoo_secure_password_123`
   - Database name: `postgres`
   - Email: your email
   - Password: `admin` (or your choice)
   - Select "Community" edition

6. **Install Accounting module**:
   - Log in to Odoo
   - Go to Apps
   - Search for "Accounting"
   - Install "Invoicing" (free community version)

### Option 2: Local MCP Server

If you prefer to run the MCP server locally (not in Docker):

1. **Install Python dependencies**:
```bash
cd D:\FTE_AI_Employee\odoo\odoo-mcp-server
pip install -r requirements.txt
```

2. **Set environment variables**:
```bash
set ODOO_URL=http://localhost:8069
set ODOO_DB=postgres
set ODOO_USER=admin
set ODOO_PASSWORD=admin
```

3. **Run the MCP server**:
```bash
python odoo_mcp_server.py
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ODOO_URL` | http://localhost:8069 | Odoo server URL |
| `ODOO_DB` | postgres | Database name |
| `ODOO_USER` | admin | Odoo username |
| `ODOO_PASSWORD` | admin | Odoo password |

### Docker Compose Services

- **db**: PostgreSQL database (port 5432 internal)
- **odoo**: Odoo Community Edition (port 8069)
- **odoo-mcp**: Odoo MCP Server (port 8810)

## Testing the Integration

### 1. Test Odoo Connection

```bash
# Using the MCP client
python ..\.qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8810 ^
  -t odoo_connect ^
  -p '{}'
```

### 2. Get Account Summary

```bash
python ..\.qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8810 ^
  -t odoo_get_account_summary ^
  -p '{}'
```

### 3. Create a Test Partner

```bash
python ..\.qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8810 ^
  -t odoo_create_partner ^
  -p '{"name": "Test Customer", "email": "test@example.com"}'
```

### 4. Create a Test Invoice

```bash
python ..\.qwen\skills\browsing-with-playwright\scripts\mcp-client.py call ^
  -u http://localhost:8810 ^
  -t odoo_create_invoice ^
  -p '{"partner_id": 1, "invoice_type": "out_invoice"}'
```

## Integration with AI Employee

### Using Odoo MCP in Your Skills

Create a new skill file `.qwen/skills/odoo-operations.md`:

```markdown
# Odoo Operations Skill

## Available Tools

- `odoo_connect`: Connect to Odoo
- `odoo_get_account_summary`: Get financial summary
- `odoo_get_invoices`: List invoices
- `odoo_create_invoice`: Create invoice
- `odoo_get_partners`: Search customers/vendors
- `odoo_create_partner`: Create new partner
- `odoo_register_payment`: Record payment

## Example Usage

### Check Financial Status
1. Call `odoo_get_account_summary`
2. Review receivables and payables
3. Update Dashboard.md with metrics

### Create Invoice for Client
1. Call `odoo_get_partners` with search term
2. If not found, `odoo_create_partner`
3. Call `odoo_create_invoice` with partner_id
4. Create approval request in Pending_Approval/
```

### Weekly Accounting Audit

The AI Employee can now:

1. **Review unpaid invoices**:
   - Call `odoo_get_invoices` with state='posted'
   - Identify overdue payments
   - Flag for follow-up in CEO briefing

2. **Generate financial reports**:
   - Call `odoo_get_account_summary`
   - Calculate revenue, expenses, net position
   - Update Business_Goals.md

3. **Process payments**:
   - Monitor bank transactions (via other watchers)
   - Match with Odoo invoices
   - Call `odoo_register_payment` (requires approval)

## Troubleshooting

### Odoo Won't Start

```bash
# Check logs
docker-compose logs odoo

# Check database
docker-compose logs db

# Restart services
docker-compose restart
```

### MCP Server Can't Connect

1. Verify Odoo is running:
   ```bash
   curl http://localhost:8069
   ```

2. Check credentials:
   ```bash
   docker-compose exec odoo env | grep ODOO
   ```

3. Test XML-RPC connection:
   ```python
   import xmlrpc.client
   url = 'http://localhost:8069'
   db = 'postgres'
   username = 'admin'
   password = 'admin'
   common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
   uid = common.authenticate(db, username, password, {})
   print(f'UID: {uid}')
   ```

### Database Issues

**Reset database** (WARNING: Deletes all data):
```bash
docker-compose down -v
docker-compose up -d db
# Wait for DB to start
docker-compose up -d odoo
```

## Security Considerations

1. **Change default passwords** in production
2. **Use HTTPS** for external access
3. **Restrict network access** to Odoo ports
4. **Regular backups** of PostgreSQL data
5. **Keep Odoo updated** to latest version

## Backup and Restore

### Backup

```bash
# Backup PostgreSQL database
docker-compose exec db pg_dump -U odoo postgres > backup_$(date +%Y%m%d).sql

# Backup Odoo filestore
docker-compose exec odoo tar -czf /tmp/filestore_backup.tar.gz /var/lib/odoo
docker-compose cp odoo:/tmp/filestore_backup.tar.gz ./backups/
```

### Restore

```bash
# Restore database
docker-compose exec -T db psql -U odoo postgres < backup_20260306.sql

# Restore filestore
docker-compose cp ./backups/filestore_backup.tar.gz odoo:/tmp/
docker-compose exec odoo tar -xzf /tmp/filestore_backup.tar.gz -C /var/lib/odoo
```

## Next Steps

1. **Configure chart of accounts** for your business
2. **Set up tax rules** based on your jurisdiction
3. **Import existing customers** from CSV
4. **Configure payment terms** and methods
5. **Set up automated bank reconciliation** (if supported)
6. **Create product catalog** for invoicing

## Resources

- [Odoo Documentation](https://www.odoo.com/documentation)
- [Odoo 17 External API](https://www.odoo.com/documentation/17.0/developer/reference/external_api.html)
- [Odoo Community Forum](https://www.odoo.com/forum/help-1)
- [Odoo MCT Server Reference](https://github.com/AlanOgic/mcp-odoo-adv)

---

*Gold Tier Feature - AI Employee Project*
