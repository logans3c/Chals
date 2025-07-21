const express = require('express');
const router = express.Router();
const { isLoggedIn, getDashboard, addNote, deleteNote, updateNote } = require('../controllers/dashboard');

router.get('/', (req, res) => {
    res.render('index');
});

router.get('/login', (req, res) => {
    if (req.cookies.jwt) {
        return res.redirect('/dashboard');
    }
    res.render('login');
});

router.get('/register', (req, res) => {
    res.render('register');
});

router.get('/logout', (req, res) => {
    res.clearCookie('jwt');
    res.redirect('/login');
});

router.get('/dashboard', isLoggedIn,getDashboard,(req, res) => {
    res.render('dashboard');
});
router.post('/notes', isLoggedIn, addNote);
router.delete('/notes/:id', isLoggedIn, deleteNote);
router.put('/notes/:id', isLoggedIn, updateNote);

module.exports = router;