# APEX Access Control System

## Overview
The APEX Access Control System is a web-based platform built using Flask for managing users, their profiles, and administrative functions. It offers secure user authentication, role-based access control, and profile management. The application integrates with a MySQL database and allows admins to manage user accounts effectively.

---

## Features

- **User Authentication**:
  - Secure login and registration.
  - Password hashing using SHA-256.
- **Role-Based Access Control**:
  - Admin-specific features such as managing users.
  - Protected routes for authenticated users.
- **Profile Management**:
  - Users can update their personal information and profile pictures.
- **File Uploads**:
  - Support for profile picture uploads (PNG, JPG, JPEG).
  - File size limit of 5 MB.
- **Admin Functionalities**:
  - Add, edit, and delete users.
  - View a list of all users.
- **Session Management**:
  - Session timeout set to 7 days.

---

## Security Features

- **Password Hashing**:
  - User passwords are hashed with SHA-256 before storing in the database.
- **Role-Based Access**:
  - Admin-only routes are protected with a decorator (`@admin_required`).
  - User-only routes require authentication (`@login_required`).
- **Session Management**:
  - Sessions are secured with a secret key and have a defined lifetime.

---

## Prerequisites

- Python 3.7+
- MySQL Database

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/apex-access-control.git
   cd apex-access-control
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL Database**:
   - Create a MySQL database named `access_control`.
   - Import the SQL schema from `schema.sql` into your database.
   - Update the `connectSQL` function in `app.py` with your MySQL credentials.

5. **Set Up Uploads Directory**:
   ```bash
   mkdir -p static/uploads
   ```

6. **Run the Application**:
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000/`.

---

## Usage

1. **Login**:
   - Access the login page at `/login`.
   - Admins can log in to access user management features.

2. **User Management (Admin Only)**:
   - View all users at `/users`.
   - Add a new user at `/add_user`.
   - Edit user details at `/edit_user/<user_id>`.
   - Delete a user via the delete button on the users list page.

3. **Profile Management**:
   - View and update your profile at `/profile`.
   - Upload a profile picture or change personal details.

4. **Logout**:
   - Log out using the `/logout` endpoint.

---

## Folder Structure

```
├── app.py               # Main application file
├── requirements.txt     # Python dependencies
├── static/              # Static files (CSS, images, uploads)
│   └── uploads/         # Uploaded profile pictures
├── templates/           # HTML templates
├── schema.sql           # Database schema
```

## Future Enhancements

- Integrate OAuth for third-party authentication.
- Implement multi-factor authentication.
- Add logging and error monitoring.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to propose changes.

---

## Contact

For questions or support, please contact:

- **Name**: [Nerisa Valle]
- **Email**: [nevalle@my.cspc.edu.ph]
- **GitHub**: [https://github.com/niwiisaaa]

- **Name**: [Krizia Belle Nanale]
- **Email**: [krnanale@my.cspc.edu.ph]
- **GitHub**: [https://github.com/kzzZia]