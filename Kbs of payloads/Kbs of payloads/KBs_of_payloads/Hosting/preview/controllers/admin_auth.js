const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

exports.getAdminLogin = (req, res) => {
    res.render('admin_login');
};

exports.postAdminLogin = (req, res) => {
    const { email, password } = req.body;
    
    const query = `SELECT * FROM admins WHERE email = '${email}' AND is_admin = 1`;

    db.get(query, (err, admin) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Internal server error' });
        }
        
        if (!admin) {
            console.log(admin)
            return res.status(401).json({ error: 'Invalid email' });
        }
        console.log(admin)
        
        
        // Now compare the password
        bcrypt.compare(password, admin.password, (err, isMatch) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ error: 'Internal server error' });
            }
            
            if (!isMatch) {
                return res.status(401).json({ error: 'Password is wrong' });
            }
            
            // If successful, issue a token and redirect
            const token = jwt.sign({ id: admin.id, isAdmin: true }, process.env.JWT_SECRET, { expiresIn: '1h' });
            res.cookie('adminToken', token, { httpOnly: true, maxAge: 3600000 }); // 1 hour
            res.redirect('/admin/dashboard');
        });
    });
};


exports.adminLogout = (req, res) => {
    res.clearCookie('adminToken');
    res.json({ message: 'Admin logged out successfully' });
};

// Middleware to check if user is admin
exports.isAdmin = (req, res, next) => {
    const token = req.cookies.adminToken;

    if (!token) {
        return res.status(401).json({ error: 'No token, authorization denied' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.admin = decoded;

        if (!decoded.isAdmin) {
            return res.status(403).json({ error: 'Not authorized as an admin' });
        }

        next();
    } catch (err) {
        res.status(401).json({ error: 'Token is not valid' });
    }
};