import { useState } from "react";
import { Button } from "../ui/button";
import { Menu, Sun, Moon, Bell, User } from "lucide-react";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "../ui/dropdown-menu";
import { useAuth } from "../../contexts/AuthContext";
import { useTheme } from "../../contexts/ThemeContext";
import { motion } from "framer-motion";

interface NavbarProps {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}

export default function Navbar({ toggleSidebar }: NavbarProps) {
  const { logout, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
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
        <motion.div whileHover={{ scale: 1.1, rotate: 5 }} whileTap={{ scale: 0.9 }}>
          <Button variant="ghost" size="icon" onClick={toggleTheme} className="rounded-xl hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-gray-800 dark:hover:to-gray-700">
            {theme === 'dark' ? <Sun size={18} className="text-yellow-500" /> : <Moon size={18} className="text-blue-600" />}
          </Button>
        </motion.div>
        
        <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
          <Button variant="ghost" size="icon" className="relative rounded-xl hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-gray-800 dark:hover:to-gray-700">
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
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <motion.div whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}>
              <Button variant="ghost" size="icon" className="rounded-full p-0 w-10 h-10 border-2 border-gradient-to-r from-blue-500 to-purple-500 hover:shadow-lg transition-all duration-300">
                {user?.avatar ? (
                  <motion.img 
                    src={user.avatar} 
                    alt={user.name} 
                    className="w-8 h-8 rounded-full object-cover"
                    whileHover={{ rotate: 5 }}
                  />
                ) : (
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                    <User size={16} className="text-white" />
                  </div>
                )}
              </Button>
            </motion.div>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">{user?.name || 'User'}</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {user?.email}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => window.location.href = "/profile"}>
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => window.location.href = "/settings"}>
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout}>
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}