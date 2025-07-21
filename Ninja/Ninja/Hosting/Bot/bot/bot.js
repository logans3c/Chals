const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const CONFIG = {
    APPNAME: process.env['APPNAME'] || "Admin",
    APPURL: process.env['APPURL'] || "http://localhost:5000",
    // URL regex to only allow localhost URLs
    APPURLREGEX: process.env['APPURLREGEX'] || "^http:\\/\\/localhost:[0-9]+\\/.*$",
    ADMINPASS: process.env['ADMIN_PASSWORD'] || "adminwwwwwwwwwwwwwwws",
    APPLIMITTIME: Number(process.env['APPLIMITTIME'] || "60"),
    APPLIMIT: Number(process.env['APPLIMIT'] || "5"),
    APPEXTENSIONS: (() => {
        const extDir = path.join(__dirname, 'extensions');
        const dir = []
        fs.readdirSync(extDir).forEach(file => {
            if (fs.lstatSync(path.join(extDir, file)).isDirectory()) {
                dir.push(path.join(extDir, file))
            }
        });
        return dir.join(',')
    })()
}

console.table(CONFIG)

function sleep(s) {
    return new Promise((resolve) => setTimeout(resolve, s * 1000))
}

function getBrowser() {
    const browserPaths = [
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium"
    ]
    for (const browserPath of browserPaths) {
        if (fs.existsSync(browserPath)) {
            return browserPath
        }
    }
    throw new Error("No browser found")
}

/**
 * @type {puppeteer.LaunchOptions}
 **/
const browserArgs = {
    executablePath: getBrowser(),
    headless: (()=>{
        const is_x11_exists = fs.existsSync('/tmp/.X11-unix');
        if (process.env['DISPLAY'] !== undefined && is_x11_exists) {
            return false;
        }
        return true;
    })(),
    args: [
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-gpu',
        '--no-gpu',
        '--disable-default-apps',
        '--disable-translate',
        '--disable-device-discovery-notifications',
        '--disable-software-rasterizer',
        '--disable-xss-auditor',
        ...(() => {
            if (CONFIG.APPEXTENSIONS === "") return [];
            return [
                `--disable-extensions-except=${CONFIG.APPEXTENSIONS}`,
                `--load-extension=${CONFIG.APPEXTENSIONS}`
            ]
        })(),
    ],
    ignoreHTTPSErrors: true
}
/**
 * @type {puppeteer.Browser}
 */
var initBrowser = null;

console.log("Bot started...");

module.exports = {
    name: CONFIG.APPNAME,
    urlRegex: CONFIG.APPURLREGEX,
    rateLimit: {
        windowS: CONFIG.APPLIMITTIME,
        max: CONFIG.APPLIMIT
    },
    bot: async (urlToVisit) => {
        // Check if URL matches the allowed pattern
        if (!new RegExp(CONFIG.APPURLREGEX).test(urlToVisit)) {
            console.error(`URL ${urlToVisit} doesn't match the allowed pattern`);
            return false;
        }
        
        console.log(`Bot will visit: ${urlToVisit}`);
        var context = null;
        
        // Use the same browser instance for all bots if no extensions are loaded
        if (CONFIG.APPEXTENSIONS === "") {
            if (initBrowser === null) {
                initBrowser = await puppeteer.launch(browserArgs);
            }
            context = await initBrowser.createBrowserContext();
        }
        // Create a new browser instance for each bot if extensions are loaded
        else {
            context = (await puppeteer.launch(browserArgs)).defaultBrowserContext();
        }
        
        try {
            const page = await context.newPage();

            // Function to log in as admin
            async function login(page) {
                console.log("Logging in as admin...");
                await page.goto(`${CONFIG.APPURL}/admin-login`, {
                    waitUntil: 'networkidle2'
                });

                // Fill login form
                await page.type('#username', 'admin');
                await page.type('#password', CONFIG.ADMINPASS);
                
                // Click login button and wait for navigation
                await Promise.all([
                    page.waitForNavigation({ waitUntil: 'networkidle2' }),
                    page.click('button[type="submit"]')
                ]);
                
                console.log("Login successful, checking admin dashboard...");
                
                // Go to admin dashboard to check reports
                await page.goto(`${CONFIG.APPURL}/admin-dashboard`, {
                    waitUntil: 'networkidle2'
                });
            }

            // Perform login flow
            await login(page);

            console.log(`Bot visiting reported URL: ${urlToVisit}`);
            // Visit the actual reported URL
            await page.goto(urlToVisit, {
                waitUntil: 'networkidle2'
            });
            
            // Wait for a while to allow any potential XSS to execute
            await sleep(10);

            console.log("Bot finished checking the URL");
            return true;
        } catch (e) {
            console.error(`Bot error: ${e}`);
            return false;
        } finally {
            if (CONFIG.APPEXTENSIONS !== "") {
                await context.browser().close();
                console.log("Browser closed");
            } else {
                await context.close();
                console.log("Browser context closed");
            }
        }
    }
}
