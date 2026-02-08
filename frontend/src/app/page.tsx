'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import type { OverviewResponse, InventoryItem } from '@/lib/types';
import { getRiskColor, getConfidenceColor, formatNumber, formatDate } from '@/lib/utils';

export default function Home() {
  const [data, setData] = useState<OverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskOnly, setRiskOnly] = useState(false);
  const [selectedStore, setSelectedStore] = useState<number | null>(null);
  const [stores, setStores] = useState<Array<{id: number, name: string}>>([
    { id: 1, name: 'Chipotle Athens Downtown' },
    { id: 2, name: 'Chipotle Athens Eastside' },
    { id: 3, name: 'Chipotle Athens West' },
    { id: 4, name: 'Chipotle Athens North' },
    { id: 5, name: 'Chipotle Athens South' },
  ]);

  useEffect(() => {
    loadData();
  }, [riskOnly, selectedStore]);

  async function loadData() {
    try {
      setLoading(true);
      const response = await api.getOverview({
        risk_only: riskOnly,
        store_id: selectedStore || undefined,
        limit: 50
      });
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-ncr-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
           <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ncr-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading inventory data...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
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
          <h1 className="text-4xl font-bold mb-2">
            Optimus Inventory Health Dashboard
          </h1>
          <p className="text-purple-100 text-lg">
            Predictive inventory management with anomaly detection
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-6">
        {/* Alerts Bar */}
        {data && data.alerts && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
           <div className="bg-white rounded-xl shadow-md p-6 border-t-4 border-red-500 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-red-600 font-medium">Critical Stockouts</p>
                  <p className="text-2xl font-bold text-red-700">{data.alerts.critical_stockouts}</p>
                </div>
                <div className="text-red-400">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-t-4 border-yellow-500 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-yellow-600 font-medium">Low Confidence</p>
                  <p className="text-2xl font-bold text-yellow-700">{data.alerts.low_confidence}</p>
                </div>
                <div className="text-yellow-400">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-md p-6 border-t-4 border-ncr-primary hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-ncr-primary font-semibold uppercase tracking-wide">Transfer Opportunities</p>
                  <p className="text-2xl font-bold text-ncr-primary">{data.alerts.transfer_opportunities}</p>
                </div>
                <div className="text-ncr-primary">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 5a1 1 0 100 2h5.586l-1.293 1.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L13.586 5H8zM12 15a1 1 0 100-2H6.414l1.293-1.293a1 1 0 10-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L6.414 15H12z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center space-x-4 flex-wrap gap-2">
              {/* Store Filter */}
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">Store:</label>
                <select
                  value={selectedStore || ''}
                  onChange={(e) => setSelectedStore(e.target.value ? parseInt(e.target.value) : null)}
                  className="rounded border-gray-300 text-sm py-1 px-2 border focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Stores</option>
                  {stores.map(store => (
                    <option key={store.id} value={store.id}>{store.name}</option>
                  ))}
                </select>
              </div>
              
              {/* Risk Filter */}
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={riskOnly}
                  onChange={(e) => setRiskOnly(e.target.checked)}
                  className="rounded border-ncr-gray-300 text-ncr-primary focus:ring-ncr-primary"
                />
                <span className="ml-2 text-sm text-gray-700">Show high-risk items only</span>
              </label>
            </div>
            
            <div className="flex space-x-2">
              <Link
                href="/peak-hours"
                className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 text-sm font-medium shadow-sm"
              >
                ⏰ Peak Hours
              </Link>
              <Link
                href="/transfers"
                className="px-6 py-3 bg-gradient-purple text-white rounded-lg hover:bg-gradient-purple-dark transition-all font-bold shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
              >
                View Transfers
              </Link>
              <Link
                href="/admin"
                className="px-6 py-3 bg-ncr-gray-700 text-white rounded-lg hover:bg-ncr-gray-800 transition-colors font-bold shadow-md"
              >
                Admin
              </Link>
            </div>
          </div>
          
          {/* Info Note */}
          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
            <span className="font-semibold">💡 Multi-Store View:</span> Each row represents inventory at a specific store. 
            The same ingredient may appear multiple times because each store has different stock levels, demand, and risk. 
            Use the store filter above to view a single location.
          </div>
        </div>

        {/* Inventory Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-ncr-gray-100">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">Store</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">SKU</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">On Hand</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">Demand/Day</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">Days Cover</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">Stockout Date</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">Confidence</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">Risk</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-ncr-dark uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data?.items.map((item, idx) => (
                  <tr key={`${item.store_id}-${item.sku_id}`} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{item.store_name}</div>
                      <div className="text-xs text-gray-500">Store ID: {item.store_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        href={`/sku/${item.store_id}/${item.sku_id}`}
                        className="text-sm text-ncr-primary hover:text-ncr-primary-dark hover:underline font-medium"
                      >
                        {item.sku_name}
                      </Link>
                      <div className="text-xs text-gray-500">{item.category}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.on_hand}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.daily_demand, 1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatNumber(item.days_of_cover, 1)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.stockout_date ? formatDate(item.stockout_date) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getConfidenceColor(item.confidence_score)}`}>
                        {formatNumber(item.confidence_score, 0)}% ({item.confidence_grade})
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded border ${getRiskColor(item.risk_level)}`}>
                        {item.risk_level.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.suggested_action}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data && data.items.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No inventory items found</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Showing {data?.items.length || 0} of {data?.total || 0} items</p>
        </div>
      </div>
    </main>
  );
}

