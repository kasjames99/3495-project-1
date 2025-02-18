require('dotenv').config();

module.exports = {
    mysql: {
        host: process.env.MYSQL_HOST || 'localhost',
        user: process.env.MYSQL_USER || 'root',
        password: process.env.MYSQL_PASSWORD || 'password',
        database: process.env.MYSQL_DATABASE || 'data_entry_db'
    },
    session: {
        secret: process.env.SECRET_KEY || 'your-secret-key'
    },
    auth: {
        url: process.env.AUTH_SERVICE_URL || 'http://auth_service:5000'
    }
};