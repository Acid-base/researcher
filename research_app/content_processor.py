# Content Processor# Functions for fetching, parsing, cleaning, and chunking content from URLs.import requestsimport httpxfrom bs4 import BeautifulSoupimport reimport fitz  # PyMuPDFimport PyPDF2import pdfplumberfrom txtai.pipeline import Textractorfrom urllib.parse import urlparseimport logginglogger = logging.getLogger(__name__)
class ContentProcessor:
    def __init__(self):
        self.textractor = Textractor(sentences=True)
        
    def fetch_and_parse(self, url):
        """
        Fetch content from a URL and parse it based on content type
        """
        try:
            # Determine the content type based on URL or headers
            if url.lower().endswith('.pdf'):
                return self._fetch_and_parse_pdf(url)
            else:
                return self._fetch_and_parse_html(url)
        except Exception as e:
            logger.error(f"Error fetching and parsing content from {url}: {str(e)}")
            return None, None
    
    def _fetch_and_parse_html(self, url):
        """
        Fetch and parse HTML content
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract the title
        title = soup.title.text.strip() if soup.title else "Untitled"
        
        # Remove script, style, and hidden elements
        for element in soup(['script', 'style', 'head', 'header', 'footer', 'nav']):
            element.decompose()
            
        # Get the main text content
        text = soup.get_text(separator=' ', strip=True)
        
        metadata = {
            'title': title,
            'url': url,
            'source_type': 'html',
            'retrieval_date': str(requests.utils.default_headers()['Date'])
        }
        
        return text, metadata
    
    def _fetch_and_parse_pdf(self, url):
        """
        Fetch and parse PDF content
        """
        # Download the PDF
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Using textractor to extract PDF content
        text = self.textractor(response.content, content_type="application/pdf")
        
        # Extracting basic metadata
        title = url.split('/')[-1].replace('.pdf', '') if url else "Untitled PDF"
        
        metadata = {
            'title': title,
            'url': url,
            'source_type': 'pdf',
            'retrieval_date': str(requests.utils.default_headers()['Date'])
        }
        
        return text, metadata
        
    def clean_text(self, text):
        """
        Clean the extracted text by removing excess whitespace, special characters, etc.
        """
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that don't add meaning
        text = re.sub(r'[^\w\s.,;:!?\'"\-–—()]', ' ', text)
        
        # Remove multiple spaces again after character removal
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
        
    def chunk_text(self, text, chunk_size=1000, overlap=100):
        """
        Split the text into chunks with semantic awareness
        
        Args:
            text: The text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
            
        # First attempt to split by paragraphs
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph exceeds the chunk size, store current chunk and start a new one
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap if possible
                if len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + " " + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += " " + paragraph
                else:
                    current_chunk = paragraph
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # If any chunk is still too large, split it further by sentences
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by sentences
                sentences = re.split(r'(?<=[.!?])\s+', chunk)
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                        final_chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        if current_chunk:
                            current_chunk += " " + sentence
                        else:
                            current_chunk = sentence
                
                if current_chunk:
                    final_chunks.append(current_chunk.strip())
                    
        return final_chunks
