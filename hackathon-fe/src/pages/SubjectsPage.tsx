import { useState } from "react";
import { motion } from "framer-motion";
import { Plus, BookOpen, Edit, Trash2, BarChart3 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { Input } from "../components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";

interface Subject {
  id: string;
  name: string;
  description: string;
  progress: number;
  uploads: number;
  notes: number;
  quizzes: number;
  bestScore: number;
  latestScore: number;
  averageScore: number;
  color: string;
}

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<Subject[]>([
    {
      id: "1",
      name: "Mathematics",
      description: "Advanced calculus and linear algebra",
      progress: 75,
      uploads: 8,
      notes: 6,
      quizzes: 4,
      bestScore: 95,
      latestScore: 87,
      averageScore: 89,
      color: "bg-blue-500"
    },
    {
      id: "2", 
      name: "Physics",
      description: "Quantum mechanics and thermodynamics",
      progress: 60,
      uploads: 5,
      notes: 4,
      quizzes: 3,
      bestScore: 88,
      latestScore: 76,
      averageScore: 82,
      color: "bg-green-500"
    },
    {
      id: "3",
      name: "Computer Science", 
      description: "Data structures and algorithms",
      progress: 90,
      uploads: 11,
      notes: 8,
      quizzes: 6,
      bestScore: 98,
      latestScore: 94,
      averageScore: 96,
      color: "bg-purple-500"
    }
  ]);

  const [newSubject, setNewSubject] = useState({ name: "", description: "" });
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleAddSubject = () => {
    if (newSubject.name.trim()) {
      const colors = ["bg-red-500", "bg-yellow-500", "bg-indigo-500", "bg-pink-500", "bg-teal-500"];
      const randomColor = colors[Math.floor(Math.random() * colors.length)];
      
      setSubjects([...subjects, {
        id: Date.now().toString(),
        name: newSubject.name,
        description: newSubject.description,
        progress: 0,
        uploads: 0,
        notes: 0,
        quizzes: 0,
        bestScore: 0,
        latestScore: 0,
        averageScore: 0,
        color: randomColor
      }]);
      setNewSubject({ name: "", description: "" });
      setIsDialogOpen(false);
    }
  };

  const handleDeleteSubject = (id: string) => {
    setSubjects(subjects.filter(subject => subject.id !== id));
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              My Subjects
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Manage your learning areas and track progress
            </p>
          </div>
          
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Plus size={20} />
                Add Subject
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Subject</DialogTitle>
                <DialogDescription>
                  Create a new subject to organize your learning materials
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Subject Name</label>
                  <Input
                    placeholder="e.g., Mathematics"
                    value={newSubject.name}
                    onChange={(e) => setNewSubject({...newSubject, name: e.target.value})}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                  <Input
                    placeholder="Brief description of the subject"
                    value={newSubject.description}
                    onChange={(e) => setNewSubject({...newSubject, description: e.target.value})}
                  />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddSubject}>
                    Create Subject
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </motion.div>

      {/* Subjects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subjects.map((subject, index) => (
          <motion.div
            key={subject.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <Card className="group">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full ${subject.color}`}></div>
                    <div>
                      <CardTitle className="text-xl">{subject.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {subject.description}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <Edit size={14} />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8 text-red-600 hover:text-red-700"
                      onClick={() => handleDeleteSubject(subject.id)}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Progress Bar */}
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600 dark:text-gray-400">Progress</span>
                    <span className="font-semibold">{subject.progress}%</span>
                  </div>
                  <Progress value={subject.progress} />
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-blue-600">{subject.uploads}</p>
                    <p className="text-xs text-gray-500">Uploads</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-600">{subject.notes}</p>
                    <p className="text-xs text-gray-500">Notes</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-purple-600">{subject.quizzes}</p>
                    <p className="text-xs text-gray-500">Quizzes</p>
                  </div>
                </div>

                {/* Quiz Scores */}
                {subject.quizzes > 0 && (
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <BarChart3 size={16} className="text-gray-600" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Quiz Performance</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div>
                        <p className="text-gray-500">Best</p>
                        <p className="font-semibold text-green-600">{subject.bestScore}%</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Latest</p>
                        <p className="font-semibold text-blue-600">{subject.latestScore}%</p>
                      </div>
                      <div>
                        <p className="text-gray-500">Average</p>
                        <p className="font-semibold text-purple-600">{subject.averageScore}%</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button size="sm" className="flex-1">
                    <BookOpen size={14} className="mr-1" />
                    View
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    Study
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Empty State */}
      {subjects.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <BookOpen size={64} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">
            No subjects yet
          </h3>
          <p className="text-gray-500 mb-4">
            Create your first subject to start organizing your learning materials
          </p>
          <Button onClick={() => setIsDialogOpen(true)}>
            <Plus size={20} className="mr-2" />
            Add Your First Subject
          </Button>
        </motion.div>
      )}
    </div>
  );
}