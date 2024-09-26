# Cloud tools documentation

## Project Overview

Cloud Management Project is a Python application that allows users to manage resources across three cloud providers: Amazon Web Services (AWS), Google Cloud Platform (GCP), and Microsoft Azure. The goal of this project is to simplify virtual machine instance management, cost monitoring, and resource utilization in a single location by providing an interactive command-line interface.

## Features

- **Instance Management**: Allows you to list, create, start, stop and delete virtual machine instances on the three cloud platforms.
- **Resource Monitoring**: Provides the ability to monitor CPU, RAM and storage usage.
- **Cost Reports**: Monitors costs associated with cloud services in AWS.
- **Interactive Interface**: Presents an interactive menu to facilitate navigation and execution of actions.

## Required Libraries

To run this project, you will need to install the following Python libraries:

1. **Boto3**: To interact with AWS services.
   ```bash
   pip install boto3
   ```

2. **Google Cloud Compute**: To manage Google Cloud resources.
   ```bash
   pip install google-cloud-compute
   ```

3. **Azure SDK**: To manage Azure resources.
   ```bash
   pip install azure-identity azure-mgmt-compute azure-mgmt-network azure-mgmt-monitor
   ```

4. **Requests** (optional): If you need to make additional API calls or manage authentications more comprehensively.
   ```bash
   pip install requests
   ```

### Installation in a Virtual Environment

1. **Create a virtual environment**:
   ```bash
   python -m venv myenv
   ```

2. **Activate the virtual environment**:
   - On Windows:
     ```bash
     myenv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source myenv/bin/activate
     ```

3. **Install required libraries** as mentioned above.

## How to Use

1. **Credentials Configuration**:
   Before running the project, you need to configure your access credentials for each cloud provider. Credentials must be stored in environment variables:
   ```python
   os.environ['AWS_ACCESS_KEY_ID'] = 'YOUR_AWS_ACCESS_KEY'
   os.environ['AWS_SECRET_ACCESS_KEY'] = 'YOUR_AWS_SECRET_KEY'
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path_to_your_google_credentials.json'
   os.environ['AZURE_SUBSCRIPTION_ID'] = 'YOUR_AZURE_SUBSCRIPTION_ID'
   os.environ['AZURE_RESOURCE_GROUP'] = 'YOUR_AZURE_RESOURCE_GROUP'
   ```

2. **Run the Script**:
   After configuring your credentials, run the main script:
   ```bash
   python main.py
   ```

3. **Interaction with the Menu**:
   - The script will present a home menu where you can choose which cloud provider you want to manage (AWS, Google Cloud, Azure).
   - After selecting a provider,you will see a specific menu with options to list, create, start, stop and delete instances, as well as monitor resources and costs.

4. **Exit the Program**:
   To exit the program, select the corresponding option in the menu.

## Contribution

Contributions are welcome! If you have suggestions or improvements, feel free to open a pull request or issue in the repository.

## License

This project is licensed under the MIT License.