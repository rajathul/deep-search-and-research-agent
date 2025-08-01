import re
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from google import genai

api_key = os.getenv("GOOGLE_API_KEY")
# client = genai.Client(api_key=api_key)

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

def tool_query_generator(client, inputs):
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
    date_from = inputs.get('date_from')
    date_to = inputs.get('date_to')
    
    if not query_keywords:
        return "Error: No query keywords provided."
    
    if date_from and date_to:
        # Format YYYY-MM-DD to YYYYMMDD
        from_formatted = date_from.replace('-', '')
        to_formatted = date_to.replace('-', '')
        date_query = f" AND submittedDate:[{from_formatted} TO {to_formatted}]"
        query_keywords += date_query
    
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

def tool_synthesis(client, inputs):
    """Tool to synthesize an answer from papers and append a formatted source list."""
    original_question = inputs.get('original_question', '')
    papers = inputs.get('papers', [])
    
    if not papers:
        return "Error: No papers provided."
    
    print("Tool: Synthesizing findings...")
    
    # Create a context string for the LLM with numbered paper details
    papers_context = ""
    for i, paper in enumerate(papers, 1):
        # Don't pass HTML to the LLM context, just the raw text
        papers_context += f"Source [{i}]: Title: {paper['title']}. Summary: {paper['summary']}\n"
    
    # Update the prompt to ask ONLY for the report text.
    prompt = f"""
    You are a meticulous research analyst. Your task is to write a concise, paragraph-style report that answers the user's question by synthesizing information from the provided paper summaries.

    **Instructions:**
    1. Write a coherent report that integrates the findings from the papers.
    2. For every claim or finding you take from a source, you **must** add a citation marker at the end of the sentence, like `[1]`, `[2]`, or `[1, 3]`.
    3. Do NOT add a "Sources" heading or list. Produce ONLY the paragraph report text.

    Original User Question: "{original_question}"

    Here are the numbered sources you must use:
    {papers_context}

    Produce ONLY the report text as requested.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
        report_text = response.text.strip()
    except Exception as e:
        return f"Error during synthesis: {e}"
    
    # Programmatically build the "Sources" list in the correct order.
    # The '##' creates a Markdown H2 heading. The '<ol>' is an ordered list.
    sources_list_html = "\n\n## Sources\n<ol>"
    for i, paper in enumerate(papers, 1):
        # The id="source-i" is used by the frontend JS for smooth scrolling.
        title = paper.get('title', 'No Title')
        link = paper.get('link', '#')
        sources_list_html += f'<li id="source-{i}"><a href="{link}" target="_blank">{title}</a></li>'
    sources_list_html += "</ol>"
    
    # Combine the LLM-generated report with the programmatically generated list
    return report_text + sources_list_html
