import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, BookOpen, Edit, Trash2, BarChart3 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Input } from '../components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { getSubjects, getUploadsBySubject, addSubject, deleteSubjectById } from '../lib/storage';
import type { StoredSubject } from '../lib/storage';

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState<StoredSubject[]>(() => getSubjects());
  const [newSubject, setNewSubject] = useState({ name: '', description: '' });
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [viewing, setViewing] = useState<null | { subject: StoredSubject; uploads: ReturnType<typeof getUploadsBySubject> }>(null);

  useEffect(() => {
    const onUpdate = () => setSubjects(getSubjects());
    window.addEventListener('app:storage-updated', onUpdate);
    return () => window.removeEventListener('app:storage-updated', onUpdate);
  }, []);

  const handleAddSubject = () => {
    if (!newSubject.name.trim()) return;
    const colors = ["bg-red-500", "bg-yellow-500", "bg-indigo-500", "bg-pink-500", "bg-teal-500", "bg-blue-500", "bg-green-500", "bg-purple-500"];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    const s: StoredSubject = {
      id: Date.now().toString() + Math.random().toString(36).slice(2),
      name: newSubject.name.trim(),
      description: newSubject.description.trim(),
      progress: 0,
      uploads: 0,
      notes: 0,
      quizzes: 0,
      bestScore: 0,
      latestScore: 0,
      averageScore: 0,
      color: randomColor,
    };
    addSubject(s);
    setNewSubject({ name: '', description: '' });
    setIsDialogOpen(false);
    setSubjects(getSubjects());
  };

  const handleDeleteSubject = (id: string) => {
    // simple delete - does not remove uploads for now
    deleteSubjectById(id);
    setSubjects(getSubjects());
  };

  const openView = (subject: StoredSubject) => {
    const uploads = getUploadsBySubject(subject.name);
    setViewing({ subject, uploads });
  };

  const closeView = () => setViewing(null);

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">My Subjects</h1>
            <p className="text-lg text-gray-600 dark:text-gray-400">Manage your learning areas and track progress</p>
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
                <DialogDescription>Create a new subject to organize your learning materials</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Subject Name</label>
                  <Input placeholder="e.g., Mathematics" value={newSubject.name} onChange={(e) => setNewSubject({ ...newSubject, name: e.target.value })} />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                  <Input placeholder="Brief description of the subject" value={newSubject.description} onChange={(e) => setNewSubject({ ...newSubject, description: e.target.value })} />
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                  <Button onClick={handleAddSubject}>Create Subject</Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {subjects.map((subject, index) => (
          <motion.div key={subject.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: index * 0.05 }} whileHover={{ scale: 1.02 }}>
            <Card className="group">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full ${subject.color}`}></div>
                    <div>
                      <CardTitle className="text-xl">{subject.name}</CardTitle>
                      <CardDescription className="mt-1">{subject.description}</CardDescription>
                    </div>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button variant="ghost" size="icon" className="h-8 w-8"><Edit size={14} /></Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-red-600 hover:text-red-700" onClick={() => handleDeleteSubject(subject.id)}>
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-600 dark:text-gray-400">Progress</span>
                    <span className="font-semibold">{subject.progress ?? 0}%</span>
                  </div>
                  <Progress value={subject.progress ?? 0} />
                </div>

                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-blue-600">{subject.uploads ?? 0}</p>
                    <p className="text-xs text-gray-500">Uploads</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-600">{subject.notes ?? 0}</p>
                    <p className="text-xs text-gray-500">Notes</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-purple-600">{subject.quizzes ?? 0}</p>
                    <p className="text-xs text-gray-500">Quizzes</p>
                  </div>
                </div>

                {subject.quizzes && subject.quizzes > 0 && (
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

                <div className="flex gap-2 pt-2">
                  <Button size="sm" className="flex-1" onClick={() => openView(subject)}>
                    <BookOpen size={14} className="mr-1" />
                    View
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">Study</Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {subjects.length === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12">
          <BookOpen size={64} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-2">No subjects yet</h3>
          <p className="text-gray-500 mb-4">Create your first subject to start organizing your learning materials</p>
          <Button onClick={() => setIsDialogOpen(true)}><Plus size={20} className="mr-2" />Add Your First Subject</Button>
        </motion.div>
      )}

      {/* View dialog - simple modal showing uploads for the subject */}
      <Dialog open={!!viewing} onOpenChange={() => closeView()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{viewing ? `Uploads for ${viewing.subject.name}` : 'Uploads'}</DialogTitle>
            <DialogDescription>{viewing ? `${viewing.uploads.length} file(s)` : ''}</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2 max-h-80 overflow-auto">
            {viewing && viewing.uploads.length === 0 && <p className="text-sm text-gray-500">No uploads for this subject yet.</p>}
            {viewing && viewing.uploads.map(u => (
              <div key={u.id} className="flex items-center justify-between p-2 border-b last:border-b-0">
                <div>
                  <div className="font-medium">{u.name}</div>
                  <div className="text-xs text-gray-500">{new Date(u.uploadedAt).toLocaleString()}</div>
                </div>
                <div className="text-sm text-gray-600">{(u.size / 1024 | 0)} KB</div>
              </div>
            ))}
          </div>
          <div className="flex justify-end mt-4">
            <Button onClick={() => closeView()}>Close</Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}