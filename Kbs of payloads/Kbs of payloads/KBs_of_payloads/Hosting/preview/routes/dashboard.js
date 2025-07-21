const express = require('express');
const router = express.Router();
const dashboardController = require('../controllers/dashboard');

router.get('/', dashboardController.isLoggedIn, dashboardController.getDashboard);
router.get('/dashboard', dashboardController.isLoggedIn, dashboardController.getDashboard);
router.post('/notes', dashboardController.isLoggedIn, dashboardController.addNote);
router.delete('/notes/:id', dashboardController.isLoggedIn, dashboardController.deleteNote);
router.put('/notes/:id', dashboardController.isLoggedIn, dashboardController.updateNote);

module.exports = router;