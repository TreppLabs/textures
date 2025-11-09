"use client";

import { useState } from 'react';

interface Theme {
  id: number;
  name: string;
  description: string;
  base_prompt: string;
  created_at: string;
}

interface GenerationControlsProps {
  theme: Theme;
  onGenerate: (params: { numVariations: number; size: string; quality: string }) => void;
  isGenerating: boolean;
}

export function GenerationControls({ theme, onGenerate, isGenerating }: GenerationControlsProps) {
  const [numVariations, setNumVariations] = useState(4);
  const [generationParams, setGenerationParams] = useState({
    size: '1024x1024',
    quality: 'standard'
  });

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Generation Controls</h2>
      
      {/* Theme Info */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-900 mb-2">Current Theme: {theme.name}</h3>
        <p className="text-sm text-gray-600 mb-2">{theme.description}</p>
        <div className="text-xs text-gray-500 font-mono bg-white p-2 rounded border">
          {theme.base_prompt}
        </div>
      </div>

      {/* Generation Parameters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label htmlFor="num-variations" className="block text-sm font-medium text-gray-700 mb-1">
            Number of Variations
          </label>
          <select
            id="num-variations"
            value={numVariations}
            onChange={(e) => setNumVariations(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value={4}>4 variations</option>
            <option value={5}>5 variations</option>
            <option value={6}>6 variations</option>
          </select>
        </div>

        <div>
          <label htmlFor="image-size" className="block text-sm font-medium text-gray-700 mb-1">
            Image Size
          </label>
          <select
            id="image-size"
            value={generationParams.size}
            onChange={(e) => setGenerationParams(prev => ({ ...prev, size: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value="1024x1024">1024×1024 (Square)</option>
            <option value="1792x1024">1792×1024 (Landscape)</option>
            <option value="1024x1792">1024×1792 (Portrait)</option>
          </select>
        </div>

        <div>
          <label htmlFor="image-quality" className="block text-sm font-medium text-gray-700 mb-1">
            Quality
          </label>
          <select
            id="image-quality"
            value={generationParams.quality}
            onChange={(e) => setGenerationParams(prev => ({ ...prev, quality: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
          >
            <option value="standard">Standard</option>
            <option value="hd">HD</option>
          </select>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          This will generate {numVariations} texture variations using the current theme
        </div>
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!isGenerating) {
              onGenerate({ 
                numVariations, 
                size: generationParams.size, 
                quality: generationParams.quality 
              });
            }
          }}
          disabled={isGenerating}
          className={`px-6 py-3 rounded-md font-medium transition-colors ${
            isGenerating
              ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
          }`}
        >
          {isGenerating ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Generating...</span>
            </div>
          ) : (
            'Generate Textures'
          )}
        </button>
      </div>

      {/* Info */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <div className="text-sm text-blue-800">
          <strong>Tip:</strong> After generation, rate the images to help the AI learn which patterns work best for this theme.
        </div>
      </div>
    </div>
  );
}
