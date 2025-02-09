-- Database setup
CREATE DATABASE IF NOT EXISTS resume_parser;
USE resume_parser;
-- drop database resume_parser;
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
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);
select *from users;
-- Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    session_token VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email) ON DELETE CASCADE
);

-- Main Analysis Table
CREATE TABLE IF NOT EXISTS resume_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    parsed_email VARCHAR(255),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	resume_score VARCHAR(255),  
    applied_profile VARCHAR(255),
    highest_education VARCHAR(255),
    professional_experience VARCHAR(255),  -- Changed to string
	linkedin VARCHAR(255),
	github VARCHAR(255),
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS phone_numbers (
    phone_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    phone_number VARCHAR(20),
    FOREIGN KEY (analysis_id) REFERENCES resume_analysis(analysis_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT NOT NULL,
    address TEXT,
    FOREIGN KEY (analysis_id) REFERENCES resume_analysis(analysis_id) ON DELETE CASCADE
);


UPDATE users
SET role_id = 2
WHERE email = 'agrani@gmail.com';
ALTER TABLE resume_analysis MODIFY COLUMN resume_score DECIMAL(5, 2);

select * from resume_analysis;
-- Related Tables (Education, Work, Contacts)
-- CREATE TABLE IF NOT EXISTS education_details (
--     education_id INT AUTO_INCREMENT PRIMARY KEY,
--     analysis_id INT NOT NULL,
--     university VARCHAR(255),
--     degree VARCHAR(255),
--     graduation_date VARCHAR(20),
--     FOREIGN KEY (analysis_id) REFERENCES resume_analysis(analysis_id) ON DELETE CASCADE
-- );
-- drop table education_details;

-- CREATE TABLE IF NOT EXISTS work_experience (
--     experience_id INT AUTO_INCREMENT PRIMARY KEY,
--     analysis_id INT NOT NULL,
--     company VARCHAR(255),
--     position VARCHAR(255),
--     start_date VARCHAR(20),
--     end_date VARCHAR(20),
--     FOREIGN KEY (analysis_id) REFERENCES resume_analysis(analysis_id) ON DELETE CASCADE
-- );
-- drop table work_experience;

-- select * from work_experience;

 select * from phone_numbers;

select* from  addresses;

-- Indexes
CREATE INDEX idx_resume_user ON resume_analysis(user_email);
