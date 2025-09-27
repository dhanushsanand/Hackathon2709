import { useState } from "react";
import "./App.css";
import { Button } from "./components/ui/button";
import PdfUpload from "./appComponents/PdfUpload";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <PdfUpload/>
    </>
  );
}

export default App;
