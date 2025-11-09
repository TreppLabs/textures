"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface KeywordAnalysis {
  keyword: string;
  category: string;
  total_uses: number;
  average_rating: number;
  success_rate: number;
  confidence: string;
}

interface ThemeStats {
  theme_id: number;
  theme_name: string;
  generations_count: number;
  images_count: number;
  rated_images_count: number;
  average_rating: number | null;
  completion_rate: number;
}

export default function AnalyticsPage() {
  const [keywordAnalysis, setKeywordAnalysis] = useState<KeywordAnalysis[]>([]);
  const [themeStats, setThemeStats] = useState<ThemeStats[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTheme, setSelectedTheme] = useState<number | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, [selectedTheme]);

  const loadAnalytics = async () => {
    try {
      const [keywordsResponse, themesResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analytics/keywords${selectedTheme ? `?theme_id=${selectedTheme}` : ''}`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/themes`)
      ]);

      if (keywordsResponse.ok) {
        const keywordsData = await keywordsResponse.json();
        setKeywordAnalysis(keywordsData);
      }

      if (themesResponse.ok) {
        const themesData = await themesResponse.json();
        // Load stats for each theme
        const statsPromises = themesData.map(async (theme: any) => {
          const statsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/themes/${theme.id}/statistics`);
          if (statsResponse.ok) {
            return await statsResponse.json();
          }
          return null;
        });
        
        const stats = await Promise.all(statsPromises);
        setThemeStats(stats.filter(Boolean));
      }
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      'structural': 'bg-blue-100 text-blue-800',
      'organic': 'bg-green-100 text-green-800',
      'textural': 'bg-yellow-100 text-yellow-800',
      'map_like': 'bg-purple-100 text-purple-800',
      'geometric': 'bg-pink-100 text-pink-800',
      'visual': 'bg-indigo-100 text-indigo-800',
      'uncategorized': 'bg-gray-100 text-gray-800'
    };
    return colors[category as keyof typeof colors] || colors.uncategorized;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading analytics...</div>
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics</h1>
              <p className="text-gray-600">
                Analyze keyword effectiveness and theme performance
              </p>
            </div>
            <Link 
              href="/" 
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>

        {/* Theme Filter */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter by Theme</h2>
          <select
            value={selectedTheme || ''}
            onChange={(e) => setSelectedTheme(e.target.value ? parseInt(e.target.value) : null)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Themes</option>
            {themeStats.map((theme) => (
              <option key={theme.theme_id} value={theme.theme_id}>
                {theme.theme_name}
              </option>
            ))}
          </select>
        </div>

        {/* Theme Statistics */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Theme Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {themeStats.map((theme) => (
              <div key={theme.theme_id} className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{theme.theme_name}</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Images Generated:</span>
                    <span className="font-medium">{theme.images_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Rated Images:</span>
                    <span className="font-medium">{theme.rated_images_count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Average Rating:</span>
                    <span className="font-medium">
                      {theme.average_rating ? theme.average_rating.toFixed(1) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completion Rate:</span>
                    <span className="font-medium">
                      {(theme.completion_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Keyword Analysis */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Keyword Effectiveness</h2>
          
          {keywordAnalysis.length === 0 ? (
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="text-gray-500 text-lg mb-2">No keyword data available</div>
              <div className="text-gray-400 text-sm">
                Generate and rate some images to see keyword effectiveness analysis
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Keyword
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Uses
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Avg Rating
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Success Rate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confidence
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {keywordAnalysis.map((keyword, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-medium text-gray-900">
                            ##{keyword.keyword}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getCategoryColor(keyword.category)}`}>
                            {keyword.category}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {keyword.total_uses}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {keyword.average_rating.toFixed(1)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {(keyword.success_rate * 100).toFixed(1)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getConfidenceColor(keyword.confidence)}`}>
                            {keyword.confidence}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
