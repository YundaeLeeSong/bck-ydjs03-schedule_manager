# Tutoring Scheduler Manager

A desktop application designed to streamline the management of tutoring students, scheduling sessions, creating Zoom meetings automatically, and sending professional email reports. Built with **Python** and **PySide6**.

## System Design

The application follows a clean, modular architecture that separates the User Interface (UI), Data Management, and External Service integrations. This ensures maintainability, scalability, and ease of testing.

### Architecture Overview

1.  **Application Layer (`tutor_schedular`)**:
    *   **Framework**: **PySide6** (Qt for Python).
    *   **Pattern**: Uses a **Stage/Scene** concept where `StageMain` (Window) manages transitions between different **Views** using a `QStackedWidget`.
    *   **Naming Convention**: Views are prefixed with `View` (e.g., `ViewWelcome`) and reside in modules prefixed with `view_`.
    *   **Entry Point**: The package is executable (`python -m tutor_schedular`), managed by `app.py`.

2.  **Data Layer (`file_manager`)**:
    *   **Pattern**: **Singleton**.
    *   **Responsibility**: Centralizes all file I/O operations. It ensures that only one instance manages the data consistency for students, schedules, and templates across the application.

3.  **Service Layer (`gmailproxy`, `zoomproxy`)**:
    *   **Pattern**: **Proxy / Adapter**.
    *   **Responsibility**: Abstracts the complexity of third-party APIs (Gmail SMTP, Zoom API). The core application interacts with clean interfaces (`IEmailService`, `IZoomService`) rather than raw API calls.

---

## Library Documentation (Custom Packages)

The system is composed of several standalone packages located in `src/main/python`.

### 1. File Manager (`file_manager`)
A robust utility for handling local data persistence and resource management.

*   **Key Class**: `FileManager` (Singleton)
*   **Functionality**:
    *   **Initialization**: Automatically creates required directory structure (`resources/schedules`, `resources/students`, `resources/templates`).
    *   **Data Persistence**: Loads and saves JSON data for students and schedules.
    *   **Templates**: Loads HTML templates for email reports.
    *   **Exports**: Generates paths for exporting files like `.ics` calendars.

### 2. Gmail Proxy (`gmailproxy`)
A wrapper around Python's `smtplib` to facilitate secure email transmission.

*   **Key Classes**: `GmailProxy`, `RealGmailService`
*   **Interfaces**: `IEmailService`
*   **Features**:
    *   Supports SSL and STARTTLS security.
    *   Handles HTML body content and file attachments.
    *   Robust error handling and logging.
*   **Environment Variables**:
    *   `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`

### 3. Zoom Proxy (`zoomproxy`)
An integration client for the Zoom Server-to-Server OAuth API.

*   **Key Classes**: `ZoomProxy`, `RealZoomService`
*   **Interfaces**: `IZoomService`
*   **Features**:
    *   **Authentication**: Handles OAuth token acquisition and management.
    *   **Meeting Management**: Creates scheduled meetings with topics, start times, and durations.
    *   **Timezone Handling**: Converts local time to UTC for API consistency.
*   **Environment Variables**:
    *   `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET`

### 4. Tutor Scheduler (`tutor_schedular`)
The core UI application package.

*   **Components**:
    *   `StageMain`: The main window container.
    *   `ViewWelcome`: Landing screen.
    *   `ViewStudentManager`: CRUD interface for students and email reporting.
    *   `ViewScheduleManager`: Interface for managing sessions and syncing with Zoom.
    *   `utils`: Helper functions (e.g., `get_status_emoji`).

---

## Setup & Usage

### Prerequisites
*   Python 3.8+
*   Active Zoom Server-to-Server OAuth application.
*   Gmail account with App Password enabled (if using Gmail).

### Installation
Use the provided `runner.py` utility for easy setup.

```bash
# 1. Initialize environment
python runner.py init

# 2. Build/Install dependencies (creates requirements.txt and installs them)
python runner.py build
```

### Configuration
Create a `.env` file in the project root:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_SECURITY=SSL
SMTP_SENDER=your_email@gmail.com

# Zoom Configuration
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
```

### Running the Application
```bash
python runner.py run
```
Or directly:
```bash
python -m src.main.python.tutor_schedular
```

### Running Tests
The project employs **Test-Driven Development (TDD)** for its libraries. Unit tests mock external services to ensure reliability without network calls.

```bash
python runner.py test
```
