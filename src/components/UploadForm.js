import React, { useState } from "react";

export default function UploadForm() {
  const [papers, setPapers] = useState(null);
  const [syllabus, setSyllabus] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!papers || !syllabus) {
      alert("Please upload both past papers and the syllabus.");
      return; // Stop execution if files are not provided
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("papers", papers);
    formData.append("syllabus", syllabus);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data && data.ranked_topics) {
        setResult(data.ranked_topics);
      } else {
        alert("No ranked topics found in the response.");
      }
    } catch (error) {
      console.error("Error uploading files:", error);
      alert("Failed to upload files. Try again.");
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-lg mx-auto bg-white rounded-xl shadow-md space-y-4">
      <h2 className="text-xl font-bold">Upload Past Papers & Syllabus</h2>
      <input
        type="file"
        accept=".zip"
        onChange={(e) => setPapers(e.target.files[0])}
        className="file-input" // Optional for styling
      />
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setSyllabus(e.target.files[0])}
        className="file-input" // Optional for styling
      />
      <button
        onClick={handleUpload}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded-md"
      >
        {loading ? "Uploading..." : "Submit"}
      </button>
      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded-md">
          <h3 className="font-bold">Analysis Results:</h3>
          <ul>
            {result.map((topic, index) => (
              <li key={index}> {topic}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
