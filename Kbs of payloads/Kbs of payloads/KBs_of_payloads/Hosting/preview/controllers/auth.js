const sqlite3 = require('sqlite3').verbose();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Create or open an SQLite database file
const db = new sqlite3.Database('./note_app.sqlite', (err) => {
    if (err) {
        console.error('Could not connect to SQLite database', err);
    } else {
        console.log('Connected to SQLite database');
    }
});

// Register User
exports.register = (req, res) => {
    console.log(req.body);
    const { name, email, password, passwordConfirm } = req.body;

    // Check if the email is already registered
    db.get('SELECT email FROM users WHERE email = ?', [email], async (err, result) => {
        if (err) {
            console.log(err);
            return res.status(500).render('register', {
                message: 'An error occurred'
            });
        }
        if (result) {
            return res.render('register', {
                message: 'That email is already in use'
            });
        } else if (password !== passwordConfirm) {
            return res.render('register', {
                message: 'Passwords do not match'
            });
        }

        let hashedPassword = await bcrypt.hash(password, 8);
        console.log(hashedPassword);

        // Insert new user into the database
        db.run(
            'INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, ?)',
            [name, email, hashedPassword, 0], // 0 for is_admin means it's a regular user
            (err) => {
                if (err) {
                    console.log(err);
                    return res.status(500).render('register', {
                        message: 'An error occurred during registration'
                    });
                }
                console.log('User registered');
                return res.render('register', {
                    message: 'User Registered Successfully'
                });
            }
        );
    });
};

// Login User
exports.login = (req, res) => {
    const { email, password } = req.body;
    if (!email || !password) {
        return res.status(400).render('login', {
            message: 'Please provide an email and password'
        });
    }

    // Query the user by email
    db.get('SELECT * FROM users WHERE email = ?', [email], async (err, user) => {
        if (err) {
            console.log(err);
            return res.status(500).render('login', {
                message: 'An error occurred. Please try again.'
            });
        }
        if (!user || !(await bcrypt.compare(password, user.password))) {
            return res.status(401).render('login', {
                message: 'Invalid email or password'
            });
        }

        const token = jwt.sign({ id: user.id, is_admin: user.is_admin }, process.env.JWT_SECRET, {
            expiresIn: process.env.JWT_EXPIRES_IN
        });

        const cookieOptions = {
            expires: new Date(
                Date.now() + parseInt(process.env.JWT_COOKIE_EXPIRES) * 24 * 60 * 60 * 1000
            ),
            httpOnly: true
        };
        res.cookie('jwt', token, cookieOptions);

        // Redirect to dashboard for both regular users and admins
        res.redirect('/dashboard');
    });
};

// Logout User
exports.logout = (req, res) => {
    res.cookie('jwt', 'logout', {
        expires: new Date(Date.now() + 2 * 1000),
        httpOnly: true
    });
    res.status(200).redirect('/');
};
