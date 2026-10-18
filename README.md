# smart-traffic-management-system-
Smart Parking Violation – Traffic Violation & Fine Management System
Project Overview:
The Smart Parking Violation – Traffic Violation & Fine Management System is a desktop application built with Python. It helps an administrator register vehicles, record traffic violations, calculate fines, track payment status, identify repeat offenders, and generate reports.
The application uses Tkinter for the graphical user interface and SQLite for storing vehicle and violation records locally.
Features:
- Dashboard:
  - View the number of registered vehicles and recorded violations.
  - See pending fines and collected fines.
  - View recent violations and repeat-offender alerts.
- Vehicle Management:
  - Add, edit, and delete vehicle records.
  - Store registration number, owner name, vehicle type, contact number, and license number.
  - Search vehicles by registration number, owner, contact number, or license number.
  - Filter by vehicle type and sort the list.
  - Display each vehicle's violation count.
- Violation Management:
  - Record a violation for a registered vehicle.
  - Store the violation date and location.
  - Automatically assign the configured fine and priority.
  - Search recorded violations.
  - View a vehicle's violation history.
- Fine Management:
  - View pending and paid fines.
  - Mark a selected fine as paid.
  - View the total pending amount and collected amount.
- Analytics:
  - Review total fines and violations.
  - Identify the most common violation type.
  - Flag vehicles with two or more recorded violations.
- Reports and Export:
  - Generate a monthly summary.
  - Export violation records to a CSV file that can be opened in spreadsheet software.
Technologies Used:
- Python — application logic
- Tkinter / ttk — desktop graphical user interface
- SQLite (sqlite3) — local database
- CSV (csv) — export violation records
- datetime — date and time handling
All modules used by the current source file are part of Python's standard library, so no third-party package installation is normally required.
Fine Rules:
The application uses the following configured fines and priorities:
Violation	Fine	Priority
Over-speeding	    ₹1,000	High
No helmet   	    ₹500	  Medium
Signal violation	₹1,000	High
Wrong parking   	₹500	  Low
No seat belt    	₹500	  Medium

How to Use the Application:
1. Register a vehicle: Open Vehicles and select Add Vehicle. Enter its registration number, owner's name, and vehicle type. Contact and license details are optional.
2. Record a violation: Open Violations and select Record Violation. Enter a registered vehicle's registration number, choose a violation type, check the date, and enter the location.
3. Review fines: Open Fine Management/Fines, select a fine, and choose Mark Selected as Paid when payment has actually been received.
4. Check analytics: Open Analytics to review totals and repeat-offender information.
5. Generate a monthly report: Open Reports, enter a month in YYYY-MM format (for example, 2026-10), and select Generate Report.
6. Export records: In Reports, select Export All Violations. The application writes traffic_violations_export.csv to its current working directory.

7. Database Information:
The application creates a local SQLite database named traffic_violation.db automatically. It contains these tables:
- vehicles — vehicle registration, owner, type, contact, and license details.
- violations — violation ID, vehicle registration, violation type, date, location, fine, payment status, and priority.
The database is stored locally; the current application does not require a remote database server or internet connection.
Troubleshooting
- Python command not found: Install Python and enable the option to add Python to PATH, or try the Windows py command.
- Application window does not open: Run the command from a terminal and read any error message shown there. Tkinter requires a graphical desktop environment.
- Vehicle registration already exists: Each vehicle registration number must be unique.
- Cannot record a violation: Register the vehicle first and use its registration number.
- Records seem missing: Check that you are running the script from the same working directory, because the database is created relative to that directory.
- CSV file is not where expected: The export is saved in the application's current working directory.

- Limitations:
- The project is a local desktop prototype, not an online or multi-user system.
- Marking a fine as paid updates the application's database; it does not process an actual online payment.
- The current export feature exports violation records to CSV.
- Fine amounts and priority levels are fixed in the source code.
- The application does not connect to a government traffic database or automatically detect violations.

- Future Enhancements:
- Add administrator login and role-based access.
- Add charts and more detailed date-based analytics.
- Add printable fine receipts and PDF reports.
- Add database backup and restore tools.
- Add optional online payment integration and payment verification.
- Add audit logs and stronger validation for production use.

- Disclaimer:
This project is intended for learning, demonstration, and academic use. Verify legal fine amounts, protect personal information, and add appropriate security controls before using it with real vehicle-owner data.
  


A vehicle is classified as a repeat offender when it has two or more recorded violations.
These are the example rules configured in this project. They should be checked against the applicable local regulations before real-world use.
