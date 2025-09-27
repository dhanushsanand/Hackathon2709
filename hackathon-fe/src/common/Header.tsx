import React from "react";
import { BookOpen } from "lucide-react";

export function Header(): React.JSX.Element {
  return (
    <header className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-5 shadow-md">
      <div className="container mx-auto flex flex-col items-center gap-2 px-4">
        <div className="flex items-center gap-2">
          <BookOpen className="h-7 w-7 text-white" />
          <h1 className="text-xl md:text-2xl font-bold tracking-wide">
            EduQuiz
          </h1>
        </div>
        <p className="text-sm font-medium opacity-90">
          Fun-Based Learning Made Simple
        </p>
      </div>
    </header>
  );
}
