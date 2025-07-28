# PDF Outline Extractor (1a)

A sophisticated Python application that intelligently extracts structured outlines from PDF documents using AI-like pattern recognition and semantic analysis.

## Overview

This tool automatically processes PDF files and generates structured JSON outlines containing hierarchical headings, titles, and page references. It uses advanced text analysis to identify document structure patterns, making it particularly effective for business documents, academic papers, RFPs, and FAQ documents.

## Features

- **Intelligent Heading Detection**: Uses AI-like pattern recognition to identify headings based on:
  - Numbered sections (1., 1.1, 1.1.1, etc.)
  - Semantic keywords (Introduction, Summary, Background, etc.)
  - Font size and formatting analysis
  - Document structure patterns
  - FAQ and Q&A format recognition

- **Multi-Document Processing**: Batch process multiple PDF files automatically
- **Hierarchical Structure**: Generates proper heading levels (H1, H2, H3)
- **Context-Aware Analysis**: Considers page position, font ratios, and document flow
- **Fragment Prevention**: Advanced filtering to avoid incomplete text fragments
- **JSON Output**: Clean, structured output format for integration

## Project Structure

```
1a/
├── app.py              # Main application with PDFOutlineExtractor class
├── Dockerfile          # Multi-stage Docker configuration
├── requirements.txt    # Python dependencies
├── input/              # Place PDF files here for processing
│   ├── file01.pdf
│   ├── file02.pdf
│   ├── file03.pdf
│   ├── file04.pdf
│   └── file05.pdf
├── output/             # Generated JSON outlines appear here
└── README.md           # This file
```

## Installation & Setup

### Local Development

1. **Clone/Download the project**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Docker Deployment

Build and run using the included Dockerfile:

```bash
# Build the image
docker build -t pdf-outline-extractor .

# Run the container
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" pdf-outline-extractor
```

## Usage

### Automatic Mode (Recommended)

Place PDF files in the `input/` directory and run:

```bash
python app.py
```

The application will:
- Process all PDF files in the `input/` folder
- Generate JSON outline files in the `output/` folder
- Display progress and results

### Manual File Processing

Process specific files:

```bash
# Single file
python app.py document.pdf

# Multiple files
python app.py file1.pdf file2.pdf file3.pdf

# Batch mode with custom output directory
python app.py --batch --output-dir results/ *.pdf
```

### Command Line Options

- `--batch`: Enable batch processing mode
- `--output-dir`, `-o`: Specify custom output directory
- `files`: List of PDF files to process (optional)

## Output Format

Generated JSON files contain:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    },
    {
      "level": "H2", 
      "text": "Background",
      "page": 2
    },
    {
      "level": "H3",
      "text": "Methodology",
      "page": 3
    }
  ]
}
```

## Technical Details

### Core Components

- **PDFOutlineExtractor**: Main class handling intelligent extraction
- **HeadingCandidate**: Data structure for heading analysis
- **Pattern Recognition**: Regex patterns for numbered sections and structures
- **Semantic Analysis**: Keyword-based heading identification
- **Font Analysis**: Typography-based heading detection

### Algorithm Features

- **Confidence Scoring**: Each heading candidate receives a confidence score
- **Adaptive Thresholding**: Adjusts sensitivity based on document complexity
- **Fragment Prevention**: Filters out incomplete text and line breaks
- **Question Handling**: Special processing for FAQ and Q&A documents
- **Context Awareness**: Considers page position, formatting, and document flow

### Dependencies

- **PyMuPDF (1.24.5)**: PDF text extraction and analysis
- **Standard Library**: re, json, argparse, collections, dataclasses, typing

## Docker Configuration

The included Dockerfile uses a multi-stage build for optimal image size:

- **Builder Stage**: Installs compilation dependencies
- **Runtime Stage**: Minimal Alpine Linux with only runtime requirements
- **Security**: Runs as non-root user (appuser:appgroup)
- **Optimization**: Efficient layer caching and package cleanup

## Use Cases

- **Document Analysis**: Extract structure from research papers, reports
- **RFP Processing**: Identify sections in Request for Proposal documents
- **FAQ Organization**: Structure Q&A documents with proper numbering
- **Content Migration**: Extract headings for content management systems
- **Document Indexing**: Create searchable indexes from PDF content

## Performance

- **Processing Speed**: ~1-5 seconds per typical document
- **Memory Usage**: Minimal - processes documents sequentially
- **Accuracy**: High precision with advanced filtering and semantic analysis
- **Scalability**: Handles batch processing of multiple documents

## Error Handling

- Graceful handling of corrupted or unreadable PDFs
- Detailed error reporting for debugging
- Continues processing remaining files if one fails
- Form document detection (skips application forms)

## Development

### Key Classes

- `PDFOutlineExtractor`: Main extraction logic
- `HeadingCandidate`: Heading analysis data structure

### Key Methods

- `extract_outline()`: Main entry point
- `is_likely_heading()`: AI-like heading detection
- `calculate_heading_confidence()`: Confidence scoring
- `extract_title_intelligently()`: Smart title extraction

### Extending the Tool

The modular design allows easy extension for:
- Additional document types
- Custom pattern recognition
- Enhanced semantic analysis
- Different output formats

## License

This project is designed for Adobe document processing workflows and follows enterprise coding standards.
