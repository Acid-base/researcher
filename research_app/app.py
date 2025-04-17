import os
import json
import logging
from flask import Flask, request, jsonify
from content_processor import ContentProcessor
from txtai_manager import TxtaiManager
from gemini_client import GeminiClient
from searxng_client import SearxngClient
import utils

# Setup logging
logger = utils.setup_logging()

# Initialize Flask app
app = Flask(__name__)

# Initialize components
content_processor = ContentProcessor()
txtai_manager = TxtaiManager()
gemini_client = GeminiClient()
searxng_client = SearxngClient()

# Ensure required directories exist
utils.ensure_directories([
    "/app/txtai_index",
    "/app/data",
    "/app/data/reports"
])

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "name": "Deep Research Tool API",
        "version": "1.0.0"
    })

@app.route('/search', methods=['POST'])
@utils.timing_decorator
def search():
    """
    Search for information on a topic using SearXNG.
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Query parameter is required"}), 400

    query = data['query']
    categories = data.get('categories', 'general,science')
    engines = data.get('engines')
    language = data.get('language', 'en')
    time_range = data.get('time_range')

    try:
        logger.info(f"Searching for: {query}")
        results = searxng_client.search(query, categories, engines, language, time_range)

        return jsonify({
            "status": "success",
            "query": query,
            "results": results.get('results', []),
            "result_count": len(results.get('results', []))
        })
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/process', methods=['POST'])
@utils.timing_decorator
def process_urls():
    """
    Process URLs to extract, clean, and index content.
    """
    data = request.json
    if not data or 'urls' not in data:
        return jsonify({"error": "URLs are required"}), 400

    urls = data['urls']
    query = data.get('query', '')  # Original query for context

    try:
        logger.info(f"Processing {len(urls)} URLs")

        processed_docs = []
        for url in urls:
            # Fetch and parse content
            content, metadata = content_processor.fetch_and_parse(url)

            if not content:
                logger.warning(f"No content extracted from {url}")
                continue

            # Clean the text
            cleaned_text = content_processor.clean_text(content)

            # Chunk the text
            chunks = content_processor.chunk_text(cleaned_text)

            # Add chunks to processed docs with metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = i + 1
                chunk_metadata['total_chunks'] = len(chunks)
                chunk_metadata['original_query'] = query

                processed_docs.append({
                    "text": chunk,
                    "metadata": chunk_metadata
                })

        # Index the processed documents
        num_indexed = txtai_manager.index_documents(processed_docs)

        return jsonify({
            "status": "success",
            "processed_urls": len(urls),
            "indexed_chunks": num_indexed,
            "index_info": txtai_manager.get_index_info()
        })
    except Exception as e:
        logger.error(f"Error in processing: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/retrieve', methods=['POST'])
@utils.timing_decorator
def retrieve():
    """
    Retrieve relevant information for a query from the txtai index.
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Query parameter is required"}), 400

    query = data['query']
    limit = data.get('limit', 10)

    try:
        logger.info(f"Retrieving information for: {query}")

        # Retrieve relevant documents
        results = txtai_manager.retrieve(query, limit)

        return jsonify({
            "status": "success",
            "query": query,
            "results": results,
            "result_count": len(results)
        })
    except Exception as e:
        logger.error(f"Error in retrieval: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
@utils.timing_decorator
def generate_report():
    """
    Generate a comprehensive research report using Gemini.
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Query parameter is required"}), 400

    query = data['query']
    limit = data.get('limit', 15)  # Number of context documents to retrieve
    prompt_template = data.get('prompt_template')  # Optional custom prompt

    try:
        logger.info(f"Generating report for: {query}")

        # Retrieve relevant documents
        context = txtai_manager.retrieve(query, limit)

        if not context:
            return jsonify({"error": "No relevant information found. Please process some URLs first."}), 404

        # Generate report
        report_result, citations = gemini_client.generate_report(context, prompt_template)

        if "error" in report_result:
            return jsonify({"error": report_result["error"]}), 500

        # Save the research results
        report_file = utils.save_research_results(query, report_result["report"], citations)

        # Format citations for response
        formatted_citations = utils.format_citations(citations)

        return jsonify({
            "status": "success",
            "query": query,
            "report": report_result["report"],
            "citations": formatted_citations,
            "source_count": len(citations),
            "saved_to": report_file
        })
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/workflow', methods=['POST'])
@utils.timing_decorator
def research_workflow():
    """
    Execute the complete research workflow: search, process, and generate report.
    """
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Query parameter is required"}), 400

    query = data['query']
    max_urls = data.get('max_urls', 10)
    categories = data.get('categories', 'general,science')
    engines = data.get('engines')
    language = data.get('language', 'en')
    time_range = data.get('time_range')
    prompt_template = data.get('prompt_template')

    try:
        logger.info(f"Starting research workflow for: {query}")

        # Step 1: Search for information
        search_results = searxng_client.search(query, categories, engines, language, time_range)
        urls = [result['url'] for result in search_results.get('results', [])[:max_urls]]

        if not urls:
            return jsonify({"error": "No search results found."}), 404

        # Step 2: Process and index the URLs
        processed_docs = []
        for url in urls:
            content, metadata = content_processor.fetch_and_parse(url)
            if not content:
                continue

            cleaned_text = content_processor.clean_text(content)
            chunks = content_processor.chunk_text(cleaned_text)

            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_id'] = i + 1
                chunk_metadata['total_chunks'] = len(chunks)
                chunk_metadata['original_query'] = query

                processed_docs.append({
                    "text": chunk,
                    "metadata": chunk_metadata
                })

        num_indexed = txtai_manager.index_documents(processed_docs)

        # Step 3: Retrieve relevant information
        context = txtai_manager.retrieve(query, 15)

        # Step 4: Generate the report
        report_result, citations = gemini_client.generate_report(context, prompt_template)

        if "error" in report_result:
            return jsonify({"error": report_result["error"]}), 500

        # Save the research results
        report_file = utils.save_research_results(query, report_result["report"], citations)

        # Format citations for response
        formatted_citations = utils.format_citations(citations)

        return jsonify({
            "status": "success",
            "query": query,
            "report": report_result["report"],
            "citations": formatted_citations,
            "source_count": len(citations),
            "urls_processed": len(urls),
            "chunks_indexed": num_indexed,
            "saved_to": report_file
        })
    except Exception as e:
        logger.error(f"Error in research workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/index-info', methods=['GET'])
def index_info():
    """
    Get information about the txtai index.
    """
    try:
        info = txtai_manager.get_index_info()
        return jsonify({
            "status": "success",
            "index_info": info
        })
    except Exception as e:
        logger.error(f"Error getting index info: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
