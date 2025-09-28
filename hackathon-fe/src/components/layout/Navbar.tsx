import { useState } from "react";
import { Button } from "../ui/button";
import { Menu, Bell } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";
import { motion } from "framer-motion";

interface NavbarProps {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export default function Navbar({ toggleSidebar }: NavbarProps) {
  useAuth();
  const [notifications] = useState(3);
  
  return (
    <header className="h-16 border-b border-gray-200 dark:border-gray-800 px-6 flex items-center justify-between bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl shadow-sm">
      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon" 
          className="md:hidden hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl" 
          onClick={toggleSidebar}
        >
          <Menu />
        </Button>
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <motion.div
            className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-md"
            whileHover={{ rotate: 5, scale: 1.05 }}
          >
            <span className="text-white font-bold text-sm">L</span>
          </motion.div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Learning Platform
          </h1>
        </motion.div>
      </div>
      
      <div className="flex items-center gap-3">
        <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
          <Button variant="ghost" size="icon" className="relative rounded-xl hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50">
            <Bell size={18} />
            {notifications > 0 && (
              <motion.span 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                whileHover={{ scale: 1.1 }}
                className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center shadow-lg"
              >
                {notifications}
              </motion.span>
            )}
          </Button>
        </motion.div>
      </div>
    </header>
  );
}