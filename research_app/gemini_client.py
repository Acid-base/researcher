# Gemini Client
# Handles communication with the Google Gemini API (via LiteLLM or direct).

import os
import json
import logging
import litellm
from litellm import completion

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key=None):
        """
        Initialize the Gemini client with API key from environment variable or parameter
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("No Gemini API key provided. Set GEMINI_API_KEY environment variable or pass as parameter")

        # Configure litellm to use Gemini
        litellm.api_key = self.api_key

    def generate_report(self, context, prompt_template=None, max_tokens=4096):
        """
        Generate a research report using the Google Gemini API

        Args:
            context: List of retrieved documents with text and metadata
            prompt_template: Optional template for structuring the prompt
            max_tokens: Maximum tokens for the generated response

        Returns:
            Generated report and citation information
        """
        if not self.api_key:
            return {"error": "No API key provided for Gemini"}, []

        try:
            # Prepare the context from retrieved documents
            formatted_context = self._format_context(context)

            # Use default prompt template if none provided
            if not prompt_template:
                prompt_template = self._get_default_prompt_template()

            # Format the final prompt
            prompt = prompt_template.format(context=formatted_context)

            # Call Gemini API via LiteLLM
            response = completion(
                model="gemini-pro",  # Using Gemini Pro model
                messages=[
                    {"role": "system", "content": "You are a thorough research assistant that synthesizes information into comprehensive reports with accurate citations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more factual responses
            )

            # Extract report content from response
            report_content = response.choices[0].message.content

            # Prepare citation information from context
            citations = self._prepare_citations(context)

            return {"report": report_content}, citations

        except Exception as e:
            logger.error(f"Error generating report with Gemini: {str(e)}")
            return {"error": f"Failed to generate report: {str(e)}"}, []

    def _format_context(self, context):
        """
        Format the retrieved context for the prompt
        """
        formatted_texts = []

        for i, doc in enumerate(context):
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            source = metadata.get("url", f"Source {i+1}")

            formatted_text = f"Source [{i+1}] - {source}:\n{text}\n"
            formatted_texts.append(formatted_text)

        return "\n".join(formatted_texts)

    def _prepare_citations(self, context):
        """
        Prepare citation information from context
        """
        citations = []

        for i, doc in enumerate(context):
            metadata = doc.get("metadata", {})

            citation = {
                "id": i+1,
                "url": metadata.get("url", ""),
                "title": metadata.get("title", f"Source {i+1}"),
                "retrieval_date": metadata.get("retrieval_date", ""),
                "source_type": metadata.get("source_type", "unknown")
            }

            citations.append(citation)

        return citations

    def _get_default_prompt_template(self):
        """
        Return a default prompt template for research reports
        """
        return """
        Based on the following information sources, generate a comprehensive research report.
        Synthesize the information to provide an in-depth analysis of the topic.

        Focus on:
        1. Presenting a cohesive narrative that integrates information from multiple sources
        2. Providing accurate analysis with supporting evidence
        3. Identifying connections, patterns, and insights across sources
        4. Including proper citations by referencing the source number [X] when using information from a specific source

        INFORMATION SOURCES:
        {context}

        Generate a well-structured report with:
        - Introduction explaining the topic and its significance
        - Main body with thorough analysis of the information
        - Conclusion summarizing key findings and implications
        - Properly cited sources throughout using the source numbers provided
        """
