# How to Get Firebase Token for Testing

## Option 1: Use Test Mode (Easiest - For Development Only)

I've added a test bypass to your authentication middleware. **This is for development only and should be removed in production!**

### Quick Test Setup:

1. Your `.env` file now has `TEST_MODE=true`
2. In Postman, use this token: `test_token`
3. Set Authorization header: `Bearer test_token`

### Postman Setup:

- Set collection variable `access_token` to: `test_token`
- All authenticated requests will work with this token

**⚠️ IMPORTANT: Remove `TEST_MODE=true` from .env before deploying to production!**

---

## Option 2: Generate Real Firebase Token (Recommended for Production Testing)

### Step 1: Get Your Firebase Config

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings → General → Your apps
4. Copy the Firebase config object

### Step 2: Update the HTML Token Generator

1. Open `firebase_token_generator.html`
2. Replace the `firebaseConfig` object with your actual config:
   ```javascript
   const firebaseConfig = {
     apiKey: "your-actual-api-key",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-actual-project-id",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "your-actual-app-id",
   };
   ```

### Step 3: Enable Google Sign-In

1. In Firebase Console → Authentication → Sign-in method
2. Enable "Google" provider
3. Add your domain to authorized domains

### Step 4: Generate Token

1. Open `firebase_token_generator.html` in a web browser
2. Click "Sign in with Google"
3. Complete Google authentication
4. Copy the generated token
5. Use this token in Postman

---

## Option 3: Use Firebase Admin SDK (For Automated Testing)

Create a test script to generate tokens programmatically:

```python
# test_token_generator.py
import firebase_admin
from firebase_admin import credentials, auth
import json

# Initialize Firebase Admin
cred = credentials.Certificate('./service-account.json')
firebase_admin.initialize_app(cred)

# Create a custom token for testing
uid = 'test_user_123'
custom_token = auth.create_custom_token(uid)

print("Custom Token:", custom_token.decode('utf-8'))

# You can also create a token with custom claims
custom_claims = {
    'email': 'test@example.com',
    'name': 'Test User'
}
custom_token_with_claims = auth.create_custom_token(uid, custom_claims)
print("Token with Claims:", custom_token_with_claims.decode('utf-8'))
```

Run this script to generate tokens for testing.

---

## Option 4: Use Firebase REST API

You can also get tokens using Firebase REST API:

```bash
# Exchange custom token for ID token
curl -X POST \
  'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=YOUR_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "token": "YOUR_CUSTOM_TOKEN",
    "returnSecureToken": true
  }'
```

---

## Recommended Testing Flow

### For Development:

1. Use **Option 1** (Test Mode) for quick API testing
2. Set `TEST_MODE=true` in .env
3. Use `test_token` as your bearer token

### For Integration Testing:

1. Use **Option 2** (HTML Generator) or **Option 3** (Admin SDK)
2. Generate real Firebase tokens
3. Test with actual authentication flow

### For Production:

1. **Remove** `TEST_MODE=true` from .env
2. Use only real Firebase tokens
3. Ensure proper security measures

---

## Security Notes

- **Never commit** `TEST_MODE=true` to production
- **Never expose** Firebase config with sensitive keys
- **Always validate** tokens in production
- **Use HTTPS** in production environments
- **Rotate keys** regularly

---

## Troubleshooting

### Common Issues:

1. **"Invalid authentication token"**

   - Check if TEST_MODE is enabled
   - Verify token format (should be `Bearer token`)
   - Ensure Firebase config is correct

2. **"Token expired"**

   - Firebase tokens expire after 1 hour
   - Generate a new token
   - Use refresh tokens for long-running tests

3. **"User not found"**

   - Ensure user exists in Firebase Auth
   - Check if custom claims are properly set

4. **CORS issues in HTML generator**
   - Serve HTML file from a web server
   - Add your domain to Firebase authorized domains
