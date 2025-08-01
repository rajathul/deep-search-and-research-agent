import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from google import genai

client = genai.Client()

def _clean_text_for_json(text):
    """Clean text to make it JSON-safe."""
    if not isinstance(text, str):
        return text
    
    # Replace problematic characters
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = text.replace('"', "'")  # Replace double quotes with single quotes
    text = text.replace('\\', '/')  # Replace backslashes
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.encode('ascii', 'ignore').decode('ascii')  # Remove non-ASCII
    return text.strip()

def tool_query_generator(inputs):
    """Tool to generate an arXiv query from a user question."""
    user_question = inputs.get('user_question', '')
    if not user_question:
        return "Error: No user question provided."
    
    prompt = f"""
    You are an expert at creating search queries for the arXiv academic database.
    Transform the user's question into a concise query string using arXiv's syntax.

    - Use prefixes like `ti:` for title, `au:` for author, and `abs:` for abstract.
    - Combine keywords with `AND`, `OR`. Use quotes for exact phrases.
    - Focus on the most critical technical terms.

    User Question: "{user_question}"

    Return ONLY the query keyword string itself, with no explanations.
    Example:
    User Question: "What are the latest advancements in using graph neural networks for drug discovery?"
    Result: ti:"graph neural network" AND abs:"drug discovery"
    """
    
    print("Tool: Generating arXiv query...")
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        api_query = response.text.strip()
        return api_query
    except Exception as e:
        return f"Error generating query: {e}"

def tool_arxiv_search(inputs):
    """Tool to search arXiv and return parsed papers."""
    query_keywords = inputs.get('query_keywords', '')
    max_results = inputs.get('max_results', 5)
    
    if not query_keywords:
        return "Error: No query keywords provided."
    
    base_url = 'http://export.arxiv.org/api/query?'
    params = {
        'search_query': query_keywords,
        'sortBy': 'relevance',
        'sortOrder': 'descending',
        'max_results': max_results
    }
    encoded_params = urllib.parse.urlencode(params)
    url = base_url + encoded_params
    
    print(f"Tool: Fetching up to {max_results} papers from arXiv...")
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                xml_data = response.read().decode('utf-8')
            else:
                return f"Error: Received status code {response.status}"
    except urllib.error.URLError as e:
        return f"Error fetching data: {e}"
    
    # Parse XML
    print("Tool: Parsing XML...")
    papers = []
    try:
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        root = ET.fromstring(xml_data)
        entries = root.findall('atom:entry', namespace)
        
        for entry in entries:
            title = entry.find('atom:title', namespace).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', namespace).text.strip().replace('\n', ' ')
            link = entry.find('atom:id', namespace).text.strip()
            
            # Clean text for JSON safety
            title = _clean_text_for_json(title)
            summary = _clean_text_for_json(summary)
            
            papers.append({'title': title, 'summary': summary, 'link': link})
        
        return papers
    except Exception as e:
        return f"Error parsing XML: {e}"

def tool_synthesis(inputs):
    """Tool to synthesize an answer from papers."""
    original_question = inputs.get('original_question', '')
    papers = inputs.get('papers', [])
    
    if not papers:
        return "Error: No papers provided."
    
    print("Tool: Synthesizing findings...")
    
    papers_context = ""
    for i, paper in enumerate(papers, 1):
        papers_context += f"Source [{i}]: "
        papers_context += f"Title: <a href='{paper['link']}' target='_blank'>{paper['title']}</a>\n"
        
    prompt = f"""
    You are a meticulous research analyst. Your task is to write a report that answers the user's question by synthesizing information from the provided paper summaries.

    **Instructions:**
    1. Write a coherent, paragraph-style report that integrates the findings from the papers.
    2. For every claim or finding you take from a source, you **must** add a citation marker at the end of the sentence, like `[1]`, `[2]`, corresponding to the source number. Format the citation as a link, e.g., `[1](#source-1)`.
    3. After the report, add a heading titled "**Sources**".
    4. Under the "Sources" heading, create a numbered list where each item has an ID that matches the citation, e.g., `<li id="source-1">`. Each item should contain the full title of the source paper as a clickable link that opens in a new tab.

    Original User Question: "{original_question}"

    Here are the numbered sources you must use:
    {papers_context}

    Produce only the report and the sources list as requested.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error during synthesis: {e}"
