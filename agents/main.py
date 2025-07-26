import argparse
import requests
import logging
import json
import asyncio

from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .agent_prompts import COURSE_PLANNER_PROMPT, CONCEPT_DETAIL_PROMPT
from .llm_service import LLMService
from .config import settings


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Course Creation Agent for LearnCrafter MVP")
    parser.add_argument("--topic", type=str, required=True, help="High-level topic for the course")
    parser.add_argument("--level", type=str, default="beginner", choices=["beginner", "intermediate", "advanced"], help="Difficulty level of the course")
    parser.add_argument("--num-modules", type=int, default=3, help="Number of modules to create")
    parser.add_argument("--concepts-per-module", type=int, default=5, help="Number of concepts per module")
    return parser.parse_args()


class LearnCrafterAPI:
    """A client for the LearnCrafter API."""
    def __init__(self, base_url):
        self.base_url = base_url

    def _get(self, endpoint):
        """Helper method for making GET requests."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            logging.info(f"GET request to {url} successful.")
            logging.debug(f"Response: {json.dumps(data, indent=2)}")
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"API request to {url} failed: {e}")
            return None

    def _post(self, endpoint, data):
        """Helper method for making POST requests."""
        url = f"{self.base_url}/api/v1{endpoint}"
        try:
            logging.debug(f"Making POST request to {url} with data: {json.dumps(data, indent=2)}")
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logging.error(f"API request to {url} failed with status {e.response.status_code}: {e}")
            try:
                logging.error(f"Response body: {e.response.json()}")
            except json.JSONDecodeError:
                logging.error(f"Response body (non-JSON): {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"API request to {url} failed: {e}")
            if e.response:
                logging.error(f"Response body: {e.response.text}")
            else:
                logging.error("No response received from server.")
            return None

    def get_available_topics(self):
        """Fetches the list of available topics."""
        return self._get("/topics")

    def create_course(self, title, description, topic, level):
        """Creates a new course."""
        data = {"title": title, "description": description, "topic": topic, "level": level}
        return self._post("/courses/", data)

    def create_module(self, course_id, title, description, order_index):
        """Creates a new module."""
        data = {"course_id": course_id, "title": title, "description": description, "order_index": order_index}
        return self._post("/modules/", data)

    def create_concept(self, module_id, title, description, order_index, learning_objectives, prerequisites):
        """Creates a new concept."""
        
        # Truncate learning objectives to a maximum of 100 characters
        truncated_objectives = [obj[:100] for obj in learning_objectives]

        data = {
            "module_id": module_id,
            "title": title,
            "description": description,
            "order_index": order_index,
            "learning_objectives": truncated_objectives,
            "prerequisites": prerequisites
        }
        return self._post("/concepts/", data)


async def get_course_plan(llm_service, topic, level, num_modules):
    """Gets a high-level course plan from the LLM."""
    logging.info("🧠 Generating course plan from LLM...")
    prompt = COURSE_PLANNER_PROMPT.format(
        topic=topic,
        level=level,
        num_modules=num_modules
    )
    try:
        plan = await llm_service.refine_prompt(prompt)
        return plan
    except Exception as e:
        logging.error(f"Failed to get course plan from LLM: {e}")
        return None


async def get_concept_details(llm_service, topic, module_title, num_concepts):
    """Gets detailed concept plans for a module from the LLM."""
    logging.info(f"🧠 Generating concept details for module: [bold]{module_title}[/bold]...")
    prompt = CONCEPT_DETAIL_PROMPT.format(
        topic=topic,
        module_title=module_title,
        num_concepts=num_concepts
    )
    try:
        details = await llm_service.refine_prompt(prompt)
        return details
    except Exception as e:
        logging.error(f"Failed to get concept details from LLM: {e}")
        return None


async def main():
    """Main function for the course creation agent."""
    console = Console()
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
    )

    console.print(Panel(Text("🚀 Course Creation Agent Started 🚀", justify="center", style="bold white"), 
                        title="[bold blue]LearnCrafter[/bold blue]", 
                        border_style="blue"))

    args = parse_arguments()
    logging.info(f"▶️ Agent configured with arguments: [bold cyan]{args.topic}[/bold cyan] | Level: [bold cyan]{args.level}[/bold cyan] | Modules: [bold cyan]{args.num_modules}[/bold cyan]")

    api_client = LearnCrafterAPI(settings.host)
    llm_service = LLMService()

    logging.info("🔍 [bold]Step 1: Validating Topic[/bold]")
    logging.info(f"Checking for topic '{args.topic}' with the LearnCrafter API...")
    topics_response = api_client.get_available_topics()
    if topics_response is None or 'topics' not in topics_response:
        logging.error("❌ Could not fetch or parse available topics from the API. Exiting.")
        return

    available_topic_values = [topic['value'] for topic in topics_response.get('topics', [])]
    if args.topic not in available_topic_values:
        logging.error(f"❌ Topic '{args.topic}' is not supported by the LearnCrafter API.")
        logging.error(f"Please choose from the following topics: {', '.join(available_topic_values)}")
        return
    logging.info(f"✅ Topic '[bold green]{args.topic}[/bold green]' is valid.")

    logging.info("📚 [bold]Step 2: Generating Course Plan[/bold]")
    course_plan = await get_course_plan(llm_service, args.topic, args.level, args.num_modules)
    if not course_plan:
        logging.error("❌ Could not generate a course plan. Exiting.")
    else:
        logging.info("✅ Successfully generated course plan.")
        console.print(Panel(f"[bold]Title:[/bold] {course_plan['course_title']}\n[bold]Description:[/bold] {course_plan['course_description']}", 
                              title="[bold green]Course Details[/bold green]", 
                              border_style="green"))

        logging.info("📝 [bold]Step 3: Creating Course in LearnCrafter[/bold]")
        course_data = api_client.create_course(
            title=course_plan['course_title'],
            description=course_plan['course_description'],
            topic=args.topic,
            level=args.level
        )

        if not course_data:
            logging.error("❌ Failed to create the course. Exiting.")
        else:
            course_id = course_data['id']
            logging.info(f"✅ Course created successfully! [bold]ID: {course_id}[/bold]")

            logging.info("🧩 [bold]Step 4: Creating Modules and Concepts[/bold]")
            for i, module_plan in enumerate(course_plan['module_plans']):
                module_order_index = i + 1
                logging.info(f"  ➡️ [bold]Creating Module {module_order_index}:[/bold] [cyan]{module_plan['module_title']}[/cyan]")
                module_data = api_client.create_module(
                    course_id=course_id,
                    title=module_plan['module_title'],
                    description=module_plan['module_description'],
                    order_index=module_order_index
                )

                if not module_data:
                    logging.warning(f"  ⚠️ Skipping module due to creation failure: {module_plan['module_title']}")
                    continue

                module_id = module_data['id']
                logging.info(f"  ✅ Module created! [bold]ID: {module_id}[/bold]")

                concept_details = await get_concept_details(
                    llm_service,
                    topic=args.topic,
                    module_title=module_plan['module_title'],
                    num_concepts=args.concepts_per_module
                )

                if concept_details and 'concepts' in concept_details:
                    logging.info(f"    🧠 Generating concepts for '[bold]{module_plan['module_title']}[/bold]'...")
                    for j, concept in enumerate(concept_details['concepts']):
                        concept_order_index = j + 1
                        logging.info(f"      - [bold]Creating Concept {concept_order_index}:[/bold] {concept['concept_title']}")
                        concept_data = api_client.create_concept(
                            module_id=module_id,
                            title=concept['concept_title'],
                            description=concept['concept_description'],
                            order_index=concept_order_index,
                            learning_objectives=concept['learning_objectives'],
                            prerequisites=concept['prerequisites']
                        )
                        if concept_data:
                            logging.info(f"      ✅ Concept created! [bold]ID: {concept_data['id']}[/bold]")
                        else:
                            logging.warning(f"      ⚠️ Failed to create concept: {concept['concept_title']}")
                else:
                    logging.warning(f"  ⚠️ Could not generate concept details for module: {module_plan['module_title']}")

    logging.info("🎉 [bold green]Course Creation Agent Finished[/bold green] 🎉")


if __name__ == "__main__":
    asyncio.run(main()) 