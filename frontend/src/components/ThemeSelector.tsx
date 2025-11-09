"use client";

import { useState } from 'react';

interface Theme {
  id: number;
  name: string;
  description: string;
  base_prompt: string;
  created_at: string;
}

interface ThemeSelectorProps {
  themes: Theme[];
  selectedTheme: Theme | null;
  onThemeSelect: (theme: Theme) => void;
  onCreateTheme: () => void;
  onThemeCreated?: () => void; // Callback to refresh themes list
}

export function ThemeSelector({ themes, selectedTheme, onThemeSelect, onCreateTheme, onThemeCreated }: ThemeSelectorProps) {
  const [isCreating, setIsCreating] = useState(false);
  const [newThemeName, setNewThemeName] = useState('');
  const [newThemePrompt, setNewThemePrompt] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateTheme = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newThemeName.trim() || !newThemePrompt.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/themes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newThemeName,
          base_prompt: newThemePrompt,
          description: `Theme created on ${new Date().toLocaleDateString()}`
        }),
      });

      if (response.ok) {
        const newTheme = await response.json();
        onThemeSelect(newTheme);
        setNewThemeName('');
        setNewThemePrompt('');
        setIsCreating(false);
        setError(null);
        // Refresh themes list
        if (onThemeCreated) {
          onThemeCreated();
        }
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Failed to create theme' }));
        setError(errorData.error || `Error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to create theme:', error);
      setError('Failed to connect to API. Make sure the backend is running at http://localhost:8000');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Existing Themes */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {themes.map((theme) => (
          <div
            key={theme.id}
            onClick={() => onThemeSelect(theme)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
              selectedTheme?.id === theme.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 bg-white'
            }`}
          >
            <h3 className="font-semibold text-gray-900 mb-2">{theme.name}</h3>
            <p className="text-sm text-gray-600 mb-2">{theme.description}</p>
            <p className="text-xs text-gray-500 font-mono bg-gray-100 p-2 rounded">
              {theme.base_prompt}
            </p>
          </div>
        ))}
      </div>

      {/* Create New Theme */}
      {isCreating ? (
        <form onSubmit={handleCreateTheme} className="bg-white p-6 border-2 border-dashed border-gray-300 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Theme</h3>
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="theme-name" className="block text-sm font-medium text-gray-700 mb-1">
                Theme Name
              </label>
              <input
                id="theme-name"
                type="text"
                value={newThemeName}
                onChange={(e) => setNewThemeName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                placeholder="e.g., Organic Cellular"
                required
                disabled={isSubmitting}
              />
            </div>
            <div>
              <label htmlFor="theme-prompt" className="block text-sm font-medium text-gray-700 mb-1">
                Base Prompt
              </label>
              <textarea
                id="theme-prompt"
                value={newThemePrompt}
                onChange={(e) => setNewThemePrompt(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
                rows={3}
                placeholder="e.g., organic cellular structure with ##flowing lines and ##fractal patterns"
                required
                disabled={isSubmitting}
              />
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <span className="flex items-center">
                    <span className="animate-spin mr-2">⏳</span>
                    Creating...
                  </span>
                ) : (
                  'Create Theme'
                )}
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsCreating(false);
                  setError(null);
                  setNewThemeName('');
                  setNewThemePrompt('');
                }}
                disabled={isSubmitting}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      ) : (
        <button
          onClick={() => setIsCreating(true)}
          className="w-full p-6 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-800 transition-colors"
        >
          <div className="text-center">
            <div className="text-2xl mb-2">+</div>
            <div className="font-medium">Create New Theme</div>
            <div className="text-sm">Start a new texture generation theme</div>
          </div>
        </button>
      )}
    </div>
  );
}
