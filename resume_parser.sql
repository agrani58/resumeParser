
-- DROP DATABASE IF EXISTS resume_parser;
CREATE DATABASE IF NOT EXISTS resume_parser;
USE resume_parser;

-- Roles Table
CREATE TABLE IF NOT EXISTS roles (
    role_id INT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);
INSERT INTO roles VALUES (1, 'user'), (2, 'admin');

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role_id INT DEFAULT 1,
    signup_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    subscription_type ENUM('free', 'premium') NOT NULL DEFAULT 'free',
    start_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);
ALTER TABLE subscriptions
ADD COLUMN end_date DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL 1 MONTH);

UPDATE subscriptions
SET is_active = FALSE
WHERE end_date < CURRENT_TIMESTAMP;
SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;
-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    session_token VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);

-- Main Resume Analysis Table
CREATE TABLE IF NOT EXISTS resume_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    parsed_email VARCHAR(255),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resume_score DECIMAL(5,2),
    applied_profile VARCHAR(255),
    highest_education VARCHAR(255),
    professional_experience VARCHAR(255),
    linkedin VARCHAR(255),
    github VARCHAR(255),
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);
select *from users;
-- Phone Numbers Table
CREATE TABLE IF NOT EXISTS phone_numbers (
    phone_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    phone_number VARCHAR(20),
    FOREIGN KEY (analysis_id) REFERENCES resume_analysis(analysis_id) ON DELETE CASCADE
);

-- Addresses Table
CREATE TABLE IF NOT EXISTS addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    address TEXT,
    FOREIGN KEY (analysis_id) REFERENCES resume_analysis(analysis_id) ON DELETE CASCADE
);

-- Skills Table
CREATE TABLE IF NOT EXISTS skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    skill_name VARCHAR(255) NOT NULL UNIQUE
);

-- Analysis Skills Table
CREATE TABLE IF NOT EXISTS analysis_skills (
    analysis_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (analysis_id, skill_id),
    FOREIGN KEY (analysis_id) REFERENCES resume_analysis(analysis_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
);


UPDATE users
SET signup_date = DATE_SUB(NOW(), INTERVAL 8 DAY)
WHERE email = 'f@f.com';

UPDATE subscriptions
SET end_date = DATE_SUB(NOW(), INTERVAL 1 DAY)
WHERE email = 'f@f.com';

delete from users
where email ="agrani@gmail.com";
delete from resume_analysis
where analysis_id = 21;
update users 
set role_id=2;
delete from users
where email="admin@gmail.com";
select * from users;
-- Indexes for Performance;
CREATE INDEX idx_user_email ON resume_analysis(user_email);