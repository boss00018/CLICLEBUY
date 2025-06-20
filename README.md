# CIRCLEBUY

A modern web application for college/university students to buy and sell stationery, textbooks, and other academic tools. This platform includes real-time chat functionality between buyers and sellers.

## 🌟 Features

- **User Authentication**
  - Secure registration and login
  - Password strength meter
  - University-based accounts
  - Google OAuth integration

- **Product Management**
  - List items with images and descriptions
  - Categorized browsing
  - Mark items as sold
  - Manage your listings

- **Real-time Chat**
  - Instant messaging between buyers and sellers
  - Chat about specific products
  - Suggested message templates

- **Domain-Based Communities**
  - Automatic grouping by email domain
  - University-specific marketplaces
  - Community member listings

- **Modern UI/UX**
  - Animated backgrounds and transitions
  - Interactive elements
  - Responsive design for all devices
  - Real-time notifications

## 🚀 Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Real-time Communication**: WebSockets
- **UI Enhancements**: Animate.css, SweetAlert2
- **Authentication**: JWT, Google OAuth

## 📋 Setup and Installation

1. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Add Logo**
   ```
   Copy circlebuy.png to the static/ directory
   ```

3. **Configure Google OAuth**
   - Create a project in the [Google Developer Console](https://console.developers.google.com/)
   - Enable the Google+ API
   - Create OAuth credentials (Web application type)
   - Set the authorized redirect URI to `http://localhost:8000/auth/callback`
   - Copy `.env.example` to `.env` and fill in your Google OAuth credentials

4. **Run the Application (Development)**
   ```
   python run.py
   ```

5. **Access the Website**
   ```
   http://127.0.0.1:8000
   ```

## 🔒 Production Deployment

1. **Set Environment Variables**
   ```
   export SECRET_KEY="your-secure-secret-key"
   ```

2. **Run with Gunicorn (Production)**
   ```
   gunicorn -c gunicorn_config.py app:app
   ```

3. **Nginx Configuration (Optional)**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /ws {
           proxy_pass http://127.0.0.1:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

## 🧪 Testing and Security

1. **Run All Tests**
   ```
   python run_tests.py
   ```

2. **Security Check**
   ```
   python security_check.py
   ```

3. **Performance Tests**
   ```
   pytest tests/test_performance.py -v
   ```

4. **Load Tests**
   ```
   python tests/test_load.py
   ```

## 📱 Usage Guide

1. **Register** for an account with your university email or use Google Sign-In
2. **Browse** items by category or search for specific items
3. **List** your own items for sale with descriptions and images
4. **Chat** with sellers to arrange purchases
5. **Manage** your listings in the "My Products" section
6. **Connect** with your university community in the "My Community" section

## 🔮 Future Enhancements

- User ratings and reviews
- Advanced search filters
- In-app notifications
- Mobile app version
- Payment integration
- University verification

## 🔒 Security Features

- Rate limiting to prevent abuse
- Secure file uploads with validation
- CORS protection
- Secure password hashing
- JWT authentication
- Input validation
- Automatic data cleanup
- Domain-based isolation