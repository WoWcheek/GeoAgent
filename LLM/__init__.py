from langchain_openai import ChatOpenAI as OpenAI
from langchain_anthropic import ChatAnthropic as Anthropic
from langchain_google_genai import ChatGoogleGenerativeAI as Gemini

LLM_type = OpenAI | Gemini | Anthropic

OPENAI_MODEL_NAME = "gpt-4o"
GEMINI_MODEL_NAME = "gemini-2.0-flash"
ANTHROPIC_MODEL_NAME = "claude-3-7-sonnet-20250219"

OPEN_AI_PROMPT_FILE = "LLM/prompt.txt"
GEMINI_PROMPT_FILE = "LLM/prompt.txt"
ANTHROPIC_PROMPT_FILE = "LLM/prompt.txt"

from .llm_guess import LlmGuess
from .llm_wrapper import LlmWrapper