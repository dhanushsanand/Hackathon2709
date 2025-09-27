import React from "react";

export function Footer(): React.JSX.Element {
return (
<footer className="bg-gray-800 text-gray-200 py-4 text-center mt-6">
<p className="text-sm">© {new Date().getFullYear()} EduQuiz. All rights reserved.</p>
</footer>
);
}