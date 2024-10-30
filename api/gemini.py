import os
from typing import List, Optional, Dict, Union
import google.generativeai as genai
from metrics import get_user_metrics
from flask import current_app
from google.generativeai.types import GenerateContentResponse


genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
model = genai.GenerativeModel("gemini-1.5-flash")


def get_prompt(metrics: Dict[str, any]) -> str:
    """
    Construct a prompt for the Gemini LLM API based on course metrics

    Args:
        metrics (Dict[str, any]): The course metrics for generating improvement ideas.

    Returns:
        str: The generated prompt for the model.
    """
    return ( # To change the prompt, just edit this returned string
        f"""Analyze the following course metrics and provide specific, actionable suggestions **for the subject coordinator and teaching staff** to improve course quality. 
           Focus only on areas where the metrics indicate room for improvement or non-compliance with best practices. 
           Present the suggestions in a concise, bullet-point format and ensure they are practical for **teachers and subject coordinators to implement**. 
           Avoid general commentary, personal pronouns, or addressing any QA personnel.
           Course Metrics:
           {metrics}
            Targeted Recommendations for Teaching Staff and Subject Coordinators:"""
    )


def get_course_improvement_ideas(email: str) -> Optional[List[str]]:
    """
    Fetches course improvement ideas using Google Generative AI based on the user's course metrics.

    Args:
        email (str): The email of the user for whom to fetch the metrics.

    Returns:
        Optional[List[str]]: A list of improvement ideas or None if there is an error.
    """
    try:
        if current_app:
            metrics: Dict[str, Union[str, bool]] = get_user_metrics(email)
        prompt: str = get_prompt(metrics)
        response: GenerateContentResponse = model.generate_content(prompt)
        # Extract and clean up the response
        ideas: List[str] = response.text.strip().split("\n")
        # Remove any numbering or bullet points
        ideas = [idea.lstrip("•-1234567890. ")
                 for idea in ideas if idea.strip()]
        
        current_app.logger.info("Generated improvement ideas:")
        for idea in ideas:
            current_app.logger.info(f"- {idea}")
        return ideas
    except RuntimeError as e:
        current_app.logger.log_exception(f"Issue querying Gemini API: {e}.")
        return None
