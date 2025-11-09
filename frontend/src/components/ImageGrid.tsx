"use client";

import { useState } from 'react';
import { RatingStars } from './RatingStars';

interface Image {
  id: number;
  filename: string;
  file_path: string;
  prompt: string;
  rating: number | null;
  created_at: string;
}

interface ImageGridProps {
  images: Image[];
  showRatings?: boolean;
  onRatingChange?: (imageId: number, rating: number) => void;
}

export function ImageGrid({ images, showRatings = false, onRatingChange }: ImageGridProps) {
  const [ratingImages, setRatingImages] = useState<{ [key: number]: number }>({});

  const handleRatingChange = (imageId: number, rating: number) => {
    setRatingImages(prev => ({ ...prev, [imageId]: rating }));
    if (onRatingChange) {
      onRatingChange(imageId, rating);
    }
  };

  if (images.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 text-lg">No images generated yet</div>
        <div className="text-gray-400 text-sm mt-2">Create a theme and generate some textures to get started</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {images.map((image) => (
        <div key={image.id} className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Image */}
          <div className="aspect-square bg-gray-100 relative flex items-center justify-center">
            <img
              src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/images/${image.file_path}`}
              alt={`Generated texture: ${image.prompt}`}
              className="w-full h-full object-cover"
              onError={(e) => {
                // Hide the broken image and show placeholder
                const target = e.target as HTMLImageElement;
                target.classList.add('hidden');
                const parent = target.parentElement;
                if (parent) {
                  const placeholder = parent.querySelector('.image-placeholder');
                  if (placeholder) {
                    placeholder.classList.remove('hidden');
                  }
                }
              }}
              onLoad={(e) => {
                // Hide placeholder when image loads
                const target = e.target as HTMLImageElement;
                const parent = target.parentElement;
                if (parent) {
                  const placeholder = parent.querySelector('.image-placeholder');
                  if (placeholder) {
                    placeholder.classList.add('hidden');
                  }
                }
              }}
            />
            {/* Placeholder for images that haven't been generated yet */}
            <div className="image-placeholder absolute inset-0 flex flex-col items-center justify-center p-4 text-center bg-gray-100 hidden">
              <div className="text-4xl mb-2">🎨</div>
              <div className="text-sm font-medium text-gray-700 mb-1">Generated Texture</div>
              <div className="text-xs text-gray-500">{image.filename}</div>
              <div className="text-xs text-gray-400 mt-2">
                Image file not available yet
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-4">
            {/* Prompt */}
            <div className="mb-3">
              <p className="text-sm text-gray-600 font-mono bg-gray-50 p-2 rounded">
                {image.prompt}
              </p>
            </div>

            {/* Rating */}
            {showRatings && (
              <div className="mb-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">Rating:</span>
                  <RatingStars
                    rating={ratingImages[image.id] || image.rating || 0}
                    onRatingChange={(rating) => handleRatingChange(image.id, rating)}
                    interactive={true}
                  />
                </div>
              </div>
            )}

            {/* Metadata */}
            <div className="text-xs text-gray-500">
              <div>ID: {image.id}</div>
              <div>Created: {new Date(image.created_at).toLocaleDateString()}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
