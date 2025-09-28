import { /* Link removed */ } from "react-router-dom";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const { googleLogin, loading, error } = useAuth();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 via-purple-50 to-blue-100 dark:from-gray-950 dark:via-purple-950 dark:to-indigo-950 p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-blue-400/30 to-purple-600/30 rounded-full blur-3xl"
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        />
        <motion.div
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-indigo-400/30 to-pink-600/30 rounded-full blur-3xl"
          animate={{ 
            scale: [1.2, 1, 1.2],
            rotate: [0, -180, -360],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md relative z-10"
      >
        <Card className="shadow-2xl border-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl">
          <CardHeader className="space-y-1 text-center pb-8">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg"
            >
              <motion.span 
                className="text-white font-bold text-2xl"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                L
              </motion.span>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <CardTitle className="text-3xl font-extrabold bg-gradient-to-r from-blue-700 to-purple-700 bg-clip-text text-transparent">
                Welcome to LearnHub
              </CardTitle>
              <CardDescription className="text-base mt-3 text-gray-600 dark:text-gray-400">
                Enter your credentials to access your learning dashboard ✨
              </CardDescription>
            </motion.div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Sign in with your Google account to access the dashboard.</p>
              </div>

              <div className="flex items-center justify-center">
                <button
                  onClick={() => googleLogin()}
                  className="flex items-center gap-3 px-4 py-2 border rounded-xl hover:shadow-md transition"
                  disabled={loading}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" className="w-5 h-5">
                    <path fill="#fbbc05" d="M43.6 20.5H42V20.5H24v7.5h11.3C34.3 31.5 29.6 35 24 35c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.9 1.1 8 2.9l5.5-5.5C33.6 4.9 29.1 3 24 3 12.9 3 3.7 12.2 3.7 23.3S12.9 43.7 24 43.7c11 0 20.3-9.1 20.3-20.3 0-1.4-.2-2.7-.7-3.9z"/>
                    <path fill="#ea4335" d="M6.3 14.3l6.4 4.7C14.9 16 19 13 24 13c3.1 0 5.9 1.1 8 2.9l5.5-5.5C33.6 4.9 29.1 3 24 3 15.6 3 8.2 7.6 6.3 14.3z"/>
                    <path fill="#34a853" d="M24 43.7c5.6 0 10.3-3.5 12.9-8.5H24v-7.5h19.2c.6 1.7.8 3.6.8 5.5 0 11-9.2 20.3-20.3 20.3-11.1 0-20.3-9.2-20.3-20.3 0-1.9.3-3.8.8-5.5l6.4 4.7C12.5 38.1 17.9 43.7 24 43.7z"/>
                    <path fill="#4285f4" d="M43.6 20.5H42V20.5H24v7.5h11.3C34.3 31.5 29.6 35 24 35v8.7c5.1 0 9.6-1.9 13.3-5.6 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0z"/>
                  </svg>
                  <span className="text-sm font-medium">Sign in with Google</span>
                </button>
              </div>
              {error && (
                <div className="text-sm text-red-600 mt-3 text-center">{error}</div>
              )}
            </div>

            {/* signup prompt removed - only Google sign-in is available */}

            {/* Removed duplicate Google sign-in button; single button above is used */}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}