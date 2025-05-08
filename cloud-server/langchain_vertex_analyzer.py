"""
langchain_vertex_analyzer.py - Module for analyzing text using LangChain with Vertex AI.
"""

import os
import logging
from typing import Dict, Any

# Google Cloud imports
import vertexai
from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate

# Import the existing detector
from language_detector import LanguageDetector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LangChainTextAnalyzer:
    """
    A class that uses LangChain with Vertex AI to analyze text
    """

    def __init__(self):
        """
        Initialize the analyzer with LangChain and Vertex AI.
        """
        try:
            # Set project configuration
            project_id = "external-server-api"
            location = "us-central1"
            model_name = "gemini-2.0-flash"

            # Set credentials path if exists
            credentials_path = os.path.join(os.path.dirname(__file__),
                                            "external-server-api-e694880b1376.json")
            if os.path.exists(credentials_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                logger.info(f"Using credentials from: {credentials_path}")
            # Initialize Vertex AI
            vertexai.init(project=project_id, location=location)
            logger.info(f"Initialized Vertex AI with project: {project_id}, location: {location}")

            # Initialize LangChain's Vertex AI model
            self.llm = VertexAI(model_name="gemini-2.0-flash")
            logger.info(f"Created LangChain VertexAI model: {model_name}")

            # Initialize the language detector for keyboard layout conversion
            self.detector = LanguageDetector()

            # Create analysis prompt template
            self.analysis_prompt_template = PromptTemplate(
                input_variables=["original_text", "converted_text"],
                template="""
                You are a strict language assistant.  
                You receive two versions of a sentence:
                
                Sentence 1: {original_text}  
                Sentence 2: {converted_text}
                
                Important notes:
                - One of them was typed in the wrong keyboard layout and was already converted.
                - You do NOT need to detect or fix keyboard layout issues – they are already handled.
                
                Your task:
                1. Choose the sentence that is more correct and meaningful in **its own original language** (Hebrew or English).
                2. Correct only **spelling and grammar** mistakes in that sentence, without changing the language.
                3. Do **not** translate between Hebrew and English.
                4. Do **not** change the sentence structure or improve the writing.
                5. Do **not** guess or invent meaning.
                6. Do **not** add, remove, merge, or split any words.
                7. For any word that is clearly incorrect or in the wrong language/layout in the chosen sentence, and cannot be corrected directly – copy the word from the same position in the other sentence and use it as-is. Replace only that word, without changing sentence structure or meaning.

                Return your response in the following format:
                CORRECTED: [the corrected version of the preferred sentence, without spelling mistakes]
                """
            )

            # Create the LangChain using pipe operator
            self.chain = self.analysis_prompt_template | self.llm

            logger.info("LangChainTextAnalyzer successfully initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LangChainTextAnalyzer: {str(e)}")
            raise

    def analyze_and_correct_text(self, text: str) -> Dict[str, Any]:
        """
        Complete text analysis and correction pipeline.

        Args:
            text: The text to analyze and correct

        Returns:
            A dictionary with the corrected text and analysis results
        """
        if not text:
            logger.warning("Empty text provided for analysis")
            return {
                "corrected_text": text,
                "reasoning": "Empty text provided"
            }

        try:
            # Step 1: Convert the text using the existing detector
            converted_text = self.detector.convert_last_language(text)
            logger.debug(f"Original text: '{text}', Converted text: '{converted_text}'")

            # Step 2: Use LangChain to analyze and correct the text
            logger.info("Sending texts to Vertex AI for analysis")
            response = self.chain.invoke(input={
                "original_text": text,
                "converted_text": converted_text
            })

            response_text = response
            logger.debug(f"Raw response from Vertex AI: {response_text}")

            if "CORRECTED:" in response_text:
                corrected_start = response_text.find("CORRECTED:") + len("CORRECTED:")
                corrected_text = response_text[corrected_start:].strip()
            else:
                # Fallback to original text if no correction found
                corrected_text = text

            # def is_hebrew(text):
            #     return any('\u0590' <= c <= '\u05FF' for c in text)
            #
            # if is_hebrew(corrected_text):
            #     corrected_text = corrected_text[::-1]

            return {
                "corrected_text": corrected_text,
            }

        except Exception as e:
            logger.error(f"Error in text analysis: {str(e)}")
            # Fallback to original text in case of error
            return {
                "corrected_text": text,
                "reasoning": f"Error during analysis: {str(e)}"
            }

    def is_available(self) -> bool:
        """
        Check if the LangChain with Vertex AI is available and working.

        Returns:
            True if the API is available, False otherwise
        """
        try:
            logger.info("Testing Vertex AI availability")
            test_response = self.llm.invoke("Hello, are you available? Please respond with 'yes' only.")
            is_available = "yes" in test_response.lower()
            logger.info(f"Vertex AI availability test result: {is_available}")
            return is_available
        except Exception as e:
            logger.error(f"Vertex AI not available: {str(e)}")
            return False


# For testing outside of the web server
if __name__ == "__main__":
    # Set up logging for direct execution
    logging.basicConfig(level=logging.INFO)

    # Example usage
    analyzer = LangChainTextAnalyzer()

    # Test with a Hebrew text typed with English keyboard
    test_text = "יןן ים' רק טםו?"  # "שלום" typed with English keyboard
    result = analyzer.analyze_and_correct_text(test_text)

    print(f"Original text: {test_text}")
    print(f"Corrected text: {result['corrected_text']}")
    if 'reasoning' in result:
        print(f"Reasoning: {result['reasoning']}")