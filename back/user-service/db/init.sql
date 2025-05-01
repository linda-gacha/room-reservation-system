-- Create role and database
CREATE ROLE meeting_user WITH LOGIN PASSWORD 'password';
CREATE DATABASE user_db;
GRANT ALL PRIVILEGES ON DATABASE user_db TO meeting_user;

-- Switch to the user_db database (This step might fail in Docker depending on context, but it's harmless)
\c user_db

-- Create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'employee', 'visitor')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE auth_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token VARCHAR(512) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions to the role
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO meeting_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO meeting_user;

-- Optionally, grant usage on schema
GRANT USAGE ON SCHEMA public TO meeting_user;

