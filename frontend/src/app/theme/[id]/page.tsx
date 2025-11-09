"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ImageGrid } from '@/components/ImageGrid';
import { GenerationControls } from '@/components/GenerationControls';
import { PromptEditor } from '@/components/PromptEditor';
import Link from 'next/link';

interface Theme {
  id: number;
  name: string;
  description: string;
  base_prompt: string;
  created_at: string;
}

interface Image {
  id: number;
  filename: string;
  file_path: string;
  prompt: string;
  rating: number | null;
  created_at: string;
}

export default function ThemePage() {
  const params = useParams();
  const themeId = params.id as string;
  
  const [theme, setTheme] = useState<Theme | null>(null);
  const [images, setImages] = useState<Image[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (themeId) {
      loadTheme();
      loadThemeImages();
    }
  }, [themeId]);

  const loadTheme = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/themes/${themeId}`);
      if (response.ok) {
        const data = await response.json();
        setTheme(data);
      }
    } catch (error) {
      console.error('Failed to load theme:', error);
    }
  };

  const loadThemeImages = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/themes/${themeId}/images`);
      if (response.ok) {
        const data = await response.json();
        setImages(data);
      }
    } catch (error) {
      console.error('Failed to load theme images:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!theme) return;
    
    setIsGenerating(true);
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme_id: theme.id,
          num_variations: 4
        }),
      });

      if (response.ok) {
        // Refresh images
        loadThemeImages();
      }
    } catch (error) {
      console.error('Failed to generate images:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRatingChange = async (imageId: number, rating: number) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/images/${imageId}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rating }),
      });

      if (response.ok) {
        // Update local state
        setImages(prev => 
          prev.map(img => 
            img.id === imageId ? { ...img, rating } : img
          )
        );
      }
    } catch (error) {
      console.error('Failed to update rating:', error);
    }
  };

  const handlePromptUpdate = async (newPrompt: string) => {
    if (!theme) return;

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/themes/${theme.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ base_prompt: newPrompt }),
      });

      if (response.ok) {
        const updatedTheme = await response.json();
        setTheme(updatedTheme);
      }
    } catch (error) {
      console.error('Failed to update prompt:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading theme...</div>
        </div>
      </div>
    );
  }

  if (!theme) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">Theme not found</div>
          <Link href="/" className="text-blue-600 hover:text-blue-800">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{theme.name}</h1>
              <p className="text-gray-600">{theme.description}</p>
            </div>
            <Link 
              href="/" 
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Prompt Editor */}
        <div className="mb-8">
          <PromptEditor
            prompt={theme.base_prompt}
            onPromptUpdate={handlePromptUpdate}
          />
        </div>

        {/* Generation Controls */}
        <div className="mb-8">
          <GenerationControls
            theme={theme}
            onGenerate={handleGenerate}
            isGenerating={isGenerating}
          />
        </div>

        {/* Images Grid */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-900">
              Generated Images ({images.length})
            </h2>
            <Link 
              href={`/theme/${themeId}/history`}
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              View History →
            </Link>
          </div>
          <ImageGrid
            images={images}
            showRatings={true}
            onRatingChange={handleRatingChange}
          />
        </div>
      </div>
    </div>
  );
}
