# HCS-Final-Project

## DESIGN OF A WEB-BASED REAL-TIME DATA MANAGEMENT AND ANALYTICS PLATFORM

This capstone project focuses on designing a web-based real-time logistics data management and analytics platform for Schweppes Zimbabwe Limited (SZL). This will replace the current inefficient, error-prone manual logistic management with a centralized automated platform. The system allows for real-time data logging, analytics, and visualization that shall be useful to distribution clerks, managers, and executives in decision-making. The transport logging, role-based access control, predictive analytics, and automated reporting will be integrated into the platform using an incremental development methodology. The platform’s design integrates modern technologies and data visualization tools to ensure scalability, security and usability

# Setup
## Setup a Conda environment ...

1. Install Miniconda by selecting the installer that fits your OS version. Once it is installed, you may have to restart your terminal (close it and open again).

2. Navigate to this directory in the terminal.

3. Run the following command to create the conda environment:

   ```bash
   conda env create -f environment.yml
   ```

4. Activate the environment:

   ```bash
   conda activate HCS-env
   ```

5. Run the Django development server:

   ```bash
   python manage.py runserver
   ```
