CREATE DATABASE IF NOT EXISTS resume_parser;
USE resume_parser;

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    role_id INT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY UNIQUE,
    username VARCHAR(255) NOT NULL ,
    password VARCHAR(255) NOT NULL,
    role_id INT DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE user_sessions (
    session_token VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,  -- NOT TIMESTAMP
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);
drop table user_sessions;
SELECT @@global.time_zone, @@session.time_zone;
SET time_zone = '+00:00';
-- Insert default roles
INSERT INTO roles (role_id, role_name) VALUES 
(1, 'user'), 
(2, 'admin'); 

select* from user_sessions,