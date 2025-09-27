import { motion } from "framer-motion";
import { 
  ArrowUpRight, 
  BookOpen, 
  FileText, 
  BrainCircuit, 
  BarChart2,
  Upload,
  Clock,
  TrendingUp
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Progress } from "../components/ui/progress";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Link } from "react-router-dom";

interface StatCardProps {
  title: string;
  value: string | number;
  description: string;
  icon: React.ElementType;
  color: string;
  trend?: string;
}

const StatCard = ({ title, value, description, icon: Icon, color, trend }: StatCardProps) => (
  <motion.div
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
    transition={{ type: "spring", stiffness: 400, damping: 17 }}
  >
    <Card className="relative overflow-hidden group">
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div className="space-y-3 flex-1">
            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">{title}</p>
            <div className="flex items-baseline space-x-3">
              <p className="text-4xl font-black text-gray-900 dark:text-white">{value}</p>
              {trend && (
                <motion.span 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="text-sm text-green-600 dark:text-green-400 flex items-center bg-green-100 dark:bg-green-900 px-2 py-1 rounded-full"
                >
                  <TrendingUp className="w-3 h-3 mr-1" />
                  {trend}
                </motion.span>
              )}
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">{description}</p>
          </div>
          <motion.div 
            className={`p-4 rounded-2xl ${color} shadow-lg`}
            whileHover={{ rotate: 5 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
          >
            <Icon size={28} />
          </motion.div>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

export default function DashboardPage() {
  // Mock data
  const stats = [
    { 
      title: "Total Uploads", 
      value: 24, 
      description: "Files uploaded this month", 
      icon: Upload,
      color: "bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400",
      trend: "+4"
    },
    { 
      title: "Notes Generated", 
      value: 18, 
      description: "AI-generated summaries", 
      icon: FileText,
      color: "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400",
      trend: "+3"
    },
    { 
      title: "Quizzes Completed", 
      value: 12, 
      description: "Practice sessions done", 
      icon: BrainCircuit,
      color: "bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-400",
      trend: "+2"
    },
    { 
      title: "Overall Progress", 
      value: "68%", 
      description: "Across all subjects", 
      icon: BarChart2,
      color: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400",
      trend: "+12%"
    }
  ];
  
  // Recent subjects
  const recentSubjects = [
    { id: "1", name: "Mathematics", progress: 75, uploads: 8, notes: 6 },
    { id: "2", name: "Physics", progress: 60, uploads: 5, notes: 4 },
    { id: "3", name: "Computer Science", progress: 90, uploads: 11, notes: 8 }
  ];

  // Recent activities
  const recentActivities = [
    { 
      id: "1", 
      type: "upload", 
      subject: "Mathematics", 
      description: "Uploaded calculus_notes.pdf",
      date: "2 hours ago",
      icon: Upload,
      color: "text-blue-500"
    },
    { 
      id: "2", 
      type: "note", 
      subject: "Physics", 
      description: "Generated notes for quantum mechanics",
      date: "Yesterday",
      icon: FileText,
      color: "text-green-500"
    },
    { 
      id: "3", 
      type: "quiz", 
      subject: "Computer Science", 
      description: "Completed Data Structures quiz (85%)",
      date: "2 days ago",
      icon: BrainCircuit,
      color: "text-purple-500"
    }
  ];
  
  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative"
      >
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl border border-gray-200 dark:border-gray-700">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-2">
            Learning Dashboard
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Welcome back! Here's an overview of your learning journey ✨
          </p>
        </div>
      </motion.div>
      
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * index }}
          >
            <StatCard {...stat} />
          </motion.div>
        ))}
      </motion.div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Subjects */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl">Recent Subjects</CardTitle>
                  <CardDescription>Your most active learning areas</CardDescription>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link to="/subjects" className="flex items-center gap-1">
                    View All <ArrowUpRight size={14} />
                  </Link>
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {recentSubjects.map((subject, index) => (
                <motion.div 
                  key={subject.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 * index }}
                  className="space-y-3"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-medium">{subject.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {subject.uploads} uploads • {subject.notes} notes
                      </p>
                    </div>
                    <span className="text-sm font-medium">{subject.progress}%</span>
                  </div>
                  <Progress value={subject.progress} className="h-2" />
                </motion.div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
        
        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-xl flex items-center gap-2">
                <Clock size={20} />
                Recent Activity
              </CardTitle>
              <CardDescription>Your latest learning activities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentActivities.map((activity, index) => (
                <motion.div 
                  key={activity.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 * index }}
                  className="flex items-start p-3 rounded-lg hover:bg-accent/50 transition-colors group"
                >
                  <div className={`p-2 rounded-md mr-4 ${activity.color.replace('text-', 'bg-').replace('500', '100')} dark:${activity.color.replace('text-', 'bg-').replace('500', '950')}`}>
                    <activity.icon size={16} className={activity.color} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{activity.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {activity.subject} • {activity.date}
                    </p>
                  </div>
                </motion.div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Jump into your learning activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button asChild className="h-16 flex-col gap-2">
                <Link to="/uploads">
                  <Upload size={20} />
                  Upload Materials
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-16 flex-col gap-2">
                <Link to="/subjects">
                  <BookOpen size={20} />
                  Manage Subjects
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-16 flex-col gap-2">
                <Link to="/quizzes">
                  <BrainCircuit size={20} />
                  Take Quiz
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}