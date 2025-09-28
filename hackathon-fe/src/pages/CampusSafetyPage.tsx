

import Chatbot from "../components/ui/chatbot";

export default function CampusSafetyPage() {
  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      <h1 className="text-3xl font-bold mb-4">ASU Campus Safety</h1>
      <p className="mb-6 text-gray-700 dark:text-gray-300">
        Stay informed about campus safety updates, emergency contacts, and resources to keep you safe at Arizona State University.
      </p>

      {/* Safety Resources */}
      <section>
        <h2 className="text-2xl font-semibold mb-2">Safety Resources</h2>
        <ul className="list-disc pl-6 text-gray-600 dark:text-gray-400 space-y-1">
          <li>
            <a href="https://cfo.asu.edu/emergency" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">ASU Emergency Procedures</a>
          </li>
          <li>
            <a href="https://cfo.asu.edu/police" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">ASU Police Department</a>
          </li>
          <li>
            <a href="https://cfo.asu.edu/safety" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Campus Safety Guides</a>
          </li>
          <li>
            <a href="https://cfo.asu.edu/sites/default/files/asu-emergency-guide.pdf" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Download: ASU Emergency Guide (PDF)</a>
          </li>
        </ul>
      </section>

      {/* Contact Directory */}
      <section>
        <h2 className="text-2xl font-semibold mb-2">Contact Directory</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="font-bold mb-1">ASU Police (Emergency)</h3>
            <p className="text-gray-700 dark:text-gray-300">480-965-3456</p>
          </div>
          <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="font-bold mb-1">ASU Police (Non-Emergency)</h3>
            <p className="text-gray-700 dark:text-gray-300">480-965-3456</p>
          </div>
          <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="font-bold mb-1">ASU Health Services</h3>
            <p className="text-gray-700 dark:text-gray-300">480-965-3349</p>
          </div>
          <div className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg">
            <h3 className="font-bold mb-1">ASU Counseling Services</h3>
            <p className="text-gray-700 dark:text-gray-300">480-965-6146</p>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section>
        <h2 className="text-2xl font-semibold mb-2">Campus Safety FAQ</h2>
        <div className="space-y-4">
          <div>
            <h3 className="font-bold">How do I report an emergency?</h3>
            <p className="text-gray-700 dark:text-gray-300">Call ASU Police at 480-965-3456 or dial 911 for immediate assistance.</p>
          </div>
          <div>
            <h3 className="font-bold">Where can I find campus safety updates?</h3>
            <p className="text-gray-700 dark:text-gray-300">Visit the <a href="https://cfo.asu.edu/emergency" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">ASU Emergency website</a> for real-time alerts and updates.</p>
          </div>
          <div>
            <h3 className="font-bold">Are there safety escort services available?</h3>
            <p className="text-gray-700 dark:text-gray-300">Yes, ASU offers safety escort services. Call 480-965-3456 to request an escort.</p>
          </div>
          <div>
            <h3 className="font-bold">What should I do if I see suspicious activity?</h3>
            <p className="text-gray-700 dark:text-gray-300">Report it immediately to ASU Police at 480-965-3456 or use the ASU LiveSafe app.</p>
          </div>
        </div>
      </section>
      
  {/* Chatbot widget (floating) - open by default on this page */}
  <Chatbot initialOpen={true} title="ASU Safety Assistant" />
    </div>
  );
}
