-- LearnCrafter MVP Database Schema
-- Supabase PostgreSQL Schema

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Status enum
CREATE TYPE entity_status AS ENUM ('active', 'inactive', 'draft');

-- Course Topics enum
CREATE TYPE course_topic AS ENUM (
    'computer-science',
    'mathematics',
    'physics',
    'chemistry',
    'biology',
    'programming',
    'data-science',
    'machine-learning',
    'intraday-trading',
    'calculus',
    'metallurgy'
);

-- Course Levels enum
CREATE TYPE course_level AS ENUM ('beginner', 'intermediate', 'advanced');

-- Prompts Table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    template TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

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

-- Seed Prompts
INSERT INTO prompts (prompt_id, name, description, template) VALUES
('concept_generation', 'Concept Content Generation', 'Generates the initial HTML content for a single educational concept.', '# Educational Concept Content Generation

You are an expert educational content creator specializing in interactive HTML pages. Your task is to create engaging, educational content that teaches concepts effectively.

## Concept Information
- **Title**: {title}
- **Description**: {description}
- **Learning Objectives**: {objectives}
- **Prerequisites**: {prerequisites}
- **Module Context**: {module_context}
- **Course Level**: {level}

## Requirements

Create a complete, standalone HTML page with the following requirements:

### 1. Structure
- Complete HTML5 document with proper DOCTYPE, head, and body sections
- Semantic HTML5 elements for accessibility

### 2. Content
- Clear, engaging explanation of the concept with examples
- Step-by-step instructions where appropriate
- Real-world examples and analogies

### 3. Interactivity
- Embedded JavaScript for interactive elements
- Form validation and user feedback
- Interactive exercises or demonstrations

### 4. Visualization
- One interactive chart using Chart.js (include CDN link)
- Visual aids and diagrams where helpful

### 5. Assessment
- A 3-question quiz with immediate feedback
- Progress tracking indicators

### 6. Code Examples
- Syntax-highlighted code snippets
- Working examples that users can interact with

### 7. Styling
- Modern, responsive CSS using flexbox/grid
- Mobile-friendly design
- Professional appearance

## Technical Requirements

### CDN Resources
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### CSS Features
- CSS Grid and Flexbox for layout
- CSS Variables for theming
- Responsive design breakpoints

### JavaScript Features
- Modern ES6+ syntax
- Error handling and validation
- Accessibility features (ARIA labels, keyboard navigation)

### Level-Specific Instructions

#### Beginner Level
- Use simple, clear language with step-by-step explanations
- Include basic examples and visual aids
- Focus on fundamental concepts and building blocks
- Provide plenty of context and background information
- Use analogies and real-world examples

#### Intermediate Level
- Include more complex examples and practical applications
- Discuss trade-offs, considerations, and best practices
- Add code snippets with explanations
- Include interactive exercises and challenges
- Cover multiple approaches to solving problems

#### Advanced Level
- Include advanced concepts, techniques, and patterns
- Add performance considerations and optimization strategies
- Discuss real-world applications and case studies
- Include challenging exercises and problem-solving scenarios
- Cover edge cases and advanced use cases

## Output Format

Return ONLY the complete HTML file with all CSS and JavaScript embedded. Do not include any explanations outside the HTML structure.

The content should be educational, engaging, and immediately usable by learners.
'),
('concept_regeneration', 'Concept Content Regeneration', 'Regenerates concept content based on feedback.', '# Concept Content Regeneration

Please regenerate the content for "{concept_title}" with improvements.

## Current Content
{current_content}

## Feedback for Improvement
{feedback}

## Improvement Requirements

1. **Address Feedback**: Incorporate any specific feedback provided
2. **Enhance Learning Experience**: Improve clarity, engagement, and educational value
3. **Code Quality**: Ensure all code is functional, well-commented, and follows best practices
4. **Interactivity**: Add or improve interactive elements where beneficial
5. **Accuracy**: Verify all content is accurate and up-to-date
6. **User Engagement**: Optimize for better learner engagement and retention

## Technical Improvements

### Content Structure
- Maintain proper HTML5 structure
- Ensure semantic markup for accessibility
- Keep responsive design principles

### Interactive Elements
- Verify all JavaScript functionality
- Ensure form validation works correctly
- Test interactive components

### Visual Design
- Maintain consistent styling
- Ensure mobile responsiveness
- Optimize for readability

### Educational Value
- Clarify complex concepts
- Add more examples where needed
- Improve assessment questions

## Output Format

Return ONLY the complete, improved HTML file with all CSS and JavaScript embedded. The new version should address the feedback while maintaining the same educational structure and improving overall quality.
'),
('content_validation', 'Content Validation', 'Validates generated content for quality and correctness.', '# Content Validation

Please validate this educational content for quality and effectiveness.

## Content to Validate
{content}

## Validation Criteria

### 1. Educational Value and Clarity
- Is the content clear and easy to understand?
- Are learning objectives met?
- Is the difficulty level appropriate?
- Are examples relevant and helpful?

### 2. Technical Correctness and Accuracy
- Is all information accurate and up-to-date?
- Are code examples functional and correct?
- Are technical concepts explained properly?
- Are there any factual errors?

### 3. Interactive Functionality
- Do all interactive elements work correctly?
- Is JavaScript code functional and error-free?
- Are forms and inputs properly validated?
- Do charts and visualizations display correctly?

### 4. Accessibility and Usability
- Is the content accessible to users with disabilities?
- Is the navigation intuitive?
- Is the design responsive and mobile-friendly?
- Are there any usability issues?

### 5. Code Quality and Best Practices
- Is HTML properly structured and semantic?
- Is CSS well-organized and maintainable?
- Is JavaScript code clean and efficient?
- Are there any security vulnerabilities?

### 6. User Engagement Potential
- Is the content engaging and interesting?
- Are there sufficient interactive elements?
- Is the pacing appropriate?
- Will learners stay motivated?

## Validation Report

Please provide specific feedback on:
- **Strengths**: What works well
- **Issues**: Any problems or concerns
- **Suggestions**: Recommendations for improvement
- **Overall Assessment**: Pass/Fail with reasoning
');

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