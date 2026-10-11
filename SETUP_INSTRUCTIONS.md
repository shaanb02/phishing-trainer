# 🚀 Phishing Trainer - Complete Setup Guide

## ✅ What I've Done For You

I've configured your app with:
- ✅ Fixed all bugs (undefined variables, tracking URLs, Flask-Login)
- ✅ Added dotenv support for environment variables
- ✅ Fixed email service bugs (Resend restriction removed)
- ✅ Created `.env.example` template
- ✅ Created `requirements.txt` with all dependencies

## 📋 Setup Steps (5 Minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask and related packages
- python-dotenv (for .env files)
- SendGrid and Resend (email services)
- All other required packages

### Step 2: Configure Email Service

**Choose ONE option below:**

---

#### Option A: Gmail (Easiest for Testing) ⭐ RECOMMENDED

**1. Get Gmail App Password:**
   - Go to: https://myaccount.google.com/security
   - Enable **2-Step Verification** (if not already on)
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and enter "Phishing Trainer"
   - Click "Generate"
   - Copy the 16-character password (it looks like: `abcd efgh ijkl mnop`)

**2. Create `.env` file** in your project root folder:

```bash
# Copy .env.example to .env
cp .env.example .env
```

**3. Edit `.env` file** and fill in your details:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
FROM_EMAIL=your-email@gmail.com
SESSION_SECRET=change-me-to-random-string
```

**Replace:**
- `your-email@gmail.com` with your Gmail address
- `abcdefghijklmnop` with your 16-char app password (no spaces!)

---

#### Option B: SendGrid (Better Deliverability)

**1. Sign up for SendGrid:**
   - Go to: https://sendgrid.com
   - Create free account (100 emails/day)
   - Verify your email address
   - Go to Settings → API Keys
   - Create new API key with "Mail Send" permissions
   - Copy the API key (starts with `SG.`)

**2. Create `.env` file:**

```env
SENDGRID_API_KEY=SG.your-actual-api-key-here
FROM_EMAIL=your-verified-email@domain.com
SESSION_SECRET=change-me-to-random-string
```

---

#### Option C: Resend (Modern, Developer-Friendly)

**1. Sign up for Resend:**
   - Go to: https://resend.com
   - Create account (100 emails/day free)
   - Go to API Keys
   - Create new API key
   - Copy the API key (starts with `re_`)

**2. Create `.env` file:**

```env
RESEND_API_KEY=re_your-actual-api-key-here
FROM_EMAIL=onboarding@resend.dev
SESSION_SECRET=change-me-to-random-string
```

---

#### Option D: Mailtrap (Testing Only - Fake Emails)

**Perfect for testing without sending real emails!**

**1. Sign up at https://mailtrap.io** (free)

**2. Get SMTP credentials from your inbox**

**3. Create `.env` file:**

```env
SMTP_SERVER=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USERNAME=your-mailtrap-username
SMTP_PASSWORD=your-mailtrap-password
FROM_EMAIL=test@example.com
SESSION_SECRET=change-me-to-random-string
```

**Note:** Emails won't go to real addresses, but you can see them in Mailtrap!

---

### Step 3: Run the Application

```bash
python main.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Debug mode: on
Database tables created successfully
```

### Step 4: Test Email Sending

1. Open browser: http://localhost:5000
2. Go to "Users" and add yourself as a test user
3. Go to "Templates" and select a template
4. Send to yourself
5. **Check your email!** (and spam folder)

---

## 🔍 Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
**Fix:** Run `pip install python-dotenv`

### "SMTPAuthenticationError" (Gmail)
**Fix:** 
- Make sure you're using App Password, not your regular Gmail password
- Check 2-Step Verification is enabled
- Remove all spaces from the app password

### "Connection refused" 
**Fix:**
- Check SMTP_SERVER and SMTP_PORT are correct
- Check firewall isn't blocking port 587

### Emails not arriving
**Fix:**
- Check spam/junk folder
- For Gmail: Check "All Mail" folder
- Verify FROM_EMAIL matches your SMTP_USERNAME
- Check logs for "Email sent successfully" message

### Still in development mode
**Fix:**
- Make sure `.env` file is in the project root folder (same folder as `main.py`)
- Check the file is named `.env` (not `.env.txt` or `.env.example`)
- Restart the Flask app after creating `.env`

---

## 📊 How to Know It's Working

### ✅ WORKING - You'll see in logs:
```
Email sent successfully to user@example.com
```
or
```
Email sent successfully to user@example.com via SendGrid (Status: 202)
```
or
```
Email sent successfully to user@example.com via Resend (ID: xxx)
```

### ❌ NOT WORKING - You'll see:
```
[DEVELOPMENT MODE] Would send email to user@example.com
```

---

## 🎯 Quick Checklist

Before testing:
- [ ] Installed all dependencies (`pip install -r requirements.txt`)
- [ ] Created `.env` file in project root
- [ ] Added email credentials to `.env`
- [ ] Changed SESSION_SECRET to a random string
- [ ] Restarted Flask app
- [ ] Added yourself as a user in the app
- [ ] Sent test email to yourself

---

## 💡 Pro Tips

1. **Test with yourself first** - Always send to your own email initially
2. **Check spam folder** - First emails often land in spam
3. **Use Mailtrap for dev** - Perfect for testing without spamming real inboxes
4. **Gmail limits** - Free Gmail has sending limits (~500/day)
5. **Production** - Use SendGrid/Resend for better deliverability

---

## 📁 File Structure

Your project should look like this:

```
PhishingTrainer/
├── .env                    ← YOU CREATE THIS (copy from .env.example)
├── .env.example           ← Template I created
├── requirements.txt       ← Dependencies I created
├── main.py
├── app.py                 ← Updated with dotenv
├── routes.py              ← Bug fixes applied
├── email_service.py       ← Bug fixes applied
├── models.py
├── tracking.py
├── ai_generator.py
├── templates/
├── static/
└── instance/
    └── phishing_training.db
```

---

## 🆘 Still Need Help?

If you're stuck, tell me:
1. Which email service you chose (Gmail/SendGrid/Resend/Mailtrap)
2. What error message you're seeing
3. What the logs say when you try to send

I'll help you troubleshoot! 🚀

---

## 🎉 Success!

Once you see "Email sent successfully" in the logs and the email arrives in your inbox, you're all set!

Next steps:
- Add more users
- Create custom templates
- Launch phishing campaigns
- Track results in the dashboard
