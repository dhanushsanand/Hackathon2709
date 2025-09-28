import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Trophy, Clock, CheckCircle, RotateCcw, Target, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../components/ui/dialog';
import { Input } from '@/components/ui/input';

interface Question {
  id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer';
  options: string[] | null;
  correct_answer: string;
  explanation: string;
  difficulty: number;
  source_chunk: string;
}

interface Quiz {
  id: string;
  pdf_id: string;
  user_id: string;
  title: string;
  description: string;
  questions: Question[];
  total_questions: number;
  estimated_time: number;
  created_at: string;
  completedAt?: Date;
  score?: number;
  bestScore?: number;
}

interface QuizSubmission {
  quiz_id: string;
  answers: {
    [questionId: string]: string;
  };
}

interface QuizAttempt {
  answers: { [questionId: string]: string };
  timeRemaining: number;
  currentQuestion: number;
}

const QuizzesPage: React.FC = () => {
  // Add missing imports

  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);
  const [quizAttempt, setQuizAttempt] = useState<QuizAttempt | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [filter, setFilter] = useState<'all' | 'completed' | 'pending'>('all');
  const [deleteQuizId, setDeleteQuizId] = useState<string | null>(null);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [quizResults, setQuizResults] = useState<any>(null);

  const [loadingNotes, setLoadingNotes] = useState(false);

useEffect(() => {
  fetchQuizzes();
}, []);

const fetchQuizzes = async () => {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const response = await fetch('http://localhost:8000/quiz/user/all', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      cache: 'no-store'   // 🚀 bypass browser cache
    });

    if (!response.ok) throw new Error(`Failed to fetch quizzes: ${response.status}`);
    
    const data = await response.json();
    console.log('Fetched quiz data:', data);
    if (Array.isArray(data)) {
      setQuizzes(data);
    } else if (data.quizzes) {
      setQuizzes(data.quizzes);
    } else {
      console.error('Unexpected quiz data format:', data);
      setQuizzes([]);
    }
  } catch (error) {
    console.error('Error fetching quizzes:', error);
  }
};


  const submitQuiz = async (quizId: string, answers: { [key: string]: string }) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No token found');

      const response = await fetch(`http://localhost:8000/quiz/${quizId}/submit`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers })
      });

      if (!response.ok) throw new Error('Failed to submit quiz');

      const results = await response.json();
      setQuizResults(results);

      // Generate study notes
      if (results.quiz_attempt_id) {
        generateStudyNotes(results.quiz_attempt_id);
      }

      return results;
    } catch (error) {
      console.error('Error submitting quiz:', error);
      throw error;
    }
  };

const generateStudyNotes = async (
  quizAttemptId: string,
  retries = 3,
  delay = 1000
) => {
  try {
    setLoadingNotes(true); // show loader
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const response = await fetch(
      `http://localhost:8000/notes/generate/${quizAttemptId}`,
      {
        method: "POST", // backend expects POST
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      if (retries > 0) {
        console.warn(`Retrying notes generation... (${retries} left)`);
        setTimeout(
          () => generateStudyNotes(quizAttemptId, retries - 1, delay * 2),
          delay
        );
        return;
      }
      throw new Error(`Failed after retries: ${response.status}`);
    }

    const data = await response.json();
    console.log("Generated study notes:", data);
  } catch (error) {
    console.error("Error generating study notes:", error);
  } finally {
    setLoadingNotes(false); // hide loader
  }
};


  const startQuiz = (quiz: Quiz) => {
    setSelectedQuiz(quiz);
    setQuizAttempt({
      answers: {},
      timeRemaining: quiz.estimated_time * 60, // convert to seconds
      currentQuestion: 0
    });
    setShowResults(false);
  };

  const answerQuestion = (questionId: string, answer: string) => {
    if (!quizAttempt) return;
    
    setQuizAttempt({
      ...quizAttempt,
      answers: {
        ...quizAttempt.answers,
        [questionId]: answer
      }
    });
  };

  const nextQuestion = () => {
    if (!quizAttempt || !selectedQuiz) return;
    
    if (quizAttempt.currentQuestion < selectedQuiz.questions.length - 1) {
      setQuizAttempt({
        ...quizAttempt,
        currentQuestion: quizAttempt.currentQuestion + 1
      });
    } else {
      finishQuiz();
    }
  };

  const finishQuiz = async () => {
    if (!selectedQuiz || !quizAttempt) return;
    
    try {
      const results = await submitQuiz(selectedQuiz.id, quizAttempt.answers);
      
      // Update quiz in list with new score
      setQuizzes(prevQuizzes => 
        prevQuizzes.map(q => 
          q.id === selectedQuiz.id 
            ? { ...q, completedAt: new Date(), score: results.score }
            : q
        )
      );
      
      setShowResults(true);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300';
      case 'Medium': return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300';
      case 'Hard': return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300';
      default: return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-300';
    }
  };

  const deleteQuiz = (id: string) => {
    setQuizzes(quizzes.filter(quiz => quiz.id !== id));
    setDeleteQuizId(null);
  };

  const filteredQuizzes = quizzes.filter(quiz => {
    switch (filter) {
      case 'completed': return quiz.completedAt;
      case 'pending': return !quiz.completedAt;
      default: return true;
    }
  });

  const currentQuestion = selectedQuiz && quizAttempt 
    ? selectedQuiz.questions[quizAttempt.currentQuestion] 
    : null;

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

  if (selectedQuiz && quizAttempt && !showResults) {
    return (
      <motion.div
        className="max-w-4xl mx-auto space-y-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        {/* Quiz Header */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {selectedQuiz.title}
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Question {quizAttempt.currentQuestion + 1} of {selectedQuiz.questions.length}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Clock className="h-4 w-4" />
                <span className="font-mono">
                  {Math.floor(quizAttempt.timeRemaining / 60)}:
                  {(quizAttempt.timeRemaining % 60).toString().padStart(2, '0')}
                </span>
              </div>
              <Button
                variant="ghost"
                onClick={() => {
                  setSelectedQuiz(null);
                  setQuizAttempt(null);
                }}
              >
                Exit Quiz
              </Button>
            </div>
          </div>
          
          <div className="mt-4">
            <Progress 
              value={((quizAttempt.currentQuestion + 1) / selectedQuiz.questions.length) * 100} 
              className="h-2"
            />
          </div>
        </Card>

        {/* Question Card */}
        {currentQuestion && (
          <Card className="p-8">
            <motion.div
              key={currentQuestion.id}
              initial={{ x: 20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              className="space-y-6"
            >
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {currentQuestion.question_text}
              </h2>
              
              <div className="space-y-3">
                {currentQuestion.question_type === 'short_answer' ? (
                  <Input
                    type="text"
                    placeholder="Type your answer here..."
                    value={quizAttempt.answers[currentQuestion.id] || ''}
                    onChange={(e) => answerQuestion(currentQuestion.id, e.target.value)}
                    className="w-full"
                  />
                ) : currentQuestion.options?.map((option, index) => {
                  const isSelected = quizAttempt.answers[currentQuestion.id] === option;
                  return (
                    <motion.button
                      key={index}
                      onClick={() => answerQuestion(currentQuestion.id, option)}
                      className={`w-full p-4 text-left rounded-xl border-2 transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-6 h-6 ${currentQuestion.question_type === 'true_false' ? 'rounded-lg' : 'rounded-full'} border-2 flex items-center justify-center ${
                          isSelected 
                            ? 'border-blue-500 bg-blue-500' 
                            : 'border-gray-300 dark:border-gray-600'
                        }`}>
                          {isSelected && <div className="w-2 h-2 bg-white rounded-full" />}
                        </div>
                        <span className="text-gray-900 dark:text-gray-100">{option}</span>
                      </div>
                    </motion.button>
                  );
                })}
              </div>
              
              <div className="flex justify-end">
                <Button
                  onClick={nextQuestion}
                  disabled={quizAttempt.answers[currentQuestion.id] === undefined}
                  size="lg"
                >
                  {quizAttempt.currentQuestion === selectedQuiz.questions.length - 1 
                    ? 'Finish Quiz' 
                    : 'Next Question'
                  }
                </Button>
              </div>
            </motion.div>
          </Card>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
          Practice Quizzes
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Test your knowledge with interactive quizzes
        </p>
      </motion.div>

      {/* Stats Cards */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/20 dark:to-blue-900/20 border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500 rounded-xl">
                <Target className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                  {quizzes.length}
                </h3>
                <p className="text-blue-600 dark:text-blue-400 font-medium">Total Quizzes</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/20 dark:to-green-900/20 border-green-200 dark:border-green-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-500 rounded-xl">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-green-700 dark:text-green-300">
                  {quizzes.filter(q => q.completedAt).length}
                </h3>
                <p className="text-green-600 dark:text-green-400 font-medium">Completed</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-950/20 dark:to-yellow-900/20 border-yellow-200 dark:border-yellow-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-500 rounded-xl">
                <Trophy className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-yellow-700 dark:text-yellow-300">
                  {Math.round(
                    quizzes
                      .filter(q => q.bestScore)
                      .reduce((acc, q) => acc + (q.bestScore || 0), 0) /
                    quizzes.filter(q => q.bestScore).length || 0
                  )}%
                </h3>
                <p className="text-yellow-600 dark:text-yellow-400 font-medium">Avg Score</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/20 dark:to-purple-900/20 border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-500 rounded-xl">
                <Clock className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-purple-700 dark:text-purple-300">
                  {quizzes.reduce((acc, q) => acc + q.estimated_time, 0)}
                </h3>
                <p className="text-purple-600 dark:text-purple-400 font-medium">Total Minutes</p>
              </div>
            </div>
          </Card>
        </div>
      </motion.div>

      {/* Filter Tabs */}
      <motion.div variants={itemVariants}>
        <div className="flex gap-2 mb-6">
          {[
            { key: 'all', label: 'All Quizzes' },
            { key: 'completed', label: 'Completed' },
            { key: 'pending', label: 'Pending' }
          ].map((tab) => (
            <Button
              key={tab.key}
              variant={filter === tab.key ? 'default' : 'ghost'}
              onClick={() => setFilter(tab.key as any)}
            >
              {tab.label}
            </Button>
          ))}
        </div>
      </motion.div>

      {/* Quiz List */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredQuizzes.map((quiz, index) => (
            <motion.div
              key={quiz.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="p-6 hover:shadow-xl transition-shadow">
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {quiz.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 text-sm">
                        {quiz.description}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-lg font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300`}>
                      PDF Quiz
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{quiz.estimated_time} min</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Target className="h-4 w-4" />
                      <span>{quiz.total_questions} questions</span>
                    </div>
                  </div>
                  
                  {quiz.bestScore && (
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 dark:text-gray-400">Best Score:</span>
                      <span className={`font-semibold ${getScoreColor(quiz.bestScore)}`}>
                        {quiz.bestScore}%
                      </span>
                    </div>
                  )}
                  
                  <div className="flex gap-2 pt-2">
                    <Button
                      onClick={() => startQuiz(quiz)}
                      className="flex-1"
                      size="sm"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      {quiz.completedAt ? 'Retake' : 'Start Quiz'}
                    </Button>
                    {quiz.completedAt && (
                      <Button variant="ghost" size="sm">
                        <RotateCcw className="h-4 w-4" />
                      </Button>
                    )}
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="text-red-500 hover:text-red-700 hover:bg-red-100 dark:hover:bg-red-950/20"
                      onClick={() => setDeleteQuizId(quiz.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteQuizId} onOpenChange={() => setDeleteQuizId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Quiz</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this quiz? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex gap-2 justify-end">
            <Button variant="ghost" onClick={() => setDeleteQuizId(null)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => deleteQuizId && deleteQuiz(deleteQuizId)}
              className="bg-red-500 hover:bg-red-600 text-white"
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {filteredQuizzes.length === 0 && (
        <motion.div variants={itemVariants}>
          <Card className="p-12 text-center">
            <Trophy className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No quizzes found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              {filter === 'completed' 
                ? 'Complete some quizzes to see them here'
                : filter === 'pending'
                ? 'All quizzes have been completed'
                : 'No quizzes available'
              }
            </p>
          </Card>
        </motion.div>
      )}
      {loadingNotes && (
  <div className="flex items-center justify-center p-6">
    <svg
      className="animate-spin h-6 w-6 text-blue-500 mr-2"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      ></circle>
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      ></path>
    </svg>
    <span className="text-gray-700 dark:text-gray-300">
      Generating study notes...
    </span>
  </div>
)}
    </motion.div>
  );
};

export default QuizzesPage;