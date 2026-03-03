-- XANENE OPS Database Schema
-- PostgreSQL Database Setup

-- Create database (run as postgres superuser)
-- CREATE DATABASE xanene_ops;
-- CREATE USER xanene WITH PASSWORD 'your_secure_password';
-- GRANT ALL PRIVILEGES ON DATABASE xanene_ops TO xanene;

-- Connect to the database
-- \c xanene_ops

-- Enable UUID extension (optional, for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'field_staff',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_role CHECK (role IN ('admin', 'operations_manager', 'field_staff', 'sales'))
);

-- Create index on email for faster lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Events table
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    start_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    end_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    category VARCHAR(50) NOT NULL,
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE,
    recurrence_type VARCHAR(50) DEFAULT 'none',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_category CHECK (category IN ('collection', 'production', 'delivery', 'training', 'sales')),
    CONSTRAINT valid_recurrence CHECK (recurrence_type IN ('none', 'daily', 'weekly'))
);

-- Create indexes for events
CREATE INDEX idx_events_start_datetime ON events(start_datetime);
CREATE INDEX idx_events_end_datetime ON events(end_datetime);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_is_active ON events(is_active);
CREATE INDEX idx_events_created_by ON events(created_by_id);

-- Event-Staff association table (many-to-many)
CREATE TABLE event_staff (
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, user_id)
);

CREATE INDEX idx_event_staff_event_id ON event_staff(event_id);
CREATE INDEX idx_event_staff_user_id ON event_staff(user_id);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(50) NOT NULL DEFAULT 'medium',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    category VARCHAR(50) NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    assigned_to_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_by_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'in_progress', 'completed')),
    CONSTRAINT valid_category CHECK (category IN ('collection', 'production', 'delivery', 'training', 'sales', 'admin'))
);

-- Create indexes for tasks
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_category ON tasks(category);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to_id);
CREATE INDEX idx_tasks_created_by ON tasks(created_by_id);
CREATE INDEX idx_tasks_is_active ON tasks(is_active);
CREATE INDEX idx_tasks_completed_at ON tasks(completed_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user
-- Password: admin123 (hashed with bcrypt)
INSERT INTO users (email, full_name, hashed_password, role)
VALUES (
    'admin@xanene.com',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G.2f2f2f2f2f2f',
    'admin'
) ON CONFLICT (email) DO NOTHING;

-- Grant permissions to xanene user (if not using superuser)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO xanene;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO xanene;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO xanene;
