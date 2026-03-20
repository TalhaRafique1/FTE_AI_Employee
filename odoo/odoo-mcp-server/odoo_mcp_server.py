"""
Odoo MCP Server - Gold Tier

Model Context Protocol server for Odoo Community Edition integration.
Provides accounting, invoicing, and business management capabilities.

Usage:
    python odoo_mcp_server.py

Or via Docker:
    docker-compose up odoo-mcp
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import xmlrpc.client

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('odoo-mcp-server')


class OdooClient:
    """Client for Odoo JSON-RPC API."""

    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize Odoo client.

        Args:
            url: Odoo server URL (e.g., http://localhost:8069)
            db: Database name
            username: Odoo username
            password: Odoo password
        """
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.common = None
        self.models = None

    def authenticate(self) -> bool:
        """
        Authenticate with Odoo.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Common endpoint for authentication
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                logger.info(f'Authenticated with Odoo as user ID: {self.uid}')
                return True
            else:
                logger.error('Odoo authentication failed')
                return False

        except Exception as e:
            logger.error(f'Error authenticating with Odoo: {e}')
            return False

    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """
        Execute a method on an Odoo model.

        Args:
            model: Model name (e.g., 'account.move', 'res.partner')
            method: Method name (e.g., 'search', 'read', 'create')
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from Odoo
        """
        if not self.uid:
            if not self.authenticate():
                raise Exception('Not authenticated with Odoo')

        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )
        except Exception as e:
            logger.error(f'Error executing {method} on {model}: {e}')
            raise

    def search(self, model: str, domain: List, limit: int = 80, fields: Optional[List[str]] = None) -> List[Dict]:
        """Search records in Odoo."""
        ids = self.execute(model, 'search', domain, limit=limit)
        if fields:
            return self.execute(model, 'read', [ids], fields=fields)
        return ids

    def create(self, model: str, values: Dict) -> int:
        """Create a record in Odoo."""
        return self.execute(model, 'create', [values])

    def write(self, model: str, ids: List, values: Dict) -> bool:
        """Update records in Odoo."""
        return self.execute(model, 'write', [ids], values)

    def delete(self, model: str, ids: List) -> bool:
        """Delete records in Odoo."""
        return self.execute(model, 'unlink', [ids])

    # Business-specific methods
    def get_invoices(self, state: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get invoices, optionally filtered by state."""
        domain = []
        if state:
            domain.append(('state', '=', state))

        return self.search(
            'account.move',
            domain,
            limit=limit,
            fields=['id', 'name', 'partner_id', 'amount_total', 'state', 'invoice_date', 'invoice_date_due']
        )

    def create_invoice(self, partner_id: int, invoice_type: str = 'out_invoice',
                       lines: Optional[List[Dict]] = None) -> int:
        """
        Create an invoice.

        Args:
            partner_id: Customer/partner ID
            invoice_type: Type (out_invoice, in_invoice, out_refund, in_refund)
            lines: Invoice line items

        Returns:
            Invoice ID
        """
        invoice_values = {
            'move_type': invoice_type,
            'partner_id': partner_id,
            'invoice_line_ids': [],
        }

        if lines:
            for line in lines:
                invoice_values['invoice_line_ids'].append((0, 0, {
                    'product_id': line.get('product_id'),
                    'name': line.get('name', 'Service'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0),
                }))

        return self.create('account.move', invoice_values)

    def get_partners(self, search_term: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get partners (customers/vendors)."""
        domain = []
        if search_term:
            domain.append(('name', 'ilike', search_term))

        return self.search(
            'res.partner',
            domain,
            limit=limit,
            fields=['id', 'name', 'email', 'phone', 'company_id']
        )

    def create_partner(self, name: str, email: Optional[str] = None,
                       phone: Optional[str] = None, company_type: str = 'person') -> int:
        """Create a partner."""
        return self.create('res.partner', {
            'name': name,
            'email': email,
            'phone': phone,
            'company_type': company_type,
        })

    def get_products(self, search_term: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get products."""
        domain = []
        if search_term:
            domain.append(('name', 'ilike', search_term))

        return self.search(
            'product.template',
            domain,
            limit=limit,
            fields=['id', 'name', 'list_price', 'categ_id']
        )

    def get_account_summary(self) -> Dict:
        """Get summary of accounts."""
        try:
            # Get total receivables
            receivables = self.search(
                'account.move',
                [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
                limit=1000,
                fields=['amount_total', 'amount_residual']
            )

            total_receivable = sum(item.get('amount_residual', 0) for item in receivables)

            # Get total payables
            payables = self.search(
                'account.move',
                [('move_type', '=', 'in_invoice'), ('state', '=', 'posted')],
                limit=1000,
                fields=['amount_total', 'amount_residual']
            )

            total_payable = sum(item.get('amount_residual', 0) for item in payables)

            return {
                'total_receivable': total_receivable,
                'total_payable': total_payable,
                'net_position': total_receivable - total_payable,
                'invoice_count': len(receivables),
                'bill_count': len(payables),
            }
        except Exception as e:
            logger.error(f'Error getting account summary: {e}')
            return {'error': str(e)}

    def confirm_invoice(self, invoice_id: int) -> bool:
        """Confirm/post an invoice."""
        return self.write('account.move', [invoice_id], {'state': 'posted'})

    def register_payment(self, invoice_id: int, amount: float,
                         payment_date: Optional[str] = None) -> bool:
        """Register payment for an invoice."""
        try:
            # Create payment record
            payment_values = {
                'move_id': invoice_id,
                'payment_type': 'inbound',
                'amount': amount,
                'date': payment_date or datetime.now().strftime('%Y-%m-%d'),
            }
            self.create('account.payment', payment_values)
            return True
        except Exception as e:
            logger.error(f'Error registering payment: {e}')
            return False


# Create MCP server
server = Server('odoo-mcp')

# Global Odoo client (will be initialized from env vars)
odoo_client: Optional[OdooClient] = None


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Odoo tools."""
    return [
        Tool(
            name='odoo_connect',
            description='Connect to Odoo and verify authentication',
            inputSchema={
                'type': 'object',
                'properties': {}
            }
        ),
        Tool(
            name='odoo_get_account_summary',
            description='Get summary of accounts receivable and payable',
            inputSchema={
                'type': 'object',
                'properties': {}
            }
        ),
        Tool(
            name='odoo_get_invoices',
            description='Get invoices from Odoo, optionally filtered by state',
            inputSchema={
                'type': 'object',
                'properties': {
                    'state': {
                        'type': 'string',
                        'description': 'Invoice state (draft, posted, cancel)',
                        'enum': ['draft', 'posted', 'cancel']
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Maximum number of invoices to return',
                        'default': 10
                    }
                }
            }
        ),
        Tool(
            name='odoo_create_invoice',
            description='Create a new invoice in Odoo',
            inputSchema={
                'type': 'object',
                'properties': {
                    'partner_id': {
                        'type': 'integer',
                        'description': 'Customer/partner ID'
                    },
                    'invoice_type': {
                        'type': 'string',
                        'description': 'Type of invoice',
                        'enum': ['out_invoice', 'in_invoice', 'out_refund', 'in_refund'],
                        'default': 'out_invoice'
                    },
                    'lines': {
                        'type': 'array',
                        'description': 'Invoice line items',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'product_id': {'type': 'integer'},
                                'name': {'type': 'string'},
                                'quantity': {'type': 'number'},
                                'price_unit': {'type': 'number'}
                            }
                        }
                    }
                },
                'required': ['partner_id']
            }
        ),
        Tool(
            name='odoo_get_partners',
            description='Search for partners (customers/vendors)',
            inputSchema={
                'type': 'object',
                'properties': {
                    'search_term': {
                        'type': 'string',
                        'description': 'Search term for partner name'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Maximum number of partners to return',
                        'default': 10
                    }
                }
            }
        ),
        Tool(
            name='odoo_create_partner',
            description='Create a new partner (customer/vendor)',
            inputSchema={
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Partner name'
                    },
                    'email': {
                        'type': 'string',
                        'description': 'Email address'
                    },
                    'phone': {
                        'type': 'string',
                        'description': 'Phone number'
                    },
                    'company_type': {
                        'type': 'string',
                        'description': 'Type of partner',
                        'enum': ['person', 'company'],
                        'default': 'person'
                    }
                },
                'required': ['name']
            }
        ),
        Tool(
            name='odoo_get_products',
            description='Search for products',
            inputSchema={
                'type': 'object',
                'properties': {
                    'search_term': {
                        'type': 'string',
                        'description': 'Search term for product name'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Maximum number of products to return',
                        'default': 10
                    }
                }
            }
        ),
        Tool(
            name='odoo_confirm_invoice',
            description='Confirm/post an invoice',
            inputSchema={
                'type': 'object',
                'properties': {
                    'invoice_id': {
                        'type': 'integer',
                        'description': 'Invoice ID to confirm'
                    }
                },
                'required': ['invoice_id']
            }
        ),
        Tool(
            name='odoo_register_payment',
            description='Register payment for an invoice',
            inputSchema={
                'type': 'object',
                'properties': {
                    'invoice_id': {
                        'type': 'integer',
                        'description': 'Invoice ID'
                    },
                    'amount': {
                        'type': 'number',
                        'description': 'Payment amount'
                    },
                    'payment_date': {
                        'type': 'string',
                        'description': 'Payment date (YYYY-MM-DD)'
                    }
                },
                'required': ['invoice_id', 'amount']
            }
        ),
        Tool(
            name='odoo_search',
            description='Generic search on any Odoo model',
            inputSchema={
                'type': 'object',
                'properties': {
                    'model': {
                        'type': 'string',
                        'description': 'Model name (e.g., account.move, res.partner)'
                    },
                    'domain': {
                        'type': 'array',
                        'description': 'Search domain'
                    },
                    'fields': {
                        'type': 'array',
                        'description': 'Fields to return',
                        'items': {'type': 'string'}
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Maximum number of records',
                        'default': 80
                    }
                },
                'required': ['model']
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    global odoo_client

    try:
        if name == 'odoo_connect':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Odoo client not initialized')]

            if odoo_client.authenticate():
                return [TextContent(
                    type='text',
                    text=json.dumps({'success': True, 'uid': odoo_client.uid}, indent=2)
                )]
            else:
                return [TextContent(type='text', text='Authentication failed')]

        elif name == 'odoo_get_account_summary':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            summary = odoo_client.get_account_summary()
            return [TextContent(
                type='text',
                text=json.dumps(summary, indent=2)
            )]

        elif name == 'odoo_get_invoices':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            state = arguments.get('state')
            limit = arguments.get('limit', 10)
            invoices = odoo_client.get_invoices(state=state, limit=limit)
            return [TextContent(
                type='text',
                text=json.dumps(invoices, indent=2)
            )]

        elif name == 'odoo_create_invoice':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            partner_id = arguments.get('partner_id')
            invoice_type = arguments.get('invoice_type', 'out_invoice')
            lines = arguments.get('lines', [])

            invoice_id = odoo_client.create_invoice(partner_id, invoice_type, lines)
            return [TextContent(
                type='text',
                text=json.dumps({'success': True, 'invoice_id': invoice_id}, indent=2)
            )]

        elif name == 'odoo_get_partners':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            search_term = arguments.get('search_term')
            limit = arguments.get('limit', 10)
            partners = odoo_client.get_partners(search_term, limit)
            return [TextContent(
                type='text',
                text=json.dumps(partners, indent=2)
            )]

        elif name == 'odoo_create_partner':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            name = arguments.get('name')
            email = arguments.get('email')
            phone = arguments.get('phone')
            company_type = arguments.get('company_type', 'person')

            partner_id = odoo_client.create_partner(name, email, phone, company_type)
            return [TextContent(
                type='text',
                text=json.dumps({'success': True, 'partner_id': partner_id}, indent=2)
            )]

        elif name == 'odoo_get_products':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            search_term = arguments.get('search_term')
            limit = arguments.get('limit', 10)
            products = odoo_client.get_products(search_term, limit)
            return [TextContent(
                type='text',
                text=json.dumps(products, indent=2)
            )]

        elif name == 'odoo_confirm_invoice':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            invoice_id = arguments.get('invoice_id')
            success = odoo_client.confirm_invoice(invoice_id)
            return [TextContent(
                type='text',
                text=json.dumps({'success': success}, indent=2)
            )]

        elif name == 'odoo_register_payment':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            invoice_id = arguments.get('invoice_id')
            amount = arguments.get('amount')
            payment_date = arguments.get('payment_date')

            success = odoo_client.register_payment(invoice_id, amount, payment_date)
            return [TextContent(
                type='text',
                text=json.dumps({'success': success}, indent=2)
            )]

        elif name == 'odoo_search':
            if not odoo_client:
                return [TextContent(type='text', text='Error: Not connected to Odoo')]

            model = arguments.get('model')
            domain = arguments.get('domain', [])
            fields = arguments.get('fields')
            limit = arguments.get('limit', 80)

            results = odoo_client.search(model, domain, limit, fields)
            return [TextContent(
                type='text',
                text=json.dumps(results, indent=2)
            )]

        else:
            return [TextContent(type='text', text=f'Unknown tool: {name}')]

    except Exception as e:
        logger.error(f'Error in tool call {name}: {e}')
        return [TextContent(
            type='text',
            text=json.dumps({'error': str(e)}, indent=2)
        )]


def initialize_odoo_client():
    """Initialize Odoo client from environment variables."""
    global odoo_client

    url = os.getenv('ODOO_URL', 'http://localhost:8069')
    db = os.getenv('ODOO_DB', 'postgres')
    username = os.getenv('ODOO_USER', 'admin')
    password = os.getenv('ODOO_PASSWORD', 'admin')

    logger.info(f'Connecting to Odoo at {url}')
    odoo_client = OdooClient(url, db, username, password)

    if odoo_client.authenticate():
        logger.info('Successfully connected to Odoo')
    else:
        logger.error('Failed to connect to Odoo')


async def main():
    """Run the MCP server."""
    # Initialize Odoo client
    initialize_odoo_client()

    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == '__main__':
    asyncio.run(main())
