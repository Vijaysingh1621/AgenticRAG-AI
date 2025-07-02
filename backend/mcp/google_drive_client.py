import os
import json
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

class GoogleDriveMCP:
    """Model Context Protocol client for Google Drive integration"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists(self.credentials_file):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    raise FileNotFoundError(f"Google Drive credentials file not found: {self.credentials_file}")
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
    
    def search_files(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for files in Google Drive"""
        try:
            results = self.service.files().list(
                q=f"name contains '{query}' or fullText contains '{query}'",
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, webViewLink, size)"
            ).execute()
            
            files = results.get('files', [])
            return files
        except Exception as e:
            print(f"Error searching Google Drive: {e}")
            return []
    
    def get_file_content(self, file_id: str) -> Optional[str]:
        """Get content of a text file from Google Drive"""
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType', '')
            
            # Handle different file types
            if 'text/' in mime_type or 'application/json' in mime_type:
                content = self.service.files().get_media(fileId=file_id).execute()
                return content.decode('utf-8')
            elif 'application/vnd.google-apps.document' in mime_type:
                # Export Google Docs as plain text
                content = self.service.files().export_media(
                    fileId=file_id, 
                    mimeType='text/plain'
                ).execute()
                return content.decode('utf-8')
            elif 'application/vnd.google-apps.spreadsheet' in mime_type:
                # Export Google Sheets as CSV
                content = self.service.files().export_media(
                    fileId=file_id, 
                    mimeType='text/csv'
                ).execute()
                return content.decode('utf-8')
            else:
                return f"Cannot extract text from file type: {mime_type}"
                
        except Exception as e:
            print(f"Error getting file content: {e}")
            return None
    
    def search_and_retrieve(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for files and retrieve their content"""
        files = self.search_files(query, max_results)
        results = []
        
        for file in files:
            content = self.get_file_content(file['id'])
            if content:
                results.append({
                    'id': file['id'],
                    'name': file['name'],
                    'content': content[:2000],  # Limit content length
                    'full_content': content,
                    'url': file.get('webViewLink', ''),
                    'type': 'google_drive',
                    'modified': file.get('modifiedTime', ''),
                    'size': file.get('size', 'Unknown')
                })
        
        return results

# Mock MCP client for when Google Drive isn't configured
class MockGoogleDriveMCP:
    """Mock MCP client for testing purposes"""
    
    def search_and_retrieve(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        return [
            {
                'id': 'mock_1',
                'name': f'Mock Document about {query}',
                'content': f'This is mock content related to {query}. This would normally come from Google Drive.',
                'full_content': f'Extended mock content about {query}...',
                'url': 'https://docs.google.com/mock',
                'type': 'google_drive',
                'modified': '2024-01-01T00:00:00Z',
                'size': '1024'
            }
        ]

def get_drive_client() -> GoogleDriveMCP | MockGoogleDriveMCP:
    """Get Google Drive client or mock if credentials not available"""
    try:
        return GoogleDriveMCP()
    except (FileNotFoundError, Exception) as e:
        print(f"Google Drive not configured, using mock: {e}")
        return MockGoogleDriveMCP()
