import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDkS__6-JMonqXzezWjDRbsgvVN6xjhjBI",
  authDomain: "hackathon2025-58340.firebaseapp.com",
  projectId: "hackathon2025-58340",
  storageBucket: "hackathon2025-58340.firebasestorage.app",
  messagingSenderId: "343910704855",
  appId: "1:343910704855:web:90d641be2741b48939f292",
};

// Initialize Firebase app and Auth
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

export default app;
