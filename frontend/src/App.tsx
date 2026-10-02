import { useEffect, useState } from "react";

export default function App() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/health")
      .then((r) => r.json())
      .then((d) => setStatus(`API ${d.status}, DB ${d.database}`))
      .catch(() => setStatus("API unreachable"));
  }, []);

  return <h1 className="p-8 text-2xl font-semibold">PlaceIQ: {status}</h1>;
}
