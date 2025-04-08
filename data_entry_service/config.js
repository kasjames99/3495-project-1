require('dotenv').config();

module.exports = {
    mysql: {
        host: process.env.MYSQL_HOST || 'mysql',
        user: process.env.MYSQL_USER || 'app_user',
        password: process.env.MYSQL_PASSWORD || 'app_password',
        database: process.env.MYSQL_DATABASE || 'data_entry_db'
    },
    session: {
        secret: process.env.SECRET_KEY || 'your-secret-key'
    },
    auth: {
        url: process.env.AUTH_SERVICE_URL || 'http://auth-service'
    }
};