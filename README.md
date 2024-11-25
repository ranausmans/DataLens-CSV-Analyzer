DataLens AI 🔍
=============

DataLens AI is an intelligent CSV and Excel file analyzer powered by Google's Gemini AI. It provides instant insights, statistical analysis, and visualizations for your data.

Live Demo: https://usman.today/datalens

Features ✨
----------
• AI-Powered Analysis: Get intelligent insights about your data using Google's Gemini AI
• Statistical Analysis: Automatic calculation of key statistics and correlations
• Interactive Visualizations: Beautiful charts and graphs using Plotly
• Multiple File Formats: Support for both CSV and Excel files (.csv, .xlsx, .xls)
• Export to PDF: Download complete analysis reports as PDF
• Modern UI: Clean, responsive interface built with TailwindCSS

Technology Stack 🛠️
-----------------
Backend:
- Flask (Python web framework)
- Langchain (AI framework)
- Google Gemini AI
- Pandas (Data analysis)
- Plotly (Visualization)

Frontend:
- HTML/CSS/JavaScript
- TailwindCSS
- Plotly.js
- html2pdf.js

Getting Started 🚀
----------------
1. Clone the repository:
   git clone [https://github.com/ranausmans/datalens.git](https://github.com/ranausmans/DataLens-CSV-Analyzer.git)
   cd datalens

2. Create and activate virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install requirements:
   pip install -r requirements.txt

4. Set up environment variables:
   Create a .env file in the backend directory:
   GEMINI_API_KEY=your_gemini_api_key_here

5. Run the application:
   python app.py

The application will be available at http://localhost:5040

Usage 📊
-------
1. Open the application in your web browser
2. Upload a CSV or Excel file
3. Wait for the analysis to complete
4. View:
   - AI-generated insights
   - Statistical analysis
   - Interactive visualizations
5. Export the analysis to PDF if needed

API Endpoints 🔌
--------------
- GET /: Main application interface
- POST /api/analyze: Analyze uploaded file
  - Accepts: CSV, XLSX, XLS files
  - Returns: JSON with analysis results

Contributing 🤝
-------------
Contributions are welcome! Please feel free to submit a Pull Request.

Error Handling 🔧
---------------
The application includes comprehensive error handling for:
- Invalid file formats
- Empty files
- Data processing errors
- JSON serialization issues

Future Enhancements 🎯
--------------------
- Support for more file formats
- Advanced visualization options
- User authentication
- Analysis history
- Data filtering capabilities

License 📝
---------
This project is licensed under the MIT License - see the LICENSE file for details.

Author ✍️
--------
Rana Usman
Email: ranausman@outlook.com
GitHub: github.com/ranausmans

Acknowledgments 🙏
----------------
- Google Gemini AI for providing the AI capabilities
- The open-source community for the amazing tools and libraries

-------------------
Made with ❤️ by Rana Usman 
