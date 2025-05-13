import React from "react"
import { useState } from 'react';
function App() {
  
  const [text, setText] = useState('');
  const [option, setOption] = useState('0'); 
  const [theme, setTheme] = useState('');
  const [matrix, setMatrix] = useState([]);
  const [image, setImage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setMatrix([]);
    setImage('');
    try {
      const response = await fetch('https://assignment-gb8w.onrender.com/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, option: parseInt(option) }),
      });

      const data = await response.json();

      if (response.ok) {
        setTheme(data.theme);
        if (parseInt(option) === 1) {
          setImage(`data:image/png;base64,${data.image}`);
        } else {
          setMatrix(data.matrix);
        }
      } else {
        setError(data.error || 'Something went wrong.');
      }
    } catch (err) {
      setError('Server not reachable.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-32 p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Pattern Generator</h2>

      <div className="space-y-4">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">write something</label>
          <input
            id="prompt"
            type="text"
            placeholder="like ocean waves, clouds, sun..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
          />
        </div>

        <div>
          <p className="text-sm font-medium text-gray-700 mb-1">Select output type</p>
          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                value="0"
                checked={option === '0'}
                onChange={(e) => setOption(e.target.value)}
                className="mr-2"
              />
              Matrix
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                value="1"
                checked={option === '1'}
                onChange={(e) => setOption(e.target.value)}
                className="mr-2"
              />
              Image
            </label>
          </div>
        </div>

        <button 
          onClick={handleGenerate} 
          disabled={loading || !text.trim()}
          className={`w-full py-2 px-4 rounded-lg font-medium text-white transition ${loading || !text.trim() ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
        >
          {loading ? 'Processing...' : 'Enter'}
        </button>

        {error && (
          <div className="p-3 bg-red-50 border-l-4 border-red-500 rounded">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}
      </div>

      {loading && (
        <div className="mt-6 flex justify-center">
          <div className="animate-pulse w-full h-64 bg-gray-200 rounded-md"></div>
        </div>
      )}

      {theme && (
        <p className="text-center mt-6 mb-2 text-gray-700">
           Theme: <span className="font-semibold text-blue-600">{theme}</span>
        </p>
      )}

      {matrix.length > 0 && (
        <div className="mt-4">
          <div
            className="grid"
            style={{
              gridTemplateColumns: `repeat(64, 4px)`,
              gridTemplateRows: `repeat(64, 4px)`,
              gap: '1px',
              justifyContent: 'center',
              backgroundColor: '#ccc',
              padding: '5px',
              borderRadius: '8px'
            }}
          >
            {matrix.flat().map((cell, idx) => (
              <div
                key={idx}
                className="rounded-sm"
                style={{
                  width: '4px',
                  height: '4px',
                  backgroundColor: cell ? '#1D4ED8' : '#fff'
                }}
              ></div>
            ))}
          </div>
        </div>
      )}

      {image && (
        <div className="mt-6 flex justify-center">
          <img src={image} alt="Generated Theme" className="rounded shadow-md border w-100 h-100 object-contain" />
        </div>
      )}
    </div>
  );
  
}

export default App;
