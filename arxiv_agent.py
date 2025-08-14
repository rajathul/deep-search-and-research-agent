import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from base_agent import BaseAgent

class ArxivAgent(BaseAgent):
    """Agent specialized for searching and processing ArXiv papers."""
    
    def __init__(self):
        super().__init__("ArXiv Agent")
    
    def generate_search_query(self, user_question: str, **kwargs) -> str:
        """Generate ArXiv-specific search query with prefixes."""
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
        
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )
            if response.text is not None:
                return response.text.strip()
            else:
                return ""
        except Exception:
            return super().generate_search_query(user_question, **kwargs)
    
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search ArXiv for papers."""
        max_results = kwargs.get('max_results', 5)
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        
        # Add date filtering if provided
        if date_from and date_to:
            from_formatted = date_from.replace('-', '')
            to_formatted = date_to.replace('-', '')
            query += f" AND submittedDate:[{from_formatted} TO {to_formatted}]"
        
        base_url = 'http://export.arxiv.org/api/query?'
        params = {
            'search_query': query,
            'sortBy': 'relevance',
            'sortOrder': 'descending',
            'max_results': max_results
        }
        
        url = base_url + urllib.parse.urlencode(params)
        
        try:
            with urllib.request.urlopen(url) as response:
                xml_data = response.read().decode('utf-8')
            return self._parse_arxiv_xml(xml_data)
        except Exception as e:
            print(f"ArXiv search error: {e}")
            return []
    
    def _parse_arxiv_xml(self, xml_data: str) -> List[Dict[str, Any]]:
        """Parse ArXiv XML response."""
        papers = []
        try:
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            root = ET.fromstring(xml_data)
            entries = root.findall('atom:entry', namespace)

            for entry in entries:
                title_elem = entry.find('atom:title', namespace)
                summary_elem = entry.find('atom:summary', namespace)
                link_elem = entry.find('atom:id', namespace)
                
                if all(elem is not None and getattr(elem, 'text', None) for elem in [title_elem, summary_elem, link_elem]):
                    papers.append({
                        'title': self._clean_text(getattr(title_elem, 'text', "") or ""),
                        'summary': self._clean_text(getattr(summary_elem, 'text', "") or ""),
                        'link': (getattr(link_elem, 'text', "") or "").strip(),
                        'source_type': 'arxiv'
                    })
            return papers
        except Exception as e:
            print(f"XML parsing error: {e}")
            return []
    
    def _clean_text(self, text: str) -> str:
        """Clean text for JSON safety."""
        if not text:
            return ""
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = text.replace('"', "'")
        import re
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def process_sources(self, sources: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Process ArXiv sources (already clean from XML parsing)."""
        return sources
