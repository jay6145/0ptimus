'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { DemoStats } from '@/lib/types';

export default function AdminPage() {
  const [stats, setStats] = useState<DemoStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  async function loadStats() {
    try {
      setLoading(true);
      const data = await api.getDemoStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }

  async function regenerateData() {
    if (!confirm('This will delete all existing data and generate new demo data. Continue?')) {
      return;
    }

    try {
      setRegenerating(true);
      await api.regenerateDemoData({
        num_stores: 5,
        num_skus: 200,
        days_history: 60
      });
      alert('Demo data regenerated successfully!');
      await loadStats();
    } catch (err) {
      alert('Failed to regenerate data: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setRegenerating(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading statistics...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Data Administration</h1>
              <p className="text-gray-600 mt-1">
                Manage demo data and view system statistics
              </p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              ← Back to Overview
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-8 py-6">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Database Statistics */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Database Statistics</h2>
          
          {stats && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="border rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Stores</p>
                <p className="text-2xl font-bold text-gray-900">{stats.stores}</p>
              </div>
              <div className="border rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">SKUs</p>
                <p className="text-2xl font-bold text-gray-900">{stats.skus}</p>
              </div>
              <div className="border rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Inventory Snapshots</p>
                <p className="text-2xl font-bold text-gray-900">{stats.inventory_snapshots.toLocaleString()}</p>
              </div>
              <div className="border rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Sales Records</p>
                <p className="text-2xl font-bold text-gray-900">{stats.sales_records.toLocaleString()}</p>
              </div>
              <div className="border rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Anomalies Detected</p>
                <p className="text-2xl font-bold text-red-600">{stats.anomalies}</p>
              </div>
              <div className="border rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Transfer Recommendations</p>
                <p className="text-2xl font-bold text-blue-600">{stats.transfer_recommendations}</p>
              </div>
            </div>
          )}

          {stats?.date_range && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Data Range:</span>{' '}
                {new Date(stats.date_range.start).toLocaleDateString()} to{' '}
                {new Date(stats.date_range.end).toLocaleDateString()}{' '}
                ({stats.date_range.days} days)
              </p>
            </div>
          )}
        </div>

        {/* Demo Data Generator */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Demo Data Generator</h2>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Warning</h3>
                <p className="mt-1 text-sm text-yellow-700">
                  Regenerating demo data will delete all existing data and create new synthetic data.
                  This action cannot be undone.
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">What will be generated:</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>5 stores with realistic locations (Atlanta, Boston, Chicago, Denver, Seattle)</li>
                <li>200 SKUs across 8 categories (Beverages, Snacks, Dairy, Produce, etc.)</li>
                <li>60 days of sales history with weekday/weekend patterns</li>
                <li>15-20 injected anomalies (shrink events, receiving errors, systematic patterns)</li>
                <li>5-8 transfer opportunities</li>
                <li>Cycle counts for ~20% of SKUs</li>
                <li>Store distance matrix for transfer optimization</li>
              </ul>
            </div>

            <button
              onClick={regenerateData}
              disabled={regenerating}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {regenerating ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Regenerating Data...
                </span>
              ) : (
                'Regenerate Demo Data'
              )}
            </button>
          </div>
        </div>

        {/* API Information */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">API Information</h2>
          
          <div className="space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-700">Backend API</p>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                http://localhost:8000/docs
              </a>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Health Check</p>
              <a
                href="http://localhost:8000/api/health"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                http://localhost:8000/api/health
              </a>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Version</p>
              <p className="text-sm text-gray-600">1.0.0</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
