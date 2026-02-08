'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { TransferRecommendationsResponse, TransferRecommendation } from '@/lib/types';
import { formatNumber, formatCurrency } from '@/lib/utils';

export default function TransfersPage() {
  const [data, setData] = useState<TransferRecommendationsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const response = await api.getTransferRecommendations({ min_urgency: 0.5 });
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  async function createTransfer(rec: TransferRecommendation, index: number) {
    try {
      setCreating(index);
      await api.createTransferDraft({
        from_store_id: rec.from_store_id,
        to_store_id: rec.to_store_id,
        sku_id: rec.sku_id,
        qty: rec.qty
      });
      alert('Transfer draft created successfully!');
      await loadData();
    } catch (err) {
      alert('Failed to create transfer: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setCreating(null);
    }
  }

  function getUrgencyColor(score: number): string {
    if (score >= 0.8) return 'bg-red-100 text-red-800 border-red-200';
    if (score >= 0.6) return 'bg-orange-100 text-orange-800 border-orange-200';
    return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  }

  function getUrgencyLabel(score: number): string {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ncr-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading transfer recommendations...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-ncr-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-red-800 font-semibold mb-2">Error Loading Data</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={loadData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-ncr-gray-50">
      {/* Header */}
      <div className="bg-gradient-purple text-white">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Transfer Recommendations</h1>
              <p className="text-purple-100 text-lg">
                Optimize inventory by transferring between stores
              </p>
            </div>
            <Link
              href="/"
              className="px-6 py-3 bg-white text-ncr-primary rounded-lg hover:bg-ncr-gray-100 transition-colors font-semibold shadow-lg"
            >
              ← Back to Overview
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-6">
        {/* Summary Cards */}
        {data && data.summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-xl shadow-md p-6 border-t-4 border-ncr-primary hover:shadow-lg transition-shadow">
              <p className="text-sm text-ncr-primary font-semibold uppercase tracking-wide mb-2">Total Opportunities</p>
              <p className="text-4xl font-bold text-ncr-primary">{data.summary.total_opportunities}</p>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 border-t-4 border-red-500 hover:shadow-lg transition-shadow">
               <p className="text-sm text-red-600 font-semibold uppercase tracking-wide mb-2">High Urgency</p>
               <p className="text-4xl font-bold text-red-600">{data.summary.high_urgency}</p>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 border-t-4 border-ncr-secondary hover:shadow-lg transition-shadow">
               <p className="text-sm text-ncr-secondary font-semibold uppercase tracking-wide mb-2">Total Units</p>
               <p className="text-4xl font-bold text-ncr-secondary">{data.summary.total_units}</p>
            </div>
            <div className="bg-white rounded-xl shadow-md p-6 border-t-4 border-green-500 hover:shadow-lg transition-shadow">
               <p className="text-sm text-green-600 font-semibold uppercase tracking-wide mb-2">Est. Savings</p>
               <p className="text-4xl font-bold text-green-600">{formatCurrency(data.summary.estimated_savings)}</p>
            </div>
          </div>
        )}

        {/* Recommendations List */}
        <div className="space-y-4">
          {data?.recommendations.map((rec, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{rec.sku_name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded border ${getUrgencyColor(rec.urgency_score)}`}>
                        {getUrgencyLabel(rec.urgency_score)} Urgency
                      </span>
                    </div>
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">From:</span> {rec.from_store_name}
                      </div>
                      <div>→</div>
                      <div>
                        <span className="font-medium">To:</span> {rec.to_store_name}
                      </div>
                      <div>
                        <span className="font-medium">Qty:</span> {rec.qty} units
                      </div>
                      {rec.distance_km && (
                        <div>
                          <span className="font-medium">Distance:</span> {formatNumber(rec.distance_km, 0)} km
                        </div>
                      )}
                      {rec.transfer_cost && (
                        <div>
                          <span className="font-medium">Cost:</span> {formatCurrency(rec.transfer_cost)}
                        </div>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={() => createTransfer(rec, idx)}
                    disabled={creating === idx}
                    className="px-6 py-3 bg-gradient-purple text-white rounded-lg hover:bg-gradient-purple-dark disabled:bg-ncr-gray-400 disabled:cursor-not-allowed transition-all font-bold shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
                  >
                    {creating === idx ? 'Creating...' : 'Create Transfer'}
                  </button>
                </div>

                {/* Rationale */}
                <div className="bg-gray-50 rounded p-4 mb-4">
                  <p className="text-sm text-gray-700">{rec.rationale}</p>
                </div>

                {/* Impact Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="border-l-4 border-orange-400 pl-4">
                    <p className="text-xs text-gray-600 mb-1">Receiver Impact</p>
                    <p className="text-sm">
                      <span className="font-semibold text-orange-600">{formatNumber(rec.receiver_days_before, 1)} days</span>
                      {' → '}
                      <span className="font-semibold text-green-600">{formatNumber(rec.receiver_days_after, 1)} days</span>
                    </p>
                  </div>
                  <div className="border-l-4 border-blue-400 pl-4">
                    <p className="text-xs text-gray-600 mb-1">Donor Impact</p>
                    <p className="text-sm">
                      <span className="font-semibold text-blue-600">{formatNumber(rec.donor_days_before, 1)} days</span>
                      {' → '}
                      <span className="font-semibold text-gray-600">{formatNumber(rec.donor_days_after, 1)} days</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {data && data.recommendations.length === 0 && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Transfer Opportunities</h3>
            <p className="text-gray-600">All stores have balanced inventory levels</p>
          </div>
        )}
      </div>
    </main>
  );
}
