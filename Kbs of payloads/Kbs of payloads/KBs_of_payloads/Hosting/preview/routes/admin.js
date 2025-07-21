const express = require('express');
const router = express.Router();
const adminAuthController = require('../controllers/admin_auth');
const adminDashboardController = require('../controllers/admin_dashboard');

// Auth routes
router.get('/login', adminAuthController.getAdminLogin);
router.post('/login', adminAuthController.postAdminLogin);
router.post('/logout', adminAuthController.adminLogout);

// Protected admin routes
router.get('/', adminAuthController.getAdminLogin);   
router.get('/dashboard', adminAuthController.isAdmin, adminDashboardController.getAdminDashboard);
router.delete('/users/:id', adminAuthController.isAdmin, adminDashboardController.removeUser);
router.get('/users', adminAuthController.isAdmin, adminDashboardController.listUsers);

module.exports = router;