-- LearnCrafter MVP Database Schema
-- Supabase PostgreSQL Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Courses Table
CREATE TABLE courses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    topic VARCHAR(100) NOT NULL,
    level VARCHAR(50) DEFAULT 'beginner',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Modules Table
CREATE TABLE modules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(course_id, order_index)
);

-- Concepts Table
CREATE TABLE concepts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    learning_objectives TEXT[] DEFAULT '{}',
    prerequisites TEXT[] DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(module_id, order_index)
);

-- Indexes for Performance
CREATE INDEX idx_courses_topic ON courses(topic);
CREATE INDEX idx_courses_level ON courses(level);
CREATE INDEX idx_courses_status ON courses(status);
CREATE INDEX idx_courses_created_at ON courses(created_at DESC);

CREATE INDEX idx_modules_course_id ON modules(course_id);
CREATE INDEX idx_modules_order_index ON modules(order_index);
CREATE INDEX idx_modules_status ON modules(status);

CREATE INDEX idx_concepts_module_id ON concepts(module_id);
CREATE INDEX idx_concepts_order_index ON concepts(order_index);
CREATE INDEX idx_concepts_status ON concepts(status);

-- Composite indexes for efficient queries
CREATE INDEX idx_modules_course_order ON modules(course_id, order_index);
CREATE INDEX idx_concepts_module_order ON concepts(module_id, order_index);

-- Row Level Security (RLS) Policies
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE concepts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Courses
CREATE POLICY "Courses are viewable by everyone" ON courses
    FOR SELECT USING (true);

CREATE POLICY "Courses are insertable by authenticated users" ON courses
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Courses are updatable by authenticated users" ON courses
    FOR UPDATE USING (true);

CREATE POLICY "Courses are deletable by authenticated users" ON courses
    FOR DELETE USING (true);

-- RLS Policies for Modules
CREATE POLICY "Modules are viewable by everyone" ON modules
    FOR SELECT USING (true);

CREATE POLICY "Modules are insertable by authenticated users" ON modules
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Modules are updatable by authenticated users" ON modules
    FOR UPDATE USING (true);

CREATE POLICY "Modules are deletable by authenticated users" ON modules
    FOR DELETE USING (true);

-- RLS Policies for Concepts
CREATE POLICY "Concepts are viewable by everyone" ON concepts
    FOR SELECT USING (true);

CREATE POLICY "Concepts are insertable by authenticated users" ON concepts
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Concepts are updatable by authenticated users" ON concepts
    FOR UPDATE USING (true);

CREATE POLICY "Concepts are deletable by authenticated users" ON concepts
    FOR DELETE USING (true);

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_modules_updated_at BEFORE UPDATE ON modules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_concepts_updated_at BEFORE UPDATE ON concepts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing
INSERT INTO courses (title, description, topic, level) VALUES
('Data Structures & Algorithms', 'Comprehensive guide to DSA fundamentals', 'computer-science', 'intermediate'),
('Web Development Basics', 'Introduction to HTML, CSS, and JavaScript', 'programming', 'beginner'),
('Machine Learning Fundamentals', 'Core concepts of ML and AI', 'machine-learning', 'advanced');

-- Sample modules
INSERT INTO modules (course_id, title, description, order_index) VALUES
((SELECT id FROM courses WHERE title = 'Data Structures & Algorithms' LIMIT 1), 'Arrays and Lists', 'Fundamental linear data structures', 1),
((SELECT id FROM courses WHERE title = 'Data Structures & Algorithms' LIMIT 1), 'Trees and Graphs', 'Hierarchical and network data structures', 2),
((SELECT id FROM courses WHERE title = 'Web Development Basics' LIMIT 1), 'HTML Fundamentals', 'Structure and semantics', 1),
((SELECT id FROM courses WHERE title = 'Web Development Basics' LIMIT 1), 'CSS Styling', 'Layout and design principles', 2); 