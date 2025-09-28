import React, { useState, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, Image, Video, Music, X, Download, Eye } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Input } from '../components/ui/input';

interface FileUpload {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
  progress: number;
  url?: string;
  subject: string;
}

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<FileUpload[]>([
    {
      id: '1',
      name: 'Mathematics_Chapter_1.pdf',
      size: 2400000,
      type: 'application/pdf',
      uploadedAt: new Date('2024-01-15'),
      progress: 100,
      url: '#',
      subject: 'Mathematics'
    },
    {
      id: '2',
      name: 'Physics_Lecture_Video.mp4',
      size: 125000000,
      type: 'video/mp4',
      uploadedAt: new Date('2024-01-14'),
      progress: 100,
      url: '#',
      subject: 'Physics'
    },
    {
      id: '3',
      name: 'Chemistry_Notes.docx',
      size: 850000,
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      uploadedAt: new Date('2024-01-13'),
      progress: 100,
      url: '#',
      subject: 'Chemistry'
    }
  ]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [subject, setSubject] = useState("");
  const [subjectError, setSubjectError] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image className="h-8 w-8 text-green-500" />;
    if (type.startsWith('video/')) return <Video className="h-8 w-8 text-red-500" />;
    if (type.startsWith('audio/')) return <Music className="h-8 w-8 text-purple-500" />;
    return <FileText className="h-8 w-8 text-blue-500" />;
  };

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFileUpload(droppedFiles);
  }, []);

  const handleFileUpload = (fileList: File[]) => {
    if (!subject.trim()) {
      setSubjectError("Subject name is required before uploading.");
      return;
    }
    setSubjectError("");
    fileList.forEach((file) => {
      const fileId = Date.now().toString() + Math.random().toString(36);
      const newFile: FileUpload = {
        id: fileId,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date(),
        progress: 0,
        // Optionally, you can add subject to FileUpload type if you want to display it per file
        subject: subject.trim()
      };

      setFiles(prev => [...prev, newFile]);

      // Simulate upload progress
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          setFiles(prev => prev.map(f => 
            f.id === fileId ? { ...f, progress: 100, url: '#' } : f
          ));
        }
        setFiles(prev => prev.map(f => 
          f.id === fileId ? { ...f, progress } : f
        ));
      }, 200);
    });
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileUpload(Array.from(e.target.files));
    }
  };

  const handleChooseFilesClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Placeholder for quiz generation logic
  const handleGenerateQuiz = (file: FileUpload) => {
    alert(`Quiz generation for '${file.name}' coming soon!`);
  };

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
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          File Uploads
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Upload and manage your learning materials
        </p>
      </motion.div>

      {/* Upload Area */}
      <motion.div variants={itemVariants}>
        <Card className="p-8">
          <div
            className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
              isDragOver
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <motion.div
              className="space-y-6"
              animate={{ scale: isDragOver ? 1.05 : 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
            >
              <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <Upload className="h-8 w-8 text-white" />
              </div>

              {/* Subject Name Input */}
              <div className="space-y-2">
                <label htmlFor="subject" className="block text-left text-gray-700 dark:text-gray-300 font-medium mb-1">Subject Name <span className="text-red-500">*</span></label>
                <Input
                  id="subject"
                  type="text"
                  value={subject}
                  onChange={e => setSubject(e.target.value)}
                  placeholder="Enter subject name (required)"
                  required
                  className="mb-1"
                />
                {subjectError && <p className="text-red-500 text-sm">{subjectError}</p>}
              </div>

              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  {isDragOver ? 'Drop files here' : 'Upload your files'}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Drag and drop files here, or click to browse
                </p>
              </div>

              <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <FileText className="h-4 w-4" /> Documents
                </span>
                <span className="flex items-center gap-1">
                  <Image className="h-4 w-4" /> Images
                </span>
                <span className="flex items-center gap-1">
                  <Video className="h-4 w-4" /> Videos
                </span>
                <span className="flex items-center gap-1">
                  <Music className="h-4 w-4" /> Audio
                </span>
              </div>

              <div className="space-y-4">
                <input
                  type="file"
                  multiple
                  onChange={handleFileInputChange}
                  className="hidden"
                  ref={fileInputRef}
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mp3,.wav"
                  disabled={!subject.trim()}
                />
                <Button className="cursor-pointer" onClick={handleChooseFilesClick} disabled={!subject.trim()}>
                  Choose Files
                </Button>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Maximum file size: 100MB
                </p>
              </div>
            </motion.div>
          </div>
        </Card>
      </motion.div>

      {/* File List */}
      <motion.div variants={itemVariants}>
        <Card className="p-6">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
            Uploaded Files ({files.length})
          </h2>
          
          <div className="space-y-4">
            {files.map((file, index) => (
              <motion.div
                key={file.id}
                className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex-shrink-0">
                  {getFileIcon(file.type)}
                </div>
                
                <div className="flex-grow min-w-0">
                  <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                    {file.name}
                  </h3>
                  {file.subject && (
                    <p className="text-xs text-blue-600 dark:text-blue-400 font-semibold">Subject: {file.subject}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>{formatFileSize(file.size)}</span>
                    <span>•</span>
                    <span>{file.uploadedAt.toLocaleDateString()}</span>
                  </div>
                  
                  {file.progress < 100 ? (
                    <div className="mt-2">
                      <Progress value={file.progress} className="h-2" />
                      <p className="text-xs text-gray-500 mt-1">
                        Uploading... {Math.round(file.progress)}%
                      </p>
                    </div>
                  ) : (
                    <div className="mt-2">
                      <span className="inline-flex items-center gap-1 text-xs text-green-600 dark:text-green-400">
                        ✓ Upload complete
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center gap-2">
                  {file.progress === 100 && (
                    <>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      {/* Show Generate Quiz for document files only */}
                      {['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(file.type) && (
                        <Button variant="outline" size="sm" onClick={() => handleGenerateQuiz(file)}>
                          Generate Quiz
                        </Button>
                      )}
                    </>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(file.id)}
                    className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/20"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </motion.div>
            ))}
            
            {files.length === 0 && (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <Upload className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No files uploaded yet</p>
                <p className="text-sm">Upload your first file to get started</p>
              </div>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Upload Statistics */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950/20 dark:to-blue-900/20 border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500 rounded-xl">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                  {files.filter(f => f.progress === 100).length}
                </h3>
                <p className="text-blue-600 dark:text-blue-400 font-medium">Total Files</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/20 dark:to-green-900/20 border-green-200 dark:border-green-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-500 rounded-xl">
                <Upload className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-green-700 dark:text-green-300">
                  {formatFileSize(files.reduce((acc, file) => acc + file.size, 0))}
                </h3>
                <p className="text-green-600 dark:text-green-400 font-medium">Total Size</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950/20 dark:to-purple-900/20 border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-500 rounded-xl">
                <Video className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-purple-700 dark:text-purple-300">
                  {files.filter(f => f.type.startsWith('video/')).length}
                </h3>
                <p className="text-purple-600 dark:text-purple-400 font-medium">Video Files</p>
              </div>
            </div>
          </Card>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default UploadPage;