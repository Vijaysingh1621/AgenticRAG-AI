from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os

# Set your Gemini API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCGSJ2o_-jyTb5aGhfrlbGDnLJgZVpuPSQ"

embedder = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
