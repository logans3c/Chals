//Npm modules
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const dotenv = require('dotenv');
const cookieParser = require('cookie-parser');
const path = require('path');
dotenv.config();
const app = express();

// Database connection and initialization function
async function initializeDatabase() {
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database('./note_app.sqlite', (err) => {
            if (err) {
                console.error('Failed to open database:', err);
                reject(err);
            } else {
                console.log('Connected to SQLite');
               
                // Create 'users' table
                db.run(`
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        is_admin BOOLEAN NOT NULL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                `, (err) => {
                    if (err) {
                        console.error('Failed to create users table:', err);
                        reject(err);
                    }
                });

                // Create 'admins' table with CHECK constraint
                db.run(`
                    CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        is_admin BOOLEAN NOT NULL DEFAULT 1 CHECK (is_admin = 1),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                `, (err) => {
                    if (err) {
                        console.error('Failed to create admins table:', err);
                        reject(err);
                    }
                });

                // Create 'notes' table
                db.run(`
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                `, (err) => {
                    if (err) {
                        console.error('Failed to create notes table:', err);
                        reject(err);
                    } else {
                        resolve(db);
                    }
                });
            }
        });
    });
}
// Middleware
app.use(express.static('public'));
app.use(express.urlencoded({extended:false}));
app.use(express.json());
app.use(cookieParser());


// Html engine
app.set('view engine','hbs');

// Initialize database and start server
initializeDatabase()
    .then((db) => {
        global.db = db;
        console.log('Database initialized');

        //routes
        app.use('/', require('./routes/pages'));
        app.use('/auth', require('./routes/auth'));
        const dashboardRoutes = require('./routes/dashboard');
        app.use('/dashboard', dashboardRoutes);
        const adminRoutes = require('./routes/admin');
        app.use('/admin', adminRoutes); // This line mounts all admin routes under /admin


        // Error handling middleware
        app.use((err, req, res, next) => {
            console.error(err.stack);
            res.status(500).send('Something broke!');
        });

        // Start the server
        const PORT = process.env.PORT || 3000;
        app.listen(PORT, () => console.log(`App listening on port ${PORT}!`));
    })
    .catch((err) => {
        console.error('Failed to initialize database:', err);
        process.exit(1);
    });

