import pandas as pd
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
import plotly.express as px
import json
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if pd.isna(obj):  # Handle any NaN/NaT values
                return None
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return None if np.isnan(obj) else float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, pd.Series):
                return self.default(obj.to_dict())
            if isinstance(obj, pd.DataFrame):
                return self.default(obj.to_dict())
        except:
            pass
        return super().default(obj)

class EnhancedCSVAnalyzer:
    def __init__(self, api_key):
        logger.info(f"Initializing EnhancedCSVAnalyzer")
        try:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=api_key,
                temperature=0.15,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1000
            )
            logger.info("Successfully initialized Gemini model")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise

    def generate_prompt(self, csv_head, column_details, statistical_summary):
        return f"""
        Analyze this CSV data:
        
        Data Preview:
        {csv_head}

        Column Information:
        {column_details}

        Statistical Summary:
        {statistical_summary}

        Please provide:
        1. Key insights and patterns in the data
        2. Potential correlations between variables
        3. Anomalies or outliers
        4. Recommendations for further analysis
        5. Data quality issues if any
        
        Format the response in clear sections.
        """

    def generate_visualizations(self, df):
        visualizations = []
        
        # Numerical columns distribution
        for col in df.select_dtypes(include=[np.number]).columns:
            fig = px.histogram(df, x=col, title=f'Distribution of {col}')
            visualizations.append({
                'type': 'histogram',
                'data': json.loads(fig.to_json())
            })
        
        return visualizations

    def serialize_dataframe_values(self, df_dict):
        """Convert DataFrame values to JSON-serializable format"""
        result = {}
        for key, value in df_dict.items():
            if isinstance(value, dict):
                result[key] = self.serialize_dataframe_values(value)
            elif isinstance(value, (pd.Timestamp, datetime)):
                result[key] = value.isoformat()
            elif isinstance(value, np.integer):
                result[key] = int(value)
            elif isinstance(value, np.floating):
                result[key] = None if pd.isna(value) else float(value)
            elif isinstance(value, np.ndarray):
                result[key] = value.tolist()
            elif pd.isna(value):
                result[key] = None
            else:
                try:
                    # Try standard JSON serialization
                    json.dumps(value)
                    result[key] = value
                except:
                    # If that fails, convert to string
                    result[key] = str(value)
        return result

    def analyze_csv(self, file_path):
        logger.info(f"Starting analysis of file: {file_path}")
        try:
            # Determine file type and read accordingly
            file_extension = file_path.split('.')[-1].lower()
            try:
                if file_extension == 'csv':
                    df = pd.read_csv(file_path)
                elif file_extension in ['xlsx', 'xls']:
                    df = pd.read_excel(file_path)
                else:
                    raise ValueError("Unsupported file format. Please upload CSV or Excel files.")
            except Exception as e:
                raise ValueError(f"Error reading file: {str(e)}")

            if df.empty:
                raise ValueError("The file is empty")

            logger.info(f"Successfully read file with shape: {df.shape}")
            
            # Clean the data
            df = df.replace([np.inf, -np.inf], np.nan)
            
            # For numeric columns, replace NaN with None
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].replace({np.nan: None})
            
            # For datetime columns, handle NaT
            datetime_cols = df.select_dtypes(include=['datetime64']).columns
            df[datetime_cols] = df[datetime_cols].astype(str).replace('NaT', None)

            # Basic analysis with cleaned data
            analysis = {
                "basic_stats": self.serialize_dataframe_values(df.describe(include='all').to_dict()),
                "missing_values": self.serialize_dataframe_values(df.isnull().sum().to_dict()),
                "column_types": df.dtypes.astype(str).to_dict(),
                "row_count": len(df),
                "column_count": len(df.columns)
            }

            # Correlation analysis
            try:
                numerical_cols = df.select_dtypes(include=[np.number]).columns
                if len(numerical_cols) > 1:
                    analysis["correlations"] = self.serialize_dataframe_values(
                        df[numerical_cols].corr().to_dict()
                    )
            except Exception as e:
                logger.warning(f"Correlation analysis failed: {str(e)}")
                analysis["correlations"] = {}

            # Generate LLM insights
            try:
                csv_head = df.head().to_string()
                column_details = "\n".join([f"{col}: {df[col].dtype}" for col in df.columns])
                statistical_summary = df.describe().to_string()

                prompt = self.generate_prompt(
                    csv_head=csv_head,
                    column_details=column_details,
                    statistical_summary=statistical_summary
                )
                
                llm_response = self.llm.invoke(prompt)
                analysis["ai_insights"] = str(llm_response.content if hasattr(llm_response, 'content') else llm_response)
            except Exception as e:
                logger.error(f"AI analysis failed: {str(e)}")
                analysis["ai_insights"] = "AI analysis could not be generated due to an error."

            # Generate visualizations
            try:
                analysis["visualizations"] = self.generate_visualizations(df)
            except Exception as e:
                logger.error(f"Visualization generation failed: {str(e)}")
                analysis["visualizations"] = []

            # Verify JSON serialization before returning
            try:
                json.dumps(analysis, cls=CustomJSONEncoder)
            except Exception as e:
                logger.error(f"JSON serialization failed: {str(e)}")
                # Clean up any problematic values
                analysis = self.clean_for_json(analysis)
            
            return analysis
        except Exception as e:
            logger.error(f"Error in analyze_csv: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def clean_for_json(self, obj):
        """Recursively clean an object for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self.clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.clean_for_json(item) for item in obj]
        elif pd.isna(obj) or obj is np.nan:
            return None
        elif isinstance(obj, (np.integer, np.floating)):
            return None if pd.isna(obj) else float(obj)
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return None if pd.isna(obj) else obj.isoformat()
        else:
            try:
                json.dumps(obj)
                return obj
            except:
                return str(obj)