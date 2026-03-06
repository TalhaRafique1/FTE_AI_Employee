/**
 * Test Gmail MCP Server
 */

async function test() {
  console.log('Testing Gmail MCP Server...\n');
  
  try {
    console.log('1. Testing Node.js...');
    console.log('   ✓ Node.js is working\n');
    
    console.log('2. Testing dependencies...');
    await import('@modelcontextprotocol/sdk');
    console.log('   ✓ MCP SDK loaded\n');
    
    await import('googleapis');
    console.log('   ✓ Googleapis loaded\n');
    
    console.log('3. Testing credentials file...');
    const fs = await import('fs');
    const path = await import('path');
    
    const credentialsPath = path.join(process.cwd(), '..', 'credentials.json');
    if (fs.existsSync(credentialsPath)) {
      console.log('   ✓ credentials.json found\n');
    } else {
      console.log('   ⚠ credentials.json not found (optional for test)\n');
    }
    
    console.log('4. Testing token file...');
    const tokenPath = path.join(process.homedir(), '.ai_employee', 'gmail_token.pickle');
    if (fs.existsSync(tokenPath)) {
      console.log('   ✓ Gmail token found\n');
    } else {
      console.log('   ⚠ Gmail token not found (will be created on first use)\n');
    }
    
    console.log('✅ All basic tests passed!\n');
    console.log('Gmail MCP Server is installed correctly.');
    console.log('\nTo test with authentication:');
    console.log('  qwen -p "Send a test email to your-email@gmail.com"');
    console.log('\nOr run the server manually:');
    console.log('  node index.js');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('\nPlease check installation.');
    process.exit(1);
  }
}

test();
