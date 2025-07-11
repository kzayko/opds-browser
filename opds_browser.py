import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlencode
import logging
import os

class OPDSBrowser:
    def __init__(self, base_url):
        self.base_url = base_url
        self.current_url = base_url
        self.feed = None
        self.links = {}
        self.history = []
        self.path_ids = []  # Stack of folder ids
        
        # Load configuration from environment
        self.timeout = int(os.getenv('OPDS_TIMEOUT', 30))
        self.user_agent = os.getenv('OPDS_USER_AGENT', 'OPDS-Browser/1.0')
        
        # Setup session with optional proxy
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        
        # Configure proxy if specified
        proxy_url = os.getenv('OPDS_PROXY_URL')
        if proxy_url:
            proxy_username = os.getenv('OPDS_PROXY_USERNAME')
            proxy_password = os.getenv('OPDS_PROXY_PASSWORD')
            
            if proxy_username and proxy_password:
                proxy_auth = f"{proxy_username}:{proxy_password}@"
                proxy_url = proxy_url.replace('://', f'://{proxy_auth}')
            
            self.session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            logging.debug(f"Configured proxy: {proxy_url}")

    def fetch_feed(self, url=None, add_to_history=True, parent_id=None):
        url = url or self.current_url
        if self.feed is not None and url != self.current_url and add_to_history:
            self.history.append((self.current_url, self.path_ids.copy()))
        logging.debug(f'Fetching feed: {url}')
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        self.feed = ET.fromstring(resp.content)
        self.current_url = url
        self.links = self._parse_links()
        # Maintain path_ids stack
        if parent_id is not None:
            self.path_ids.append(parent_id)
        elif not add_to_history:
            # On back, restore path from history
            pass
        return self.feed

    def _parse_links(self):
        links = {}
        for link in self.feed.findall('{http://www.w3.org/2005/Atom}link'):
            rel = link.attrib.get('rel')
            href = link.attrib.get('href')
            if href:
                links[rel] = urljoin(self.current_url, href)
        return links

    def get_entries(self):
        entries = []
        for entry in self.feed.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title')
            author = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
            id_ = entry.find('{http://www.w3.org/2005/Atom}id')
            summary = entry.find('{http://www.w3.org/2005/Atom}summary')
            cover = None
            entry_type = None
            nav_url = None
            has_acquisition = False
            has_nav = False
            attachments = []
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                rel = link.attrib.get('rel', '')
                href = link.attrib.get('href')
                type_ = link.attrib.get('type', '')
                logging.debug(f"Link: rel={rel}, type={type_}, href={href}")
                if rel == 'http://opds-spec.org/image':
                    cover = urljoin(self.current_url, href)
                # Book detection (acquisition link)
                if rel and rel.startswith('http://opds-spec.org/acquisition'):
                    has_acquisition = True
                # Navigation/folder detection: any link with type application/atom+xml*
                if type_.startswith('application/atom+xml'):
                    has_nav = True
                    if not nav_url:
                        nav_url = urljoin(self.current_url, href)
                # Collect attachments (not navigation, not cover)
                if not type_.startswith('application/atom+xml') and rel != 'http://opds-spec.org/image':
                    if href:
                        attachments.append({'rel': rel, 'type': type_, 'url': urljoin(self.current_url, href)})
            if has_acquisition:
                entry_type = 'book'
            elif has_nav:
                entry_type = 'folder'
            else:
                entry_type = 'unknown'
            logging.debug(f"Entry: {title.text if title is not None else ''} | Type: {entry_type} | URL: {nav_url}")
            entries.append({
                'title': title.text if title is not None else '',
                'author': author.text if author is not None else '',
                'id': id_.text if id_ is not None else '',
                'summary': summary.text if summary is not None else '',
                'cover': cover,
                'type': entry_type,
                'url': nav_url,
                'attachments': attachments
            })
        return entries

    def get_navigation_links(self):
        nav = {}
        for rel in ['next', 'previous', 'start', 'self']:
            if rel in self.links:
                nav[rel] = self.links[rel]
        return nav

    def go_to(self, rel):
        if rel in self.links:
            return self.fetch_feed(self.links[rel])
        return None

    def search(self, query):
        # Try to find a search link with template
        for link in self.feed.findall('{http://www.w3.org/2005/Atom}link'):
            if link.attrib.get('rel') == 'search' and 'template' in link.attrib:
                template = link.attrib['template']
                url = template.replace('{searchTerms}', urlencode({'': query})[1:])
                return self.fetch_feed(url)
        # Fallback: append ?searchTerm=...
        search_url = self.base_url + '?searchTerm=' + urlencode({'': query})[1:]
        return self.fetch_feed(search_url)

    def go_back(self):
        if self.history:
            prev_url, prev_path = self.history.pop()
            self.path_ids = prev_path
            return self.fetch_feed(prev_url, add_to_history=False)
        return None

    def get_path_ids(self):
        return self.path_ids.copy()
    
    def reset_to_root(self):
        """Reset browser to root level"""
        self.current_url = self.base_url
        self.path_ids = []
        self.history = []
        return self.fetch_feed(self.base_url, add_to_history=False) 