\# 🤖 AI-Powered ETL Automation Pipeline



An AI-powered ETL automation workflow built with \*\*n8n\*\* to automatically clean, validate, classify, and organize messy student enrollment data into structured Excel outputs.



\---



\## 📌 Project Overview



Student enrollment data collected through online forms can often contain inconsistent names, invalid email addresses, missing phone numbers, inconsistent course names, and incorrectly formatted dates.



Manually cleaning and categorizing this data is time-consuming and error-prone.



This project solves that problem by combining \*\*ETL automation, AI-powered data cleaning, conditional routing, and Excel generation\*\* into a single automated workflow using \*\*n8n\*\*.



The workflow takes raw student enrollment data as input, processes each record using an LLM, applies validation and classification rules, and generates organized output files based on the processed results.



\---



\## 🎯 Problem Statement



The academy receives raw student enrollment data regularly from online forms.



The incoming data is often:



\- Inconsistent

\- Incomplete

\- Poorly formatted

\- Containing invalid email addresses

\- Missing phone numbers

\- Inconsistent city and course names

\- Stored in different date formats



The goal is to build an automated ETL pipeline that can:



1\. Extract the raw student data.

2\. Process each student record individually.

3\. Use AI to clean and standardize the data.

4\. Validate important fields.

5\. Categorize students based on their city.

6\. Categorize students based on email validity.

7\. Generate clean and structured output files.



The source dataset contains \*\*50 student enrollment records\*\* with intentionally messy, real-world data. :contentReference\[oaicite:0]{index=0}



\---



\## 💡 Solution



To solve the problem, an automated workflow was designed using \*\*n8n\*\*.



The workflow combines traditional ETL operations with an LLM to automatically transform the raw data.



\### High-Level Process



```text

Raw CSV Data

&#x20;    │

&#x20;    ▼

Extract Data

&#x20;    │

&#x20;    ▼

Process Each Student

&#x20;    │

&#x20;    ▼

AI Data Cleaning

&#x20;    │

&#x20;    ▼

Parse Structured AI Response

&#x20;    │

&#x20;    ▼

Apply Business Rules

&#x20;    │

&#x20;    ▼

Filter by City

&#x20;    │

&#x20;    ▼

Filter by Email Validity

&#x20;    │

&#x20;    ▼

Merge Results

&#x20;    │

&#x20;    ▼

Generate Excel Output

🏗️ Workflow Architecture

&#x20;                   ┌─────────────────┐

&#x20;                   │    CSV Input    │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │ Extract From    │

&#x20;                   │      File       │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │ Loop Over Items │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │  Basic LLM      │

&#x20;                   │     Chain       │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │ JavaScript Code │

&#x20;                   │ Parse Response  │

&#x20;                   └────────┬────────┘

&#x20;                            │

&#x20;                            ▼

&#x20;                   ┌─────────────────┐

&#x20;                   │ City Routing    │

&#x20;                   │     Switch      │

&#x20;                   └───────┬─┬───────┘

&#x20;                           │ │

&#x20;                  ┌────────┘ └────────┐

&#x20;                  ▼                   ▼

&#x20;              Chennai            Other Cities

&#x20;                  │                   │

&#x20;                  ▼                   ▼

&#x20;             Email Filter        Email Filter

&#x20;                  │                   │

&#x20;            ┌─────┴─────┐       ┌────┴─────┐

&#x20;            ▼           ▼       ▼          ▼

&#x20;          Valid       Invalid  Valid      Invalid

&#x20;            │           │       │          │

&#x20;            └───────────┴───────┴──────────┘

&#x20;                        │

&#x20;                        ▼

&#x20;                      Merge

&#x20;                        │

&#x20;                        ▼

&#x20;                 Convert to XLSX

&#x20;                        │

&#x20;                        ▼

&#x20;                 Clean Output

🤖 AI-Powered Data Cleaning



Each student record is sent to the LLM for automated cleaning and standardization.



The AI performs the following transformations:



Name



Converts names into Title Case.



Email



Validates the email address.



If the email does not contain @ or does not have a .com or .in ending, it is marked as:



INVALID\_EMAIL

Phone



If the phone number is empty or contains fewer than 10 digits, it is marked as:



MISSING

Course



Course names are standardized to:



Python

Machine Learning

Data Science

Fee Paid



Payment status is converted into Boolean values:



yes / YES → true

no / NO   → false

City



City names are converted to Title Case.



Missing city values are represented as:



UNKNOWN

Enrolled Date



Dates are standardized into:



YYYY-MM-DD



These transformation rules are implemented through the AI cleaning stage of the workflow.



🔀 Data Classification



After the AI cleans each record, the workflow applies business rules to classify the students.



Location Classification

City = Chennai

&#x20;       ↓

Chennai



City ≠ Chennai

&#x20;       ↓

Other Cities

Email Classification

Valid Email

&#x20;    ↓

VALID EMAIL



Invalid Email

&#x20;    ↓

INVALID EMAIL



The two classifications are combined to produce four final categories.



📊 Output Categories



The workflow produces four processed datasets:



Category	Condition

chennai\_valid\_email	Chennai + Valid Email

chennai\_invalid\_email	Chennai + Invalid Email

other\_valid\_email	Other City + Valid Email

other\_invalid\_email	Other City + Invalid Email



These four combinations represent the final business classification of the processed student records.



📁 Final Output



After classification, the results are consolidated and converted into Excel (XLSX) format.



The workflow therefore eliminates the need to manually:



Clean individual records

Validate emails

Categorize students

Separate datasets

Export multiple results



Instead, the complete process is automated through the n8n workflow.



🔄 Key Workflow Components

Component	Role

CSV Input	Provides raw student enrollment data

Extract From File	Reads and extracts CSV records

Loop Over Items	Processes records individually

Basic LLM Chain	Performs AI-powered data cleaning

JavaScript Code	Parses the AI-generated JSON

Switch Nodes	Applies classification rules

Merge	Combines processed outputs

Convert to File	Generates Excel output



The workflow follows the required ETL and AI-processing architecture defined for the project.



🛠️ Technology Stack

n8n – Workflow automation and orchestration

LLM / Generative AI – Data cleaning and standardization

JavaScript – Processing and parsing structured AI responses

CSV – Raw input data

Excel / XLSX – Processed output

🚀 How the Workflow Works

Step 1 – Input



Raw student enrollment data is provided as a CSV file.



Step 2 – Extraction



The CSV file is read and converted into individual records.



Step 3 – AI Processing



Each student record is sent to the LLM for cleaning and standardization.



Step 4 – Response Parsing



The AI response is parsed into structured JSON data.



Step 5 – Classification



The workflow checks:



Student city

Email validity

Step 6 – Routing



Records are automatically routed into the appropriate category.



Step 7 – Consolidation



The processed results are merged.



Step 8 – Output



The final data is converted into an Excel file.



🎓 Project Context



This project was developed as part of the CAIE Course Program – AI Automation / ETL Pipeline Challenge at Social Eagle AI Academy.



The project focuses on applying AI and workflow automation to a practical data-engineering problem rather than performing the ETL process manually.



📂 Project Structure

AI Automation/

│

├── ETL\_AI\_Automation.json

└── README.md

ETL\_AI\_Automation.json



Exported n8n workflow containing the complete automation pipeline.



README.md



Documentation for the project, including the problem, solution, workflow architecture, AI transformation logic, and output classification.



🌟 Key Takeaways



This project demonstrates how Generative AI and workflow automation can work together to build an intelligent ETL pipeline.



The workflow combines:



ETL

&#x20;+

Generative AI

&#x20;+

Data Validation

&#x20;+

Conditional Logic

&#x20;+

Workflow Automation

&#x20;=

Automated Data Processing



The result is a repeatable pipeline that transforms messy raw enrollment data into clean, categorized, and structured output with minimal manual intervention.



🔮 Future Enhancements



Potential improvements include:



Connect directly to Google Sheets or Google Forms

Automate scheduled data ingestion

Add database storage

Add error handling and retry mechanisms

Add email notification after processing

Add automated quality reports

