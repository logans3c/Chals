const dfVariable = process.env.DF || "flag{N3v3r_Tru5t_4_St4rtup}";

exports.getAdminDashboard = (req, res) => {
    // Fetch insights data
    db.all('SELECT COUNT(*) as totalUsers FROM users WHERE is_admin = 0', [], (err, userCount) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Internal server error' });
        }
        
        db.all('SELECT COUNT(*) as totalNotes FROM notes', [], (err, noteCount) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ error: 'Internal server error' });
            }
            
            db.all('SELECT COUNT(DISTINCT user_id) as activeUsers FROM notes WHERE created_at > datetime("now", "-30 days")', [], (err, activeUsers) => {
                if (err) {
                    console.error(err);
                    return res.status(500).json({ error: 'Internal server error' });
                }
                
                res.render('admin_dashboard', {
                    totalUsers: userCount[0].totalUsers,
                    totalNotes: noteCount[0].totalNotes,
                    activeUsers: activeUsers[0].activeUsers,
                    df: dfVariable

                });
            });
        });
    });
};

exports.removeUser = (req, res) => {
    const userId = req.params.id;
    
    db.run('DELETE FROM users WHERE id = ? AND is_admin = 0', [userId], function(err) {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Internal server error' });
        }
        
        if (this.changes === 0) {
            return res.status(404).json({ error: 'User not found or is an admin' });
        }
        
        // Also delete user's notes
        db.run('DELETE FROM notes WHERE user_id = ?', [userId], (err) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ error: 'Internal server error' });
            }
            
            res.json({ message: 'User and their notes removed successfully' });
        });
    });
};

exports.listUsers = (req, res) => {
    db.all('SELECT id, name, email, created_at FROM users WHERE is_admin = 0', [], (err, users) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: 'Internal server error' });
        }
        
        res.json(users);
    });
};