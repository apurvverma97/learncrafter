"""
Prompts for the Course Creation Agent.
"""

COURSE_PLANNER_PROMPT = """
You are a master instructional designer. Your task is to create a high-level plan for an educational course.

**Course Topic:** {topic}
**Difficulty Level:** {level}
**Number of Modules:** {num_modules}

Please generate a JSON object with the following structure:
- "course_title": A compelling title for the course.
- "course_description": A brief, engaging description of the course.
- "module_plans": A list of {num_modules} module plans. Each plan should be a JSON object with:
  - "module_title": A clear and descriptive title for the module.
  - "module_description": A short summary of what the module will cover.

Ensure the final output is a single, valid JSON object.
"""

CONCEPT_DETAIL_PROMPT = """
You are an expert curriculum developer. Your task is to break down a module into a series of detailed concepts.

**Course Topic:** {topic}
**Module Title:** {module_title}
**Number of Concepts:** {num_concepts}

Please generate a JSON object with a single key, "concepts", which is a list of {num_concepts} concept plans. Each plan should be a JSON object with:
- "concept_title": A title for the concept.
- "concept_description": A brief description of the concept.
- "learning_objectives": A list of 3-5 specific learning objectives. Each objective must be a string of less than 100 characters.
- "prerequisites": A list of 1-3 prerequisite skills or knowledge.

Ensure the final output is a single, valid JSON object.
"""
