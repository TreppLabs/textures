"use client";

import { useState } from 'react';

interface PromptEditorProps {
  prompt: string;
  onPromptUpdate: (newPrompt: string) => void;
}

export function PromptEditor({ prompt, onPromptUpdate }: PromptEditorProps) {
  const [editing, setEditing] = useState(false);
  const [editPrompt, setEditPrompt] = useState(prompt);

  const handleSave = () => {
    onPromptUpdate(editPrompt);
    setEditing(false);
  };

  const handleCancel = () => {
    setEditPrompt(prompt);
    setEditing(false);
  };

  const extractKeywords = (text: string) => {
    const keywordRegex = /##(\w+)/g;
    const keywords = [];
    let match;
    while ((match = keywordRegex.exec(text)) !== null) {
      keywords.push(match[1]);
    }
    return keywords;
  };

  const keywords = extractKeywords(prompt);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Base Prompt</h2>
        {!editing && (
          <button
            onClick={() => setEditing(true)}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Edit Prompt
          </button>
        )}
      </div>

      {editing ? (
        <div className="space-y-4">
          <div>
            <label htmlFor="prompt-edit" className="block text-sm font-medium text-gray-700 mb-2">
              Edit the base prompt for this theme
            </label>
            <textarea
              id="prompt-edit"
              value={editPrompt}
              onChange={(e) => setEditPrompt(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              placeholder="Enter your base prompt here..."
            />
            <div className="mt-2 text-sm text-gray-600">
              Use <code className="bg-gray-100 px-1 rounded">##keyword</code> syntax to tag keywords for tracking
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              Save Changes
            </button>
            <button
              onClick={handleCancel}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
              {prompt}
            </pre>
          </div>
          
          {keywords.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">Keywords in this prompt:</h3>
              <div className="flex flex-wrap gap-2">
                {keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium"
                  >
                    ##{keyword}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
