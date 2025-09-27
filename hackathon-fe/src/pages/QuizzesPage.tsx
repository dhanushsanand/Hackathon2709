import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Trophy, Clock, CheckCircle, RotateCcw, Target } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Progress } from '../components/ui/progress';

interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

interface Quiz {
  id: string;
  title: string;
  subject: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  duration: number; // in minutes
  questions: Question[];
  completedAt?: Date;
  score?: number;
  bestScore?: number;
}

interface QuizAttempt {
  answers: { [questionId: string]: number };
  timeRemaining: number;
  currentQuestion: number;
}

const QuizzesPage: React.FC = () => {
  const [selectedQuiz, setSelectedQuiz] = useState<Quiz | null>(null);
  const [quizAttempt, setQuizAttempt] = useState<QuizAttempt | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [filter, setFilter] = useState<'all' | 'completed' | 'pending'>('all');

  const [quizzes] = useState<Quiz[]>([
    {
      id: '1',
      title: 'Calculus Fundamentals',
      subject: 'Mathematics',
      difficulty: 'Medium',
      duration: 30,
      questions: [
        {
          id: '1',
          question: 'What is the derivative of x²?',
          options: ['x', '2x', 'x²', '2x²'],
          correctAnswer: 1,
          explanation: 'Using the power rule: d/dx[x²] = 2x¹ = 2x'
        },
        {
          id: '2',
          question: 'What is the integral of 2x?',
          options: ['x²', 'x² + C', '2x²', '2x² + C'],
          correctAnswer: 1,
          explanation: 'The integral of 2x is x² + C, where C is the constant of integration'
        },
        {
          id: '3',
          question: 'What is the limit of (x² - 1)/(x - 1) as x approaches 1?',
          options: ['0', '1', '2', 'undefined'],
          correctAnswer: 2,
          explanation: 'Factor the numerator: (x-1)(x+1)/(x-1) = x+1, so the limit is 1+1 = 2'
        }
      ],
      completedAt: new Date('2024-01-15'),
      score: 85,
      bestScore: 90
    },
    {
      id: '2',
      title: 'Newton\'s Laws Quiz',
      subject: 'Physics',
      difficulty: 'Easy',
      duration: 20,
      questions: [
        {
          id: '4',
          question: 'What is Newton\'s Second Law?',
          options: ['F = ma', 'E = mc²', 'v = at', 'P = mv'],
          correctAnswer: 0,
          explanation: 'Newton\'s Second Law states that Force equals mass times acceleration (F = ma)'
        },
        {
          id: '5',
          question: 'An object at rest will stay at rest unless acted upon by a force. This is:',
          options: ['Newton\'s Second Law', 'Newton\'s First Law', 'Newton\'s Third Law', 'Law of Gravity'],
          correctAnswer: 1,
          explanation: 'This describes Newton\'s First Law, also known as the Law of Inertia'
        }
      ],
      bestScore: 95
    },
    {
      id: '3',
      title: 'Organic Chemistry Basics',
      subject: 'Chemistry',
      difficulty: 'Hard',
      duration: 45,
      questions: [
        {
          id: '6',
          question: 'What is the IUPAC name for CH₃CH₂CH₂OH?',
          options: ['Ethanol', 'Propanol', '1-Propanol', 'Methanol'],
          correctAnswer: 2,
          explanation: '1-Propanol is the correct IUPAC name for this three-carbon alcohol'
        }
      ],
      completedAt: new Date('2024-01-10'),
      score: 72,
      bestScore: 78
    }
  ]);

  const startQuiz = (quiz: Quiz) => {
    setSelectedQuiz(quiz);
    setQuizAttempt({
      answers: {},
      timeRemaining: quiz.duration * 60, // convert to seconds
      currentQuestion: 0
    });
    setShowResults(false);
  };

  const answerQuestion = (questionId: string, answerIndex: number) => {
    if (!quizAttempt) return;
    
    setQuizAttempt({
      ...quizAttempt,
      answers: {
        ...quizAttempt.answers,
        [questionId]: answerIndex
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

  const finishQuiz = () => {
    if (!selectedQuiz || !quizAttempt) return;
    
    const correctAnswers = selectedQuiz.questions.filter(q => 
      quizAttempt.answers[q.id] === q.correctAnswer
    ).length;
    
    // Calculate score for results display
    Math.round((correctAnswers / selectedQuiz.questions.length) * 100);
    
    setShowResults(true);
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
                {currentQuestion.question}
              </h2>
              
              <div className="space-y-3">
                {currentQuestion.options.map((option, index) => {
                  const isSelected = quizAttempt.answers[currentQuestion.id] === index;
                  return (
                    <motion.button
                      key={index}
                      onClick={() => answerQuestion(currentQuestion.id, index)}
                      className={`w-full p-4 text-left rounded-xl border-2 transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
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
                  {quizzes.reduce((acc, q) => acc + q.duration, 0)}
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
                        {quiz.subject}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-lg font-medium ${getDifficultyColor(quiz.difficulty)}`}>
                      {quiz.difficulty}
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{quiz.duration} min</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Target className="h-4 w-4" />
                      <span>{quiz.questions.length} questions</span>
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
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </motion.div>

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
    </motion.div>
  );
};

export default QuizzesPage;