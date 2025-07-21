const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const jwt = require('jsonwebtoken');

// SQLite Database Connection
const db = new sqlite3.Database('./note_app.sqlite', (err) => {
    if (err) {
        console.error('Could not open database:', err);
    } else {
        console.log('Connected to SQLite database');
    }
});

// Middleware to check if user is logged in
exports.isLoggedIn = (req, res, next) => {
    console.log('isLoggedIn middleware called');
    const token = req.cookies.jwt;
    
    if (!token) {
        console.log('No token found, redirecting to login');
        return res.redirect('/login');
    }
    
    try {
        console.log('Token of the user trying to login:', token);
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        console.log('Decoded token:', decoded);

        // Fetch the user from the database
        db.get('SELECT * FROM users WHERE id = ?', [decoded.id], (err, user) => {
            if (err) {
                console.error('Database error:', err);
                return res.status(500).redirect('/login');
            }
            
            if (!user) {
                console.log('User not found for id:', decoded.id);
                res.clearCookie('jwt');
                return res.redirect('/login');
            }
            
            console.log('User found:', user.id);
            req.user = user; // Set the entire user object
            next();
        });
    } catch (error) {
        console.error('Token verification failed:', error.message);
        res.clearCookie('jwt');
        return res.redirect('/login');
    }
};

// Display dashboard with user's notes
exports.getDashboard = (req, res) => {
    console.log('getDashboard function called');
    console.log('User:', req.user);  // This should be set by isLoggedIn middleware

    if (!req.user) {
        console.log('No user information found');
        return res.redirect('/login');
    }

    // Fetch user's notes
    db.all('SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC', [req.user.id], (err, notes) => {
        if (err) {
            console.error('Error fetching notes:', err);
            return res.status(500).send('An error occurred while fetching notes');
        }

        // Render dashboard with user and notes
        res.render('dashboard', {
            user: req.user,
            notes: notes,
            isAdmin: req.user.is_admin // Pass this to the view for conditional rendering
        });
    });
};

// Add a new note
exports.addNote = (req, res) => {
    const { title, content } = req.body;
    const userId = req.user.id;

    db.run('INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)', 
    [userId, title, content], function(err) {
        if (err) {
            console.error('Error adding note:', err);
            return res.status(500).json({ message: 'Failed to add note' });
        }
        res.status(200).json({ message: 'Note added successfully', noteId: this.lastID });
    });
};

// Delete a note
exports.deleteNote = (req, res) => {
    const noteId = req.params.id;
    const userId = req.user.id;
    console.log("id of the user trying to delete note:", userId);

    db.run('DELETE FROM notes WHERE id = ? AND user_id = ?', [noteId, userId], function(err) {
        if (err) {
            console.error('Error deleting note:', err);
            return res.status(500).json({ message: 'Failed to delete note' });
        }
        if (this.changes === 0) {
            return res.status(404).json({ message: 'Note not found or not authorized to delete' });
        }
        res.status(200).json({ message: 'Note deleted successfully' });
    });
};

// Update a note
exports.updateNote = (req, res) => {
    const noteId = req.params.id;
    const { title, content } = req.body;
    const userId = req.user.id;

    db.run('UPDATE notes SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?', 
    [title, content, noteId, userId], function(err) {
        if (err) {
            console.error('Error updating note:', err);
            return res.status(500).json({ message: 'Failed to update note' });
        }
        if (this.changes === 0) {
            return res.status(404).json({ message: 'Note not found or not authorized to update' });
        }
        res.status(200).json({ message: 'Note updated successfully' });
    });
};