const express = require('express');
const puppeteer = require('puppeteer');

const app = express();
const PORT = 3000;

app.use(express.json());

const domain = process.env.DOMAIN || '127.0.0.1';
const cookie = {
  name: 'FLAG',
  value: process.env.FLAG || 'placeholder',
  domain: domain,
  httpOnly: false  // Make the cookie accessible to JavaScript
};

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay));

// Handler for the /visit endpoint to visit URLs as admin
app.post('/visit', async (req, res) => {
  const { url } = req.body;
    
  if (!url || (!url.startsWith("http://") && !url.startsWith("https://"))) {
    return res.status(400).send('Please provide a valid URL');
  }

  // Check if the URL is allowed (only internal URLs)
  if (!url.includes('127.0.0.1:5000') && !url.includes('localhost:5000')) {
    return res.status(403).send('Only internal application URLs are allowed');
  }

  try {
    const browser = await puppeteer.launch({
      args: ['--no-sandbox', '--disable-setuid-sandbox'], // Required in Docker
      ignoreHTTPSErrors: true,
      timeout: 30000
    });

    const page = await browser.newPage();
    await page.setCookie(cookie);
    
    // Login as admin
    await page.goto('http://127.0.0.1:5000/admin/login', {
      waitUntil: 'load',
      timeout: 10 * 1000
    });
    await sleep(2000);
    await page.type('input[id="username"]', 'admin');
    await page.type('input[id="password"]', process.env.ADMIN_PASSWORD || 'adminpass123');
    await Promise.all([
      page.click('button[type="submit"]'), 
      page.waitForNavigation({ waitUntil: 'load' })
    ]);
    await sleep(2000);
    
    // Visit the requested page (typically a review page)
    await page.goto(url, {
      waitUntil: "networkidle2", 
      timeout: 30000
    });
    
    // If this is an application review page, automatically approve it
    if (url.includes('/admin/review/')) {
      try {
        await page.waitForSelector('select[id="status"]', { timeout: 5000 });
        console.log('Found status dropdown');
        await page.select('select[id="status"]', 'approved');
        await Promise.all([
          page.click('button[type="submit"]'),
          page.waitForNavigation({ waitUntil: 'load' })
        ]);
        console.log(`Approved application at ${url}`);
      } catch (error) {
        console.error('Error approving application:', error);
        console.error('Error details:', error.message);
      }
    }
    await browser.close();
    res.send('Page visited successfully by admin bot');
  } catch (error) {
    console.error('Error visiting page:', error);
    res.status(500).send('An error occurred while visiting the page');
  }
});

// Basic health check endpoint
app.get('/status', (req, res) => {
  res.send('CTF Bot is running');
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`CTF Bot server is running on port ${PORT}`);
});


