# AWS Billing Data Extractor

A powerful MVP application that extracts structured data from AWS billing PDFs using Claude LLM and presents it through an intuitive Streamlit interface.

## 🚀 Features

- **PDF Processing**: Extract data from single or multiple AWS billing PDFs
- **Claude LLM Integration**: Uses Claude Sonnet 4 via Google Cloud Vertex AI for intelligent data extraction
- **Structured Output**: Extracts AWS service details including:
  - AWS Service Type (e.g., t3a.small, t2.micro)
  - Operating System (Linux/UNIX, Windows)
  - Region (Mumbai, us-east-1, etc.)
  - Usage Hours
  - CPU Cores
  - RAM (GB)
  - Cost (USD)
- **Excel Export**: Save results to Excel files with proper formatting
- **Flexible Output**: Choose between individual Excel files per PDF or combined multi-sheet Excel
- **Error Handling**: Comprehensive error handling and logging
- **User-Friendly UI**: Clean Streamlit interface for easy file upload and processing

## 📋 Requirements

- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Claude LLM access via Anthropic Vertex AI
- Service account credentials file (`paradigm-gpt-9c0deac797aa.json`)

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup credentials**:
   - Place your `paradigm-gpt-9c0deac797aa.json` file in the project directory
   - The application will automatically set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

4. **Create output directory** (optional - will be created automatically):
   ```bash
   mkdir output
   ```

## 🚀 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Using the Interface

1. **Initialize Claude LLM**: Click the "Initialize Claude LLM" button in the sidebar
2. **Upload PDFs**: Use the file uploader to select one or more AWS billing PDF files
3. **Choose Processing Mode**:
   - **Single Excel per PDF**: Creates separate Excel files for each PDF
   - **Combined Excel file**: Creates one Excel file with multiple sheets
4. **Process Files**: Click "Process Files" to start extraction
5. **View Results**: Review extracted data in the interface
6. **Download Output**: Find Excel files in the `output/` directory

### Processing Modes

#### Single Excel per PDF
- Each PDF generates its own Excel file
- File naming: `{original_pdf_name}_extracted.xlsx`
- Sheet name: Sanitized version of PDF filename

#### Combined Excel File
- All PDFs processed into one Excel file
- File naming: `AWS_Billing_Extract_{timestamp}.xlsx`
- Each PDF gets its own sheet named after the source file

## 📁 Project Structure

```
BOT/
├── app.py                 # Main Streamlit application
├── claude_llm.py         # Claude LLM integration
├── pdf_processor.py      # PDF text extraction
├── excel_handler.py      # Excel output management
├── error_handler.py      # Error handling and logging
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── run.py              # Simple run script
├── output/             # Generated Excel files (created automatically)
├── logs/               # Application logs (created automatically)
└── paradigm-gpt-9c0deac797aa.json  # Google Cloud credentials
```

## 🔧 Configuration

### Claude LLM Settings
- **Project ID**: paradigm-gpt
- **Location**: us-east5
- **Model**: claude-sonnet-4@20250514
- **Max Tokens**: 4000
- **Temperature**: 0.1

### File Limits
- **Max PDF Size**: 50 MB per file
- **Max Upload Size**: 200 MB total
- **Supported Formats**: PDF only

## 📊 Output Format

The extracted data includes these columns:

| Column | Description | Example |
|--------|-------------|---------|
| AWS | Service type | t3a.small, t2.micro |
| OS | Operating System | Linux/UNIX, Windows |
| Region | AWS Region | Mumbai, us-east-1 |
| Hours | Usage hours | 744, 2231.51 |
| Cores | CPU cores | 2, 4, 8 |
| RAM | RAM in GB | 2, 4, 16 |
| Cost | Cost in USD | $9.15, $27.67 |

### Data Handling
- **Missing Fields**: Stored as `null` in Excel
- **Numeric Formatting**: Hours as decimal, Cores/RAM as integers
- **Currency Formatting**: Cost formatted with $ symbol
- **Data Validation**: Automatic type conversion and validation

## 🚨 Error Handling

The application includes comprehensive error handling:

- **Connection Errors**: Network and API connectivity issues
- **File Errors**: Invalid PDFs, file size limits, permissions
- **Processing Errors**: Text extraction failures, LLM processing issues
- **Output Errors**: Excel file creation and formatting issues

### Logs
- Application logs are stored in `logs/` directory
- Daily log rotation with timestamp
- Both file and console logging available

## 🔍 Troubleshooting

### Common Issues

1. **Claude LLM Initialization Failed**
   - Check credentials file exists and is valid
   - Verify Google Cloud project and Vertex AI access
   - Ensure network connectivity

2. **PDF Processing Failed**
   - Check file is a valid PDF
   - Verify file size is under 50 MB
   - Try with a different PDF extraction method

3. **No Data Extracted**
   - PDF may not contain tabular billing data
   - Check if PDF is text-based (not scanned image)
   - Review logs for Claude LLM processing details

4. **Excel Export Failed**
   - Check write permissions in output directory
   - Verify disk space availability
   - Check for special characters in filenames

### Debug Mode
Enable detailed logging by modifying `config.py`:
```python
LOGGING_CONFIG = {
    "level": "DEBUG",  # Change from INFO to DEBUG
    ...
}
```

## 🤝 Support

For issues and questions:
1. Check the logs in `logs/` directory
2. Review error messages in the Streamlit interface
3. Verify all requirements are properly installed
4. Test with a simple, small PDF first

## 📝 License

This project is for internal use. Please ensure compliance with AWS terms of service and data privacy requirements when processing billing documents.

## 🔄 Version History

- **v1.0.0**: Initial MVP release with core functionality
  - PDF processing with multiple extraction methods
  - Claude LLM integration for data extraction
  - Excel export with formatting
  - Streamlit web interface
  - Comprehensive error handling
