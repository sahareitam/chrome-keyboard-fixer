"""
langchain_vertex_analyzer.py - Module for analyzing text using LangChain with Vertex AI.
"""

import os
import logging
import time
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

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
            # Set project configuration from environment variables with fallbacks
            project_id = os.getenv("PROJECT_ID", "project-id-placeholder")
            location = os.getenv("REGION", "us-central1")
            model_name = os.getenv("MODEL_NAME", "gemini-2.0-flash")

            # Detect if running in GCP environment
            is_gcp_environment = os.getenv("GAE_ENV", "").startswith("standard") or \
                               os.getenv("K_SERVICE", "") or \
                               os.getenv("FUNCTION_NAME", "")

            logger.info(f"Environment detection: Running in {'GCP' if is_gcp_environment else 'local'} environment")

            # Credentials handling based on environment
            if is_gcp_environment:
                # In GCP, the service will use the attached service account automatically
                logger.info("Using default GCP credentials")
            else:
                # Local development - use explicit credentials file
                credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if credentials_path and os.path.exists(credentials_path):
                    logger.info("Using credentials from environment variable")
                else:
                    logger.warning("No credentials found - service may fail")

            # Initialize Vertex AI with proper error handling
            try:
                vertexai.init(project=project_id, location=location)
                logger.info(f"Initialized Vertex AI with project ID and location: {location}")
            except Exception as vertex_init_error:
                logger.error(f"Failed to initialize Vertex AI: {str(vertex_init_error)}")
                raise

            # Initialize LangChain's Vertex AI model with retries
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    self.llm = VertexAI(model_name=model_name)
                    logger.info(f"Created LangChain VertexAI model: {model_name}")
                    break
                except Exception as model_init_error:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"Failed to initialize Vertex AI model after {max_retries} attempts: {str(model_init_error)}")
                        raise
                    logger.warning(f"Retry {retry_count}/{max_retries} initializing model: {str(model_init_error)}")
                    time.sleep(1)  # Short delay before retry

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
        Complete text analysis and correction pipeline with improved error handling for GCP.
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
            logger.debug("Text processing completed successfully")

            # Step 2: Use LangChain with retry logic for API calls
            max_retries = 3
            retry_count = 0
            response_text = None

            while retry_count < max_retries:
                try:
                    logger.info(f"Attempt {retry_count+1}/{max_retries}: Sending texts to Vertex AI for analysis")

                    # Add timeout handling for GCP environment
                    response = self.chain.invoke(input={
                        "original_text": text,
                        "converted_text": converted_text
                    })

                    response_text = response
                    logger.debug(f"Raw response from Vertex AI: {response_text}")
                    break  # Success - exit retry loop

                except Exception as api_error:
                    retry_count += 1
                    logger.warning(f"API call failed (attempt {retry_count}/{max_retries}): {str(api_error)}")

                    if retry_count >= max_retries:
                        logger.error(f"All retries failed for Vertex AI analysis")
                        # Fallback to original text after all retries fail
                        return {
                            "corrected_text": text,
                            "reasoning": f"API error after {max_retries} attempts: {str(api_error)}"
                        }

                    # Exponential backoff before retry
                    time.sleep(2 ** retry_count)  # 2, 4, 8 seconds

            # Process the response if we got one
            if response_text and "CORRECTED:" in response_text:
                corrected_start = response_text.find("CORRECTED:") + len("CORRECTED:")
                corrected_text = response_text[corrected_start:].strip()
            else:
                # Fallback to original text if no correction found
                corrected_text = text

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

    def translate_with_vertex(self, text: str) -> str:
        """
        Translate text between Hebrew and English using Vertex AI with improved error handling for GCP.
        """
        if not text:
            logger.warning("Empty text provided for translation")
            return text

        try:
            # Detect text language using existing detector
            hebrew_chars = 0
            english_chars = 0

            for char in text:
                lang = self.detector.detect_character_language(char)
                if lang == "hebrew":
                    hebrew_chars += 1
                elif lang == "english":
                    english_chars += 1

            # Determine translation direction based on analysis
            if hebrew_chars > english_chars:
                target_language = "English"
                source_language = "Hebrew"
            else:
                target_language = "Hebrew"
                source_language = "English"

            translation_prompt = f"""
            ROLE: You are a strict, rule-based translation engine.

            TASK: Correct spelling, grammar and punctuation errors in the input text, then translate the corrected text from {source_language} to {target_language}.

            RESTRICTIONS:
            1. DO NOT add comments, explanations or metadata.
            2. DO NOT repeat the input text in its original language.
            3. DO NOT identify the language.
            4. DO NOT include labels, titles or surrounding text.
            5. DO NOT expand, omit or alter content beyond minimal corrections.
            6. Preserve meaning, tone and all original formatting (bold, italics, lists, inline code).
            7. Output plain text only – no markdown, quotes or code fences.

            OUTPUT: The corrected and translated text only.

            INPUT TEXT:
            {text}
            """

            # Add retry logic for GCP environment
            max_retries = 3
            retry_count = 0
            translated_text = None

            while retry_count < max_retries:
                try:
                    logger.info(f"Attempt {retry_count+1}/{max_retries}: Sending text to Vertex AI for translation")
                    response = self.llm.invoke(translation_prompt)

                    # Clean up the response
                    translated_text = response.strip()
                    break  # Success - exit retry loop

                except Exception as api_error:
                    retry_count += 1
                    logger.warning(f"Translation API call failed (attempt {retry_count}/{max_retries}): {str(api_error)}")

                    if retry_count >= max_retries:
                        logger.error(f"All retries failed for translation")
                        # Return original text if all retries fail
                        return text

                    # Exponential backoff
                    time.sleep(2 ** retry_count)

            return translated_text if translated_text else text

        except Exception as e:
            logger.error(f"Error in text translation: {str(e)}")
            # Return the original text in case of error
            return text

    def rephrase_to_prompt(self, text: str) -> str:
        """
        Rephrase text into a well-structured AI prompt

        Args:
            text: Original text to rephrase

        Returns:
            Rephrased text as a ready-to-use prompt
        """
        if not text:
            logger.warning("Empty text provided for rephrasing")
            return text

        try:
            # Create rephrasing prompt
            rephrasing_prompt = f"""
            You are “PromptRefiner”, a senior cross-LLM prompt engineer.
            USER INPUT (original prompt to improve):

            \"\"\"{text}\"\"\" 
            

            OBJECTIVE:
            Rewrite the user input so that GPT-4-class or Claude-3-class models produce the most accurate, complete, and context-aware answer.

            INSTRUCTIONS
            Keep the rewritten prompt in the exact same language used in the original text.
            
            1. Preserve the original intent, but clarify goals, desired depth, and target audience.
            2. Add any missing context or constraints that help the target model:  
               - tone, answer format, length limit, domain perspective, examples, step-by-step reasoning, citation style, verification requests.
            3. Eliminate ambiguity, filler, and duplicate ideas; keep language formal and professional unless instructed otherwise.
            4. Do not mention these guidelines, your role, or any meta-text in the final result.
            5. Output only the improved prompt, plain text, no labels, no commentary, no code fencing.
            
            
            END OF INSTRUCTIONS
            """

            # Send prompt to Vertex AI
            logger.info("Sending text to Vertex AI for rephrasing to prompt")
            response = self.llm.invoke(rephrasing_prompt)

            # Clean response
            rephrased_text = response.strip()
            logger.debug(f"Original text: '{text}', Rephrased prompt: '{rephrased_text}'")

            return rephrased_text

        except Exception as e:
            logger.error(f"Error in text rephrasing: {str(e)}")
            # In case of error, return original text
            return text

    def is_available(self) -> bool:
        """
        Check if the LangChain with Vertex AI is available and working.
        Enhanced for GCP environment with retries.
        """
        max_retries = 2
        retry_count = 0

        while retry_count < max_retries:
            try:
                logger.info(f"Attempt {retry_count+1}/{max_retries}: Testing Vertex AI availability")
                test_response = self.llm.invoke("Hello, are you available? Please respond with 'yes' only.")
                is_available = "yes" in test_response.lower()
                logger.info(f"Vertex AI availability test result: {is_available}")
                return is_available

            except Exception as e:
                retry_count += 1
                logger.warning(f"Availability check failed (attempt {retry_count}/{max_retries}): {str(e)}")

                if retry_count >= max_retries:
                    logger.error(f"All availability check retries failed: {str(e)}")
                    return False

                # Short delay before retry
                time.sleep(2)

        return False  # Ensure we always return a boolean




# For testing outside of the web server
if __name__ == "__main__":
    # Set up logging for direct execution
    logging.basicConfig(level=logging.INFO)

    # Example usage
    analyzer = LangChainTextAnalyzer()

    # Test with a Hebrew text typed with English keyboard
    test_text = "יןן ים' רק טםו?"  # "שלום" typed with English keyboard
    result = analyzer.analyze_and_correct_text(test_text)
    test_text2 = "היי מה קורה הכל בסדר?? איך אתה? רוצה ללכת איתי לים ?"
    result2 = analyzer.translate_with_vertex(test_text2)
    test_text3 = "יש לי מבחן בתקשורת נתונים אשמח שתסביר לי איך אני צריך להתכונן אליו"
    result3 = analyzer.rephrase_to_prompt(test_text3)

    print(f"Original text: {test_text}")
    print(f"Corrected text: {result['corrected_text']}")
    print(f"Translated text: {result2}")
    print(f"prompt text: {result3}")

    if 'reasoning' in result:
        print(f"Reasoning: {result['reasoning']}")