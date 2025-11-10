"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ThemeSelector } from '@/components/ThemeSelector';
import { ImageGrid } from '@/components/ImageGrid';
import { GenerationControls } from '@/components/GenerationControls';

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

export default function Dashboard() {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [recentImages, setRecentImages] = useState<Image[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    // Load themes and recent images
    loadThemes();
    loadRecentImages();
  }, []);

  const loadThemes = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/themes/`);
      if (response.ok) {
        const data = await response.json();
        setThemes(data);
      }
    } catch (error) {
      console.error('Failed to load themes:', error);
    }
  };

  const loadRecentImages = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/images/recent`);
      if (response.ok) {
        const data = await response.json();
        setRecentImages(data);
      }
    } catch (error) {
      console.error('Failed to load recent images:', error);
    }
  };

  const handleRatingChange = async (imageId: number, rating: number) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/images/${imageId}/rate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rating }),
      });

      if (response.ok) {
        // Update local state
        setRecentImages(prev => 
          prev.map(img => 
            img.id === imageId ? { ...img, rating } : img
          )
        );
      }
    } catch (error) {
      console.error('Failed to update rating:', error);
    }
  };

  const handleThemeSelect = (theme: Theme) => {
    setSelectedTheme(theme);
  };

  const handleGenerate = async (params: { numVariations: number; size: string; quality: string }) => {
    if (!selectedTheme) {
      alert('Please select a theme first');
      return;
    }
    
    setIsGenerating(true);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme_id: selectedTheme.id,
          num_variations: params.numVariations,
          size: params.size,
          quality: params.quality
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Use the images from the response directly
        if (data.images && data.images.length > 0) {
          const convertedImages = data.images.map((img: any) => ({
            id: img.id,
            filename: img.filename,
            file_path: img.file_path,
            prompt: img.prompt,
            rating: img.rating || null,
            created_at: img.created_at
          }));
          setRecentImages(convertedImages);
        } else {
          // If no images in response, try to reload from API
          loadRecentImages();
        }
        
        alert(`Successfully generated ${data.variations_generated} texture variation${data.variations_generated !== 1 ? 's' : ''}!`);
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Failed to generate images' }));
        alert(`Failed to generate images: ${errorData.error || `Error ${response.status}`}`);
      }
    } catch (error) {
      console.error('Failed to generate images:', error);
      alert(`Failed to connect to API: ${error instanceof Error ? error.message : 'Unknown error'}\n\nMake sure the backend is running at http://localhost:8000`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Textures Generator
          </h1>
          <p className="text-gray-600">
            Create laser-cuttable black and white textures. Each theme aims to produce one favorite image.
          </p>
        </div>

        {/* Theme Selection */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Select Theme</h2>
          <ThemeSelector
            themes={themes}
            selectedTheme={selectedTheme}
            onThemeSelect={handleThemeSelect}
            onCreateTheme={() => {/* Theme creation handled in ThemeSelector */}}
            onThemeCreated={loadThemes}
            onThemeDeleted={loadThemes}
          />
        </div>

        {/* Generation Controls */}
        {selectedTheme && (
          <div className="mb-8">
            <GenerationControls
              theme={selectedTheme}
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
            />
          </div>
        )}

        {/* Recent Images */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-gray-900">Recent Generations</h2>
            <Link 
              href="/gallery" 
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              View All →
            </Link>
          </div>
          <ImageGrid 
            images={recentImages} 
            showRatings={true} 
            onRatingChange={handleRatingChange}
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link 
            href="/gallery"
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Gallery</h3>
            <p className="text-gray-600">Browse all generated textures</p>
          </Link>
          
          <Link 
            href="/analytics"
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Analytics</h3>
            <p className="text-gray-600">Analyze keyword effectiveness</p>
          </Link>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">New Theme</h3>
            <p className="text-gray-600">Create a new texture theme</p>
          </div>
        </div>
      </div>
    </div>
  );
}