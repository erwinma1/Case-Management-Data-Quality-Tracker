# Case-Management-Data-Quality-Tracker


Overview

The Law Manager Data Quality Tracker is a semi-automated reporting pipeline used to monitor and quantify data quality corrections made by a Data Quality team within a legal case management system.

The project extracts audit data from Law Manager tables, aggregates corrections made by team members, and produces monthly summary statistics used to track the progress of systemic error remediation.

The tracker was designed to support operational oversight of case data affecting attorney case management and internal dashboards.

As of March 2026, the Data Quality team:

Maintains approximately 29,000 active cases

Processes 30,000–40,000 new case appearances per month

Corrects roughly 1,500 data errors per month

These corrections primarily involve:

Court date updates

Case appearance corrections

Matter updates

Initial top charge corrections

Based on these figures, the system experiences an estimated 4–5% error rate, requiring ongoing monitoring and correction.

Project Purpose

This tool provides a way to:

Track systemic data errors over time

Measure progress of the Data Quality team

Monitor operational workload

Identify high-priority correction areas affecting legal case workflows

Without historical snapshots, audit logs are overwritten when records are edited by other users. This tracker preserves historical correction activity by periodically capturing snapshots of updates.

Data Pipeline Architecture

The workflow consists of a simple SQL → Python → Excel reporting pipeline.

Law Manager Database
        │
        ▼
SQL Extraction (monthly snapshot)
        │
        ▼
Archived Snapshot Files (.xlsx)
        │
        ▼
Python Processing Script
  • Concatenate historical snapshots
  • Clean timestamps
  • Remove duplicate updates
  • Generate monthly pivot summaries
        │
        ▼
Excel Dashboard Output
Data Sources

The tracker monitors updates to three core Law Manager tables:

Table	Description
Matter	Case-level information updates
Case Appearance	Court appearance updates
Init Top Charge	Initial charge corrections

Updates are identified using audit fields such as:

updated_by

added_by

date_updated

date_added

Methodology
1. SQL Data Extraction

A SQL script extracts updates made by Data Quality team members from Law Manager.

The query captures updates using:

updated_by
added_by

These fields represent the most recent editor of a record.

Snapshots should be taken every 2–4 weeks to ensure updates are captured before they are overwritten by subsequent edits.

2. Snapshot Archiving

Each SQL extract is saved as a timestamped file inside an archive directory.

Example:

Archive/
    snapshot_2025_11.xlsx
    snapshot_2025_12.xlsx
    snapshot_2026_01.xlsx

These archived snapshots form a historical dataset.

3. Python Data Processing

The Python script performs several processing steps:

File ingestion

All snapshot files are read from the archive folder.

for file in os.listdir(directory):

Each dataset is appended to a list and concatenated into a single dataframe.

Data cleaning

The script standardizes timestamps using pandas:

pd.to_datetime()

Duplicate edits are removed using:

date_updated + updated_by

This combination acts as a unique identifier for corrections.

Monthly aggregation

Corrections are aggregated by month using pivot tables.

Example:

pivot_table(index='update_date', aggfunc='sum')

This produces monthly totals of corrections made by the team.

4. Reporting Output

The script exports summarized datasets to an Excel dashboard.

Output sheets include:

Case Appearance corrections

Matter corrections

Initial Top Charge corrections

The final output file provides a monthly view of correction activity.

Example Output

Typical outputs include:

Monthly correction counts

Trend analysis of error corrections

Operational workload metrics

These reports help management track whether the backlog of historical errors is decreasing and whether incoming error rates are stable.

Known Data Limitations

Because Law Manager audit fields only store the most recent editor, corrections can be overwritten by later edits from other users.

This means:

The tracker provides a conservative estimate of corrections

Earlier corrections may be lost if snapshots are not taken regularly

To minimize this issue, snapshots should be extracted biweekly or monthly.

Future Improvements

Potential enhancements include:

Automation

Automating SQL extraction using scheduled jobs

Eliminating manual snapshot collection

Visualization

Integration with Power BI or other BI tools to provide:

Real-time dashboards

Correction trend visualization

error inflow vs outflow monitoring

Expanded Monitoring

Additional SQL queries may be added to monitor:

New data migration workflows

Salesforce integration quality checks

Additional Law Manager tables

Requirements

Python packages required:

pandas
openpyxl
os

Install dependencies:

pip install pandas openpyxl
How to Run

1️⃣ Extract monthly snapshot data from SQL
2️⃣ Save the files in the archive directory

/LM Data Quality Tracker/Archive

3️⃣ Run the Python script

python data_quality_tracker.py

4️⃣ The script generates an Excel dashboard with aggregated statistics.

Contact

For questions about the tracker or methodology:

ema@legal-aid.org
What This Project Demonstrates

This project illustrates:

Data pipeline construction

Data quality monitoring

Python automation for operational analytics

Audit log analysis

Historical snapshot reconstruction

Pivot-based reporting workflows
