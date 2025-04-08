const express = require('express');
const mysql = require('mysql2');
const axios = require('axios');
const session = require('express-session');
const config = require('./config');
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(session({
    secret: config.session.secret,
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false }
}));

const db = mysql.createPool(config.mysql);

const waitForDb = async (maxAttempts = 30, delay = 2000) => {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const connection = await db.promise().getConnection();
            connection.release();
            console.log('Successfully connected to database');
            return;
        } catch (err) {
            console.log(`Database connection attempt ${attempt} failed. Retrying in ${delay/1000} seconds...`);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
    throw new Error('Could not connect to database after multiple attempts');
};

const initDb = async () => {
    try {
        await db.promise().query(`
            CREATE TABLE IF NOT EXISTS data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                value FLOAT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);
        console.log('Database initialized successfully');
    } catch (err) {
        console.error('Error initializing database:', err);
        throw err;
    }
};

const loginRequired = (req, res, next) => {
    if (!req.session.token) {
        return res.redirect('/login');
    }
    next();
};

app.get('/', (req, res) => {
    res.redirect('/login');
});

app.get('/login', (req, res) => {
    res.render('login', { error: null });
});

app.post('/login', async (req, res) => {
    try {
        const response = await axios.post(`${config.auth.url}/login`, {
            username: req.body.username,
            password: req.body.password
        });
        
        if (response.status === 200 && response.data.token) {
            req.session.token = response.data.token;
            res.redirect('/data_entry');
        } else {
            res.render('login', { error: 'Invalid response from authentication service' });
        }
    } catch (err) {
        console.error('Login error:', err.message);
        res.render('login', { 
            error: err.response?.data?.message || 'Invalid credentials'
        });
    }
});

app.get('/data_entry', loginRequired, (req, res) => {
    res.render('data_entry', { message: null });
});

app.post('/data_entry', loginRequired, async (req, res) => {
    const value = parseFloat(req.body.value);
    
    if (isNaN(value)) {
        return res.render('data_entry', { 
            message: 'Please enter a valid number' 
        });
    }

    try {
        await db.promise().query(
            'INSERT INTO data (value) VALUES (?)',
            [value]
        );

        const [results] = await db.promise().query(
            'SELECT * FROM data ORDER BY id DESC LIMIT 1'
        );
        console.log('Last inserted entry:', results[0]);

        res.redirect('/data_entry');
    } catch (err) {
        console.error('Error inserting data:', err);
        res.render('data_entry', { 
            message: 'Error saving data. Please try again.' 
        });
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).render('error', { 
        message: 'Something went wrong!' 
    });
});

const PORT = process.env.PORT || 5001;

const startServer = async () => {
    try {
        console.log('Waiting for database connection...');
        await waitForDb();
        await initDb();
        app.listen(PORT, '0.0.0.0', () => {
            console.log(`Data Entry Service running on port ${PORT}`);
        });
    } catch (err) {
        console.error('Failed to start server:', err);
        process.exit(1);
    }
};

startServer();

module.exports = app;