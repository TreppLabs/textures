"use client";

import { useState, useEffect } from 'react';
import { ImageGrid } from '@/components/ImageGrid';
import Link from 'next/link';

interface Image {
  id: number;
  filename: string;
  file_path: string;
  prompt: string;
  rating: number | null;
  created_at: string;
}

export default function GalleryPage() {
  const [images, setImages] = useState<Image[]>([]);
  const [filteredImages, setFilteredImages] = useState<Image[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'top-per-theme' | 'all'>('top-per-theme');
  const [filters, setFilters] = useState({
    minRating: 0,
    searchTerm: '',
    sortBy: 'newest' as 'newest' | 'oldest' | 'rating'
  });

  useEffect(() => {
    loadImages();
  }, [viewMode]);

  useEffect(() => {
    applyFilters();
  }, [images, filters]);

  const loadImages = async () => {
    try {
      setIsLoading(true);
      const endpoint = viewMode === 'top-per-theme' 
        ? '/api/images/top-per-theme'
        : '/api/images';
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`);
      if (response.ok) {
        const data = await response.json();
        setImages(data);
      }
    } catch (error) {
      console.error('Failed to load images:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...images];

    // Filter by rating
    if (filters.minRating > 0) {
      filtered = filtered.filter(img => (img.rating || 0) >= filters.minRating);
    }

    // Filter by search term
    if (filters.searchTerm) {
      const searchLower = filters.searchTerm.toLowerCase();
      filtered = filtered.filter(img => 
        img.prompt.toLowerCase().includes(searchLower) ||
        img.filename.toLowerCase().includes(searchLower)
      );
    }

    // Sort
    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'newest':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        case 'oldest':
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        case 'rating':
          return (b.rating || 0) - (a.rating || 0);
        default:
          return 0;
      }
    });

    setFilteredImages(filtered);
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading gallery...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Gallery</h1>
              <p className="text-gray-600">
                {viewMode === 'top-per-theme' 
                  ? `Top image from each theme (${filteredImages.length} images)`
                  : `All generated textures (${filteredImages.length} images)`
                }
              </p>
            </div>
            <Link 
              href="/" 
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Back to Dashboard
            </Link>
          </div>
          
          {/* View Mode Toggle */}
          <div className="flex items-center space-x-4 bg-white p-4 rounded-lg shadow-sm">
            <span className="text-sm font-medium text-gray-700">View:</span>
            <button
              onClick={() => setViewMode('top-per-theme')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'top-per-theme'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Top per Theme
            </button>
            <button
              onClick={() => setViewMode('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Images
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Rating Filter */}
            <div>
              <label htmlFor="min-rating" className="block text-sm font-medium text-gray-700 mb-1">
                Minimum Rating
              </label>
              <select
                id="min-rating"
                value={filters.minRating}
                onChange={(e) => setFilters(prev => ({ ...prev, minRating: parseInt(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={0}>All ratings</option>
                <option value={1}>1+ stars</option>
                <option value={2}>2+ stars</option>
                <option value={3}>3+ stars</option>
                <option value={4}>4+ stars</option>
                <option value={5}>5 stars only</option>
              </select>
            </div>

            {/* Search */}
            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                id="search"
                type="text"
                value={filters.searchTerm}
                onChange={(e) => setFilters(prev => ({ ...prev, searchTerm: e.target.value }))}
                placeholder="Search prompts or filenames..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Sort */}
            <div>
              <label htmlFor="sort" className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <select
                id="sort"
                value={filters.sortBy}
                onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>
          </div>
        </div>

        {/* Images Grid */}
        <ImageGrid
          images={filteredImages}
          showRatings={true}
          onRatingChange={handleRatingChange}
        />

        {filteredImages.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg mb-2">No images found</div>
            <div className="text-gray-400 text-sm">
              {filters.minRating > 0 || filters.searchTerm 
                ? 'Try adjusting your filters' 
                : 'Generate some textures to see them here'
              }
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
