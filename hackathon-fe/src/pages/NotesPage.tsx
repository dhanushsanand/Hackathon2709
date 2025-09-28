import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { Card } from '../components/ui/card';

interface Note {
  id: string;
  title: string;
  content: string;
  subject: string;
  createdAt: Date;
  updatedAt: Date;
}

interface SubjectGroup {
  id: string;
  name: string;
  expanded: boolean;
  notes: Note[];
}

const NotesPage: React.FC = () => {
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [groups, setGroups] = useState<SubjectGroup[]>([
    {
      id: '1',
      name: 'Mathematics',
      expanded: true,
      notes: [
        {
          id: '1',
          title: 'Calculus Derivatives',
          content: 'Basic rules of differentiation:\n\n1. Power Rule\n2. Product Rule\n3. Chain Rule',
          subject: 'Mathematics',
          createdAt: new Date('2024-01-15'),
          updatedAt: new Date('2024-01-15')
        },
        {
          id: '2',
          title: 'Linear Algebra Basics',
          content: 'Matrix operations and properties.',
          subject: 'Mathematics',
          createdAt: new Date('2024-01-14'),
          updatedAt: new Date('2024-01-14')
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
          title: "Newton's Laws",
          content: 'First, Second and Third laws of motion.',
          subject: 'Physics',
          createdAt: new Date('2024-01-13'),
          updatedAt: new Date('2024-01-13')
        }
      ]
    }
  ]);

  const toggleGroup = (id: string) => {
    setGroups(prev => prev.map(g => g.id === id ? { ...g, expanded: !g.expanded } : g));
  };

  return (
    <motion.div className="space-y-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div>
        <h1 className="text-3xl font-bold">Study Notes</h1>
        <p className="text-sm text-gray-600 mt-1">Browse subjects and their notes</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="space-y-4">
            {groups.map(group => (
              <Card key={group.id} className="overflow-hidden">
                <div className="p-4 cursor-pointer" onClick={() => toggleGroup(group.id)}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {group.expanded ? <ChevronDown /> : <ChevronRight />}
                      <div className="font-semibold">{group.name}</div>
                    </div>
                    <div className="text-sm text-gray-500">{group.notes.length}</div>
                  </div>
                </div>
                {group.expanded && (
                  <div className="border-t">
                    {group.notes.map(note => (
                      <div key={note.id} className="p-3 hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedNote(note)}>
                        <div className="font-medium">{note.title}</div>
                        <div className="text-xs text-gray-500">{note.updatedAt.toLocaleDateString()}</div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2">
          {selectedNote ? (
            <Card className="p-6">
              <h2 className="text-2xl font-bold mb-2">{selectedNote.title}</h2>
              <div className="text-sm text-gray-500 mb-4">{selectedNote.subject} • {selectedNote.updatedAt.toLocaleDateString()}</div>
              <pre className="whitespace-pre-wrap">{selectedNote.content}</pre>
            </Card>
          ) : (
            <Card className="p-6">
              <div className="text-gray-600">Select a note to view its contents</div>
            </Card>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default NotesPage;