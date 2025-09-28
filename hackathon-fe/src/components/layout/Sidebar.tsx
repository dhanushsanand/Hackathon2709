import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { cn } from "../../lib/utils";
import { 
  BookOpen, 
  Home, 
  FolderUp, 
  FileText, 
  BrainCircuit, 
  Settings, 
  ChevronLeft, 
  ChevronRight, 
  Shield 
} from "lucide-react";
import { LogOut } from "lucide-react";
import { Button } from "../ui/button";
import { useAuth } from "../../contexts/AuthContext";

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

export default function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
  const location = useLocation();
  const { user, logout } = useAuth();

  const navItems = [
    { icon: Home, label: "Dashboard", path: "/" },
    { icon: BookOpen, label: "Subjects", path: "/subjects" },
    { icon: FolderUp, label: "Uploads", path: "/uploads" },
    { icon: FileText, label: "Notes", path: "/notes" },
    { icon: BrainCircuit, label: "Quizzes", path: "/quizzes" },
    { icon: Shield, label: "Campus Safety", path: "/campus-safety" },
    { icon: Settings, label: "Settings", path: "/settings" },
  ];

  return (
    <motion.aside 
      animate={{ width: collapsed ? 70 : 240 }}
      transition={{ duration: 0.4, ease: "easeInOut" }}
      className="bg-gradient-to-b from-white to-gray-50 dark:from-gray-900 dark:to-gray-950 border-r border-gray-200 dark:border-gray-800 h-screen sticky top-0 flex flex-col shadow-xl min-h-0 z-40"
    >
        <div className="p-4 flex items-center justify-between border-b border-gray-200 dark:border-gray-800 min-h-[73px] bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-900 sticky top-0 z-30">
        <motion.h1 
          animate={{ opacity: collapsed ? 0 : 1 }}
          transition={{ duration: 0.3, delay: collapsed ? 0 : 0.2 }}
          className="font-extrabold text-xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
        >
          {!collapsed && "LearnHub"}
        </motion.h1>
        <motion.button 
          onClick={() => setCollapsed(!collapsed)} 
          className="p-2 rounded-xl hover:bg-white dark:hover:bg-gray-800 transition-all duration-200 shadow-sm hover:shadow-md"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </motion.button>
      </div>

      <nav className="p-3 flex-1 overflow-y-auto min-h-0">
        <ul className="space-y-2">
          {navItems.map((item, index) => (
            <motion.li 
              key={item.path}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05, x: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link
                to={item.path}
                className={cn(
                  "flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden",
                  location.pathname === item.path 
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/25" 
                    : "hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-gray-800 dark:hover:to-gray-700 hover:shadow-md"
                )}
              >
                {/* Active indicator */}
                {location.pathname === item.path && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
                
                <motion.div
                  whileHover={{ rotate: location.pathname === item.path ? 0 : 5 }}
                  className="relative z-10"
                >
                  <item.icon size={20} className="min-w-[20px]" />
                </motion.div>
                
                <motion.span 
                  animate={{ opacity: collapsed ? 0 : 1 }}
                  transition={{ duration: 0.3, delay: collapsed ? 0 : 0.1 }}
                  className="whitespace-nowrap font-medium relative z-10 group-hover:translate-x-1 transition-transform duration-200"
                >
                  {!collapsed && item.label}
                </motion.span>
                
                {/* Hover effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  initial={false}
                />
              </Link>
            </motion.li>
          ))}
        </ul>
      </nav>

      {/* Footer: user / login / logout */}
      <div className="p-3 border-t border-gray-200 dark:border-gray-800">
        {user ? (
          <div className="flex items-center gap-3">
            <img src={user.avatar} alt={user.name} className="w-8 h-8 rounded-full" />
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{user.name}</div>
                <div className="text-xs text-gray-500 truncate">{user.email}</div>
              </div>
            )}
            <Button variant="ghost" size="icon" onClick={() => logout()} className="h-8 w-8">
              <LogOut size={16} />
            </Button>
          </div>
        ) : (
          <div className="flex items-center justify-center">
            <Link to="/login">
              <Button>Login</Button>
            </Link>
          </div>
        )}
      </div>
    </motion.aside>
  );
}