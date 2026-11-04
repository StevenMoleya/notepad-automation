# Python Notepad Automation with CI/CD

A Windows-based desktop automation project built with Python. The application automates Notepad startup and shutdown, sends email notifications, records execution activities and generates reports.

The project also demonstrates automated testing and CI/CD using GitHub Actions.

## Features

- **Desktop automation:** Automatically starts and stops Notepad at configured times.
- **Task scheduling:** Uses Windows Task Scheduler to execute the Python automation.
- **Email notifications:** Sends Gmail notifications when automation events occur.
- **Process monitoring:** Uses `psutil` to monitor running processes.
- **Logging:** Records automation activities and execution events.
- **Report generation:** Generates a report containing automation execution details.
- **Automated testing:** Uses pytest to validate application functionality.
- **Continuous Integration:** GitHub Actions checks Python syntax and executes automated tests.
- **Continuous Delivery:** Automatically packages the application and publishes GitHub releases.

## Technologies Used

| Technology             | Purpose                         |
| ---------------------- | ------------------------------- |
| Python                 | Automation and scripting        |
| PowerShell             | Windows command-line operations |
| Windows Task Scheduler | Scheduled execution             |
| psutil                 | Process monitoring              |
| SMTP                   | Email notifications             |
| python-dotenv          | Environment configuration       |
| pytest                 | Automated testing               |
| Git                    | Version control                 |
| GitHub Actions         | CI/CD automation                |

## Project Structure

```text
notepad-automation/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── test/
│   └── test_email_notification.py
│
├── notepad_report.py
├── notepad_automation.py
├── email_notification.py
├── requirements.txt
├── .env
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/StevenMoleya/notepad-automation.git
```

### 2. Navigate to the project directory

```bash
cd notepad-automation
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project directory.

Configure the following environment variables:

```env
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=recipient@gmail.com

START_TIME=08:15
STOP_TIME=08:20
```

Use a Gmail App Password rather than your normal Gmail password.

**Security:** Never upload your `.env` file or email credentials to GitHub.

## Running the Automation

Run the main automation script:

```bash
python notepad_report.py
```

Windows Task Scheduler can also be configured to launch the script automatically.

The schedule configured in `.env` determines when Notepad starts and stops.

## Running Automated Tests

Execute:

```bash
python -m pytest -v
```

The tests validate the email notification functionality without sending real emails.

## CI/CD Pipeline

The project uses GitHub Actions to automate code validation and release publishing.

### Continuous Integration (CI)

Triggered by pushes to the `main` branch and pull requests targeting `main`.

The pipeline:

1. Checks out the repository.
2. Sets up Python.
3. Installs project dependencies.
4. Validates Python syntax.
5. Executes automated pytest tests.

### Continuous Delivery (CD)

Triggered when a version tag beginning with `v` is pushed.

For example:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The release workflow:

1. Runs the validation job.
2. Packages the application files into a ZIP archive.
3. Publishes a GitHub release with the ZIP attachment.

## Releases

The project has an initial release:

**Version:** v1.0.0

[View GitHub Releases](https://github.com/StevenMoleya/notepad-automation/releases)

## Future Improvements

- Expand automated test coverage.
- Improve exception handling and logging.
- Add additional automation functionality.
- Improve application configuration and documentation.

## Author

**Steven Moleya**

[GitHub](https://github.com/StevenMoleya)

[LinkedIn](https://linkedin.com/in/steven-moleya)
