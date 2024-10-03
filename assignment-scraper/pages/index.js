import { useState, useEffect } from 'react';

export default function Home() {
  const [classes, setClasses] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [className, setClassName] = useState('');
  const [classType, setClassType] = useState('canvas');
  const [courseId, setCourseId] = useState('');
  const [fileId, setFileId] = useState('');

  // Load classes from the server when the page loads
  useEffect(() => {
    fetch('/api/classes')
      .then(response => response.json())
      .then(data => {
        setClasses(data.classes || []);
      })
      .catch(error => console.error('Error fetching classes:', error));
  }, []);

  // Add a class to the list
  const addClass = () => {
    if (!className || !courseId) {
      alert('Please enter both Class Name and Course ID.');
      return;
    }

    const newClass = { class_name: className, type: classType, course_id: courseId, file_id: fileId };
    const updatedClasses = [...classes, newClass];
    setClasses(updatedClasses);

    saveClasses(updatedClasses);

    // Reset form fields
    setClassName('');
    setCourseId('');
    setFileId('');
  };

  // Save classes to the server
  const saveClasses = (classesToSave) => {
    fetch('/api/classes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ classes: classesToSave }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Classes saved successfully.');
      })
      .catch(error => console.error('Error saving classes:', error));
  };

  // Remove a class from the list
  const removeClass = (index) => {
    const updatedClasses = classes.filter((_, i) => i !== index);
    setClasses(updatedClasses);
    saveClasses(updatedClasses);
  };

  // Fetch assignments from the backend when the Run button is clicked
  const fetchAssignments = () => {
    fetch('/fetch-assignments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}), // No need to send classes; backend will use saved classes
    })
      .then(response => response.json())
      .then(data => {
        setAssignments(data);
      })
      .catch(error => console.error('Error fetching assignments:', error));
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Class Assignments</h1>

      <div className="flex flex-wrap -mx-4">
        {/* Left Column */}
        <div className="w-full md:w-1/2 px-4">
          <form
            className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4"
            onSubmit={(e) => {
              e.preventDefault();
              addClass();
            }}
          >
            <h2 className="text-2xl font-semibold mb-4">Add Classes</h2>

            <div className="mb-4">
              <label htmlFor="className" className="block text-gray-700 text-sm font-bold mb-2">
                Class Name
              </label>
              <input
                type="text"
                id="className"
                value={className}
                onChange={(e) => setClassName(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                placeholder="Enter Class Name"
              />
            </div>

            <div className="mb-4">
              <label htmlFor="classType" className="block text-gray-700 text-sm font-bold mb-2">
                Class Type
              </label>
              <select
                id="classType"
                value={classType}
                onChange={(e) => setClassType(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              >
                <option value="canvas">Canvas</option>
                <option value="docx">DOCX</option>
                <option value="pdf">PDF</option>
              </select>
            </div>

            <div className="mb-4">
              <label htmlFor="courseId" className="block text-gray-700 text-sm font-bold mb-2">
                Course ID
              </label>
              <input
                type="text"
                id="courseId"
                value={courseId}
                onChange={(e) => setCourseId(e.target.value)}
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                placeholder="Enter Course ID"
              />
            </div>

            {(classType === 'docx' || classType === 'pdf') && (
              <div className="mb-4">
                <label htmlFor="fileId" className="block text-gray-700 text-sm font-bold mb-2">
                  File ID
                </label>
                <input
                  type="text"
                  id="fileId"
                  value={fileId}
                  onChange={(e) => setFileId(e.target.value)}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  placeholder="Enter File ID (if applicable)"
                />
              </div>
            )}

            <div className="flex items-center justify-between">
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Add Class
              </button>
              <button
                type="button"
                onClick={fetchAssignments}
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Run
              </button>
            </div>
          </form>

          <h3 className="text-2xl font-semibold mb-4">Class List</h3>
          <ul className="list-disc pl-5">
            {classes.map((cls, index) => (
              <li key={index} className="mb-2 flex justify-between items-center">
                <span>
                  <strong>{cls.class_name}</strong> ({cls.type}) - Course ID: {cls.course_id}
                  {cls.file_id ? ` | File ID: ${cls.file_id}` : ''}
                </span>
                <button
                  onClick={() => removeClass(index)}
                  className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded focus:outline-none focus:shadow-outline"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Right Column */}
        <div className="w-full md:w-1/2 px-4">
          <h3 className="text-2xl font-semibold mb-4">Assignments Due This Week</h3>
          <div>
            {assignments.length === 0 ? (
              <p>No assignments due this week.</p>
            ) : (
              assignments.map((assignment, index) => (
                <div key={index} className="bg-gray-100 p-4 rounded-lg mb-4">
                  <h4 className="text-xl font-bold mb-2">{assignment.title}</h4>
                  <p className="mb-2">{assignment.description}</p>
                  <small className="text-gray-600">
                    Due: {assignment.due_date} | Class: {assignment.class_name}
                  </small>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}