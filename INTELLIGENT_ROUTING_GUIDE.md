# 🧠 Intelligent Query Routing - Enhanced Agentic RAG

## 🎯 Overview

Your Agentic RAG system now features **intelligent source selection** that automatically determines which knowledge sources to use based on the query's relevance to your uploaded PDF content.

## 🔍 How It Works

### 1. **PDF Relevance Scoring**

```python
# System calculates how well the query matches PDF content
pdf_relevance_score = matches_found / total_query_terms / total_documents
```

**Scoring Logic:**

- **High (>0.7)**: Query well-covered by PDF → Prioritize PDF content
- **Medium (0.3-0.7)**: Partial coverage → Use all sources equally
- **Low (<0.3)**: Poor PDF match → Prioritize external sources

### 2. **Intelligent Source Selection**

#### **When PDF Content is Sufficient:**

- Query: _"What charts are shown in the document?"_
- **Result**: Uses only PDF content
- **Sources**: 📄 PDF only

#### **When External Sources Needed:**

- Query: _"What's the current weather in New York?"_
- **Result**: Triggers web search + Google Drive
- **Sources**: 🌐 Web + ☁️ Google Drive

#### **When Current Info Requested:**

- Query: _"What are the latest news about AI?"_
- **Result**: Prioritizes web search + Google Drive
- **Sources**: 🌐 Web + ☁️ Google Drive + 📄 PDF (supplemental)

## 🎪 Smart Trigger Keywords

### **Web Search Triggers:**

- `latest`, `current`, `today`, `recent`, `update`, `new`, `now`
- `news`, `market`, `price`, `stock`, `weather`, `event`

### **Google Drive Triggers:**

- `document`, `file`, `report`, `my`, `our`, `company`
- `latest`, `current`, `recent` (for document updates)

### **PDF-First Queries:**

- Content well-matched by similarity search
- Technical terms found in uploaded documents
- Specific references to charts, graphs, pages

## 📊 Response Prioritization

### **Low PDF Relevance (External Query)**

```
Note: This query appears to be outside the scope of the uploaded PDF content.
Focus on external sources (Google Drive and web search) for the answer.
```

### **High PDF Relevance (Document Query)**

```
Note: This query is well-covered by the PDF content.
Use PDF information as the primary source, supplemented by external sources if needed.
```

### **Mixed Relevance**

```
Note: This query partially relates to the PDF content.
Combine information from all sources appropriately.
```

## 🔄 Complete Workflow

### **Step 1: Query Analysis**

1. Calculate PDF relevance score
2. Detect trigger keywords
3. Determine source strategy

### **Step 2: Source Selection**

```python
if pdf_relevance_score < 0.3:
    # External query
    use_web_search = True
    use_drive_search = True
elif "latest" in query:
    # Current info query
    use_web_search = True
    use_drive_search = True
elif "document" in query:
    # Document query
    use_drive_search = True
```

### **Step 3: Response Generation**

1. Gather context from selected sources
2. Generate response with source prioritization notes
3. Include proper citations for transparency

## 🎯 Example Scenarios

### **Scenario 1: PDF-Focused Query**

- **Query**: _"What methodology is described in section 3?"_
- **PDF Score**: 0.85 (high)
- **Sources Used**: 📄 PDF only
- **Citations**: [1] PDF Page 3, [2] PDF Page 4

### **Scenario 2: External Information**

- **Query**: _"What's the current stock market situation?"_
- **PDF Score**: 0.1 (low)
- **Sources Used**: 🌐 Web search, ☁️ Google Drive
- **Citations**: [1] Web Search, [2] Google Drive Document

### **Scenario 3: Mixed Query**

- **Query**: _"How does the document's approach compare to current best practices?"_
- **PDF Score**: 0.5 (medium)
- **Sources Used**: 📄 PDF + 🌐 Web + ☁️ Google Drive
- **Citations**: [1] PDF Page 2, [2] Web Search, [3] Google Drive

## ✅ Benefits

### **For Users:**

- 🎯 **Relevant Results**: Always get the most appropriate information
- ⚡ **Efficient**: No unnecessary searches when PDF has the answer
- 🔍 **Comprehensive**: External sources when needed
- 📊 **Transparent**: Always know where information comes from

### **For System:**

- 🚀 **Performance**: Avoid unnecessary API calls
- 🎪 **Intelligence**: Context-aware decision making
- 🔄 **Scalability**: Efficient resource utilization
- 📈 **Accuracy**: Right sources for right queries

## 🧪 Testing Results

**All query types successfully routed:**

- ✅ PDF-specific queries → PDF content only
- ✅ External queries → Web + Google Drive
- ✅ Current info queries → External sources prioritized
- ✅ Document queries → Google Drive + PDF
- ✅ Mixed queries → All sources balanced

Your Agentic RAG system now provides **intelligent, context-aware responses** that automatically select the best knowledge sources for each unique query! 🎉
