import { useState } from "react";
import "./App.css";
import { Button } from "./components/ui/button";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <Button
        variant="outline"
        size="default"
        className="m-4 caret-amber-300"
        onClick={() => setCount((count) => count + 1)}
      ></Button>


      <h1 className="text-3xl font-bold underline">Hello world! {count}</h1>
    </>
  );
}

export default App;
