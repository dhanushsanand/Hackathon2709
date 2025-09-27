import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Search, BookOpen, Star, Calendar, Edit, Trash2, ChevronDown, ChevronRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';

interface Note {
  id: string;
  title: string;
  content: string;
  subject: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
  favorite: boolean;
}

interface NoteCategory {
  id: string;
  name: string;
  notes: Note[];
  expanded: boolean;
}

const NotesPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  
  const [categories, setCategories] = useState<NoteCategory[]>([
    {
      id: '1',
      name: 'Mathematics',
      expanded: true,
      notes: [
        {
          id: '1',
          title: 'Calculus Derivatives',
          content: 'Basic rules of differentiation:\n\n1. Power Rule: d/dx[x^n] = nx^(n-1)\n2. Product Rule: d/dx[uv] = u\'v + uv\'\n3. Chain Rule: d/dx[f(g(x))] = f\'(g(x)) · g\'(x)',
          subject: 'Mathematics',
          tags: ['calculus', 'derivatives', 'formulas'],
          createdAt: new Date('2024-01-15'),
          updatedAt: new Date('2024-01-15'),
          favorite: true
        },
        {
          id: '2',
          title: 'Linear Algebra Basics',
          content: 'Matrix operations and properties:\n\n- Matrix multiplication is associative but not commutative\n- Identity matrix: AI = IA = A\n- Inverse matrix: AA^(-1) = A^(-1)A = I',
          subject: 'Mathematics',
          tags: ['linear algebra', 'matrices', 'operations'],
          createdAt: new Date('2024-01-14'),
          updatedAt: new Date('2024-01-14'),
          favorite: false
        }
      ]
    },
    {
      id: '2',
      name: 'Physics',
      expanded: false,
      notes: [
        {
          id: '3',
          title: 'Newton\'s Laws',
          content: '1. First Law (Inertia): An object at rest stays at rest, an object in motion stays in motion\n2. Second Law: F = ma\n3. Third Law: For every action, there is an equal and opposite reaction',
          subject: 'Physics',
          tags: ['mechanics', 'forces', 'laws'],
          createdAt: new Date('2024-01-13'),
          updatedAt: new Date('2024-01-13'),
          favorite: true
        }
      ]
    },
    {
      id: '3',
      name: 'Chemistry',
      expanded: false,
      notes: [
        {
          id: '4',
          title: 'Periodic Table Trends',
          content: 'Key trends in the periodic table:\n\n- Atomic radius decreases across a period\n- Ionization energy increases across a period\n- Electronegativity increases across a period',
          subject: 'Chemistry',
          tags: ['periodic table', 'trends', 'properties'],
          createdAt: new Date('2024-01-12'),
          updatedAt: new Date('2024-01-12'),
          favorite: false
        }
      ]
    }
  ]);

  const toggleCategory = (categoryId: string) => {
    setCategories(prev => prev.map(cat => 
      cat.id === categoryId ? { ...cat, expanded: !cat.expanded } : cat
    ));
  };

  const toggleFavorite = (noteId: string) => {
    setCategories(prev => prev.map(cat => ({
      ...cat,
      notes: cat.notes.map(note => 
        note.id === noteId ? { ...note, favorite: !note.favorite } : note
      )
    })));
  };

  const getAllNotes = (): Note[] => {
    return categories.flatMap(cat => cat.notes);
  };

  const filteredCategories = categories.map(cat => ({
    ...cat,
    notes: cat.notes.filter(note => 
      note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    )
  })).filter(cat => cat.notes.length > 0 || searchTerm === '');

  const favoriteNotes = getAllNotes().filter(note => note.favorite);
  const recentNotes = getAllNotes().sort((a, b) => 
    new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  ).slice(0, 5);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 300,
        damping: 24
      }
    }
  };

  return (
    <motion.div
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          Study Notes
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Organize and manage your study materials
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <div className="space-y-6">
            {/* Search */}
            <Card className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  type="text"
                  placeholder="Search notes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </Card>

            {/* Quick Stats */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Quick Stats
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-blue-500" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Total Notes</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {getAllNotes().length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Star className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Favorites</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {favoriteNotes.length}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-gray-600 dark:text-gray-400">Subjects</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {categories.length}
                  </span>
                </div>
              </div>
            </Card>

            {/* Recent Notes */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Recent Notes
              </h3>
              <div className="space-y-3">
                {recentNotes.map((note) => (
                  <div
                    key={note.id}
                    className="p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                    onClick={() => setSelectedNote(note)}
                  >
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 text-sm truncate">
                      {note.title}
                    </h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {note.subject} • {note.updatedAt.toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Add Note Button */}
            <Button className="w-full" size="lg">
              <Plus className="h-4 w-4 mr-2" />
              Add New Note
            </Button>
          </div>
        </motion.div>

        {/* Main Content */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          {selectedNote ? (
            <Card className="p-8">
              <div className="flex items-start justify-between mb-6">
                <div className="flex-grow">
                  <div className="flex items-center gap-2 mb-2">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                      {selectedNote.title}
                    </h2>
                    <button
                      onClick={() => toggleFavorite(selectedNote.id)}
                      className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                    >
                      <Star 
                        className={`h-5 w-5 ${
                          selectedNote.favorite 
                            ? 'text-yellow-500 fill-yellow-500' 
                            : 'text-gray-400'
                        }`} 
                      />
                    </button>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>{selectedNote.subject}</span>
                    <span>•</span>
                    <span>Updated {selectedNote.updatedAt.toLocaleDateString()}</span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {selectedNote.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-lg"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-500 hover:text-red-700">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              <div className="prose prose-gray dark:prose-invert max-w-none">
                <pre className="whitespace-pre-wrap text-gray-700 dark:text-gray-300 leading-relaxed">
                  {selectedNote.content}
                </pre>
              </div>
            </Card>
          ) : (
            <div className="space-y-6">
              {filteredCategories.map((category) => (
                <Card key={category.id} className="overflow-hidden">
                  <div
                    className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 cursor-pointer hover:from-gray-100 hover:to-gray-200 dark:hover:from-gray-700 dark:hover:to-gray-600 transition-colors"
                    onClick={() => toggleCategory(category.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {category.expanded ? (
                          <ChevronDown className="h-5 w-5 text-gray-500" />
                        ) : (
                          <ChevronRight className="h-5 w-5 text-gray-500" />
                        )}
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                          {category.name}
                        </h3>
                        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                          {category.notes.length}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {category.expanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="border-t border-gray-200 dark:border-gray-700"
                    >
                      <div className="p-4 space-y-3">
                        {category.notes.map((note) => (
                          <motion.div
                            key={note.id}
                            className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                            onClick={() => setSelectedNote(note)}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-grow">
                                <div className="flex items-center gap-2 mb-2">
                                  <h4 className="font-medium text-gray-900 dark:text-gray-100">
                                    {note.title}
                                  </h4>
                                  {note.favorite && (
                                    <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                                  )}
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
                                  {note.content.substring(0, 120)}...
                                </p>
                                <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                  <span>{note.updatedAt.toLocaleDateString()}</span>
                                  <span>•</span>
                                  <span>{note.tags.length} tags</span>
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </Card>
              ))}
              
              {filteredCategories.length === 0 && searchTerm && (
                <Card className="p-12 text-center">
                  <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                    No notes found
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Try adjusting your search terms
                  </p>
                </Card>
              )}
            </div>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default NotesPage;