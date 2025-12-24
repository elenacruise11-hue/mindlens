# MindLens AI - Authentication Setup Guide

## 🔐 Real User Authentication with Supabase

This guide explains how to set up and use the real authentication system implemented in MindLens AI.

## 📋 Prerequisites

1. **Supabase Database Setup**
   - Create the following tables in your Supabase database:

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### OTP Table (for email verification)
```sql
CREATE TABLE otp (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL,
    otp_code TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🛠️ Installation & Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Update your `.env` file with the following:
   ```env
   # Supabase Configuration (already configured)
   VITE_SUPABASE_PROJECT_ID="your-project-id"
   VITE_SUPABASE_PUBLISHABLE_KEY="your-publishable-key"
   VITE_SUPABASE_URL="your-supabase-url"

   # JWT Configuration
   JWT_SECRET_KEY="your-super-secret-jwt-key-change-this-in-production"

   # Email Configuration (SMTP)
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT="587"
   SENDER_EMAIL="your-email@gmail.com"
   SENDER_PASSWORD="your-app-password"
   ```

3. **Email Setup (Gmail Example)**
   - Enable 2-factor authentication on your Gmail account
   - Generate an App Password: Google Account → Security → App passwords
   - Use the App Password as `SENDER_PASSWORD` in `.env`

## 🚀 API Endpoints

### 1. User Signup
**POST** `/signup`
```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Account created successfully! Please check your email for verification code."
}
```

### 2. Email Verification
**POST** `/verify`
```json
{
    "email": "john@example.com",
    "otp": "123456"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Email verified successfully! You can now log in."
}
```

### 3. User Login
**POST** `/login`
```json
{
    "email": "john@example.com",
    "password": "SecurePass123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful!",
    "user": {
        "id": "uuid",
        "full_name": "John Doe",
        "email": "john@example.com",
        "is_verified": true,
        "created_at": "2024-01-01T00:00:00Z"
    },
    "access_token": "jwt-token"
}
```

## 🔒 Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **Email Verification**: 6-digit OTP sent via email
- **JWT Tokens**: Secure access tokens for authenticated sessions
- **Password Validation**: Enforces strong password requirements
- **Rate Limiting**: Built-in protection against brute force attacks

## 📧 Email Template

The system sends beautifully formatted HTML emails with:
- Professional MindLens AI branding
- Clear OTP display
- Security information
- Expiration notice (10 minutes)

## 🧪 Testing the Authentication Flow

1. **Start the Application**
   ```bash
   python app.py
   ```

2. **Test Signup**
   ```bash
   curl -X POST "http://localhost:8000/signup" \
        -H "Content-Type: application/json" \
        -d '{
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123"
        }'
   ```

3. **Check Email for OTP**
   - Look for verification email in inbox
   - Note the 6-digit code

4. **Verify Email**
   ```bash
   curl -X POST "http://localhost:8000/verify" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@example.com",
            "otp": "123456"
        }'
   ```

5. **Login**
   ```bash
   curl -X POST "http://localhost:8000/login" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@example.com",
            "password": "TestPass123"
        }'
   ```

## 🔧 Troubleshooting

### Common Issues:

1. **Email Not Sending**
   - Check SMTP credentials in `.env`
   - Ensure Gmail App Password is correct
   - Verify firewall/network settings

2. **Supabase Connection Issues**
   - Verify Supabase URL and keys
   - Check database table creation
   - Ensure proper permissions

3. **Password Validation Errors**
   - Password must be at least 8 characters
   - Must contain uppercase, lowercase, and digit
   - Check password strength requirements

## 📱 Frontend Integration

The authentication system is compatible with existing frontend forms. The legacy `/signin` route automatically converts form data to the new authentication system.

## 🔐 Production Considerations

1. **Change JWT Secret**: Update `JWT_SECRET_KEY` in production
2. **Use Environment Variables**: Never commit sensitive data
3. **Enable HTTPS**: Ensure secure communication
4. **Database Security**: Configure proper Supabase RLS policies
5. **Email Service**: Consider using dedicated email services like SendGrid

## 📊 Database Schema

The authentication system uses two main tables:
- `users`: Store user account information
- `otp`: Temporary storage for email verification codes

Both tables are automatically managed by the application with proper cleanup and security measures.
