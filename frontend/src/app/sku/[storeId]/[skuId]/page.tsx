'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import type { SKUDetail, HourlyForecast } from '@/lib/types';
import { formatNumber, formatDate, getConfidenceColor } from '@/lib/utils';

export default function SKUDetailPage() {
  const params = useParams();
  const storeId = parseInt(params.storeId as string);
  const skuId = parseInt(params.skuId as string);

  const [data, setData] = useState<SKUDetail | null>(null);
  const [hourlyData, setHourlyData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [hourlyLoading, setHourlyLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHourly, setShowHourly] = useState(false);

  useEffect(() => {
    loadData();
  }, [storeId, skuId]);

  async function loadData() {
    try {
      setLoading(true);
      const response = await api.getSKUDetail(storeId, skuId, 30);
      setData(response);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  async function loadHourlyForecast() {
    if (hourlyData) {
      setShowHourly(!showHourly);
      return;
    }

    try {
      setHourlyLoading(true);
      const response = await api.getSKUHourlyForecast(storeId, skuId);
      setHourlyData(response);
      setShowHourly(true);
    } catch (err) {
      console.error('Failed to load hourly forecast:', err);
    } finally {
      setHourlyLoading(false);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading SKU details...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-red-800 font-semibold mb-2">Error Loading Data</h2>
            <p className="text-red-600">{error || 'SKU not found'}</p>
            <Link href="/" className="mt-4 inline-block px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">
              Back to Overview
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{data.sku.name}</h1>
              <p className="text-gray-600 mt-1">
                {data.store.name} • {data.sku.category}
                {data.sku.is_perishable && <span className="ml-2 text-orange-600">• Perishable</span>}
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

      <div className="max-w-7xl mx-auto px-8 py-6">
        {/* Current State Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white border rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">On Hand</p>
            <p className="text-2xl font-bold text-gray-900">{data.current_state.on_hand}</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Daily Demand</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(data.current_state.daily_demand, 1)}</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Days of Cover</p>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(data.current_state.days_of_cover, 1)}</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Confidence Score</p>
            <p className={`text-2xl font-bold ${getConfidenceColor(data.current_state.confidence_score)}`}>
              {formatNumber(data.current_state.confidence_score, 0)}% ({data.current_state.confidence_grade})
            </p>
          </div>
        </div>

        {/* Forecast Information */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Demand Forecast</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Weekday Average</p>
              <p className="text-lg font-semibold text-gray-900">{formatNumber(data.forecast.weekday_avg, 1)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Weekend Average</p>
              <p className="text-lg font-semibold text-gray-900">{formatNumber(data.forecast.weekend_avg, 1)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Forecast Confidence</p>
              <p className="text-lg font-semibold text-gray-900 capitalize">{data.forecast.confidence}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Data Points</p>
              <p className="text-lg font-semibold text-gray-900">{data.forecast.data_points}</p>
            </div>
          </div>

          {data.current_state.stockout_date && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm font-medium text-red-800">
                ⚠️ Predicted Stockout: {formatDate(data.current_state.stockout_date)}
              </p>
            </div>
          )}

          {/* Hourly Forecast Toggle */}
          <div className="mt-6 pt-4 border-t">
            <button
              onClick={loadHourlyForecast}
              disabled={hourlyLoading}
              className="px-4 py-2.5 bg-ncr-primary text-white rounded-lg hover:bg-ncr-primary-dark disabled:bg-gray-400 text-sm font-semibold shadow-sm"
            >
              {hourlyLoading ? 'Loading...' : showHourly ? 'Hide Hourly Forecast' : '⏰ View Hourly Forecast (Peak Hours)'}
            </button>
          </div>
        </div>

        {/* Hourly Forecast Section */}
        {showHourly && hourlyData && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Hourly Demand Forecast</h2>
            <p className="text-sm text-gray-600 mb-4">
              Predicted demand by hour. Peak hours (lunch 11am–2pm, dinner 5pm–8pm) in orange.
            </p>
            {hourlyData.hourly_forecast.every((f: any) => (f.predicted_demand || 0) === 0) && (
              <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
                No hourly history for this SKU; values are estimated from daily demand. Items with hourly data (e.g. Proteins, Salsas) show actual patterns.
              </div>
            )}

            {/* Current Inventory Status */}
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-blue-700 mb-1">Current On Hand</p>
                  <p className="text-2xl font-bold text-blue-900">{hourlyData.current_on_hand} units</p>
                </div>
                {hourlyData.stockout_prediction.will_stockout && (
                  <div>
                    <p className="text-sm text-red-700 mb-1">Predicted Stockout</p>
                    <p className="text-lg font-bold text-red-900">
                      {new Date(hourlyData.stockout_prediction.stockout_time).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}
                    </p>
                    {hourlyData.stockout_prediction.is_during_peak && (
                      <span className="text-xs font-semibold text-red-600">
                        ⚠️ DURING {hourlyData.stockout_prediction.peak_period?.toUpperCase()} RUSH
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Hourly Bar Chart */}
            <div className="space-y-2">
              {hourlyData.hourly_forecast.map((forecast: any, idx: number) => {
                const maxDemand = Math.max(...hourlyData.hourly_forecast.map((f: any) => f.predicted_demand || 0), 1);
                const widthPercent = ((forecast.predicted_demand || 0) / maxDemand) * 100;
                const willStockout = forecast.will_stockout_this_hour;

                return (
                  <div key={idx} className="flex items-center space-x-3">
                    <div className="w-16 text-sm font-medium text-gray-700">
                      {forecast.hour_display}
                    </div>
                    <div className="flex-1">
                      <div className="relative h-8 bg-gray-100 rounded overflow-hidden">
                        <div
                          className={`h-full transition-all ${
                            willStockout
                              ? 'bg-red-500'
                              : forecast.is_peak_hour
                              ? 'bg-orange-500'
                              : 'bg-blue-400'
                          }`}
                          style={{ width: `${widthPercent}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="w-24 text-right">
                      <span className="text-sm font-semibold text-gray-900">
                        {formatNumber(forecast.predicted_demand, 1)} units
                      </span>
                      {forecast.remaining_inventory !== undefined && (
                        <div className="text-xs text-gray-500">
                          ({formatNumber(forecast.remaining_inventory, 0)} left)
                        </div>
                      )}
                    </div>
                    {willStockout && (
                      <div className="text-xs font-bold text-red-600">
                        STOCKOUT
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="mt-6 flex items-center justify-center space-x-6 text-sm">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-blue-400 rounded mr-2"></div>
                <span className="text-gray-700">Regular Hours</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-orange-500 rounded mr-2"></div>
                <span className="text-gray-700">Peak Hours</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
                <span className="text-gray-700">Stockout</span>
              </div>
            </div>

            {/* Peak Hours Info */}
            <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded text-xs text-gray-600">
              <span className="font-semibold">Peak Hours:</span> Lunch (11am-2pm) and Dinner (5pm-8pm)
            </div>
          </div>
        )}

        {/* Anomalies */}
        {data.anomalies && data.anomalies.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Anomalies</h2>
            <div className="space-y-3">
              {data.anomalies.slice(0, 5).map((anomaly, idx) => (
                <div key={idx} className="border-l-4 border-red-400 pl-4 py-2">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-gray-900">{formatDate(anomaly.date)}</p>
                    <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800">
                      {anomaly.severity.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{anomaly.explanation}</p>
                  <p className="text-xs text-gray-500 mt-1">Residual: {formatNumber(anomaly.residual, 1)} units</p>
                </div>
              ))}
            </div>

            {data.anomaly_patterns.has_pattern && (
              <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded">
                <p className="text-sm font-medium text-orange-800">
                  🔍 Systematic Pattern Detected: {data.anomaly_patterns.frequency} anomalies in 30 days
                  (Total loss: {formatNumber(data.anomaly_patterns.total_loss, 0)} units)
                </p>
              </div>
            )}
          </div>
        )}

        {/* Recommendations */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h2>
          <div className="space-y-4">
            {/* Reorder Recommendation */}
            {data.recommendations.reorder.recommended && (
              <div className="border-l-4 border-blue-400 pl-4 py-3 bg-blue-50">
                <h3 className="font-semibold text-blue-900 mb-1">Reorder Recommended</h3>
                <p className="text-sm text-blue-800 mb-2">{data.recommendations.reorder.reason}</p>
                <p className="text-sm text-blue-700">
                  <span className="font-medium">Suggested Quantity:</span> {data.recommendations.reorder.qty} units
                </p>
              </div>
            )}

            {/* Transfer Recommendation */}
            {data.recommendations.transfer.recommended && (
              <div className="border-l-4 border-green-400 pl-4 py-3 bg-green-50">
                <h3 className="font-semibold text-green-900 mb-1">Transfer Available</h3>
                <p className="text-sm text-green-800">{data.recommendations.transfer.reason}</p>
                <Link
                  href="/transfers"
                  className="inline-block mt-2 text-sm text-green-700 hover:underline font-medium"
                >
                  View Transfer Recommendations →
                </Link>
              </div>
            )}

            {/* Cycle Count Recommendation */}
            {data.recommendations.cycle_count.recommended && (
              <div className="border-l-4 border-yellow-400 pl-4 py-3 bg-yellow-50">
                <h3 className="font-semibold text-yellow-900 mb-1">
                  Cycle Count Recommended ({data.recommendations.cycle_count.priority} Priority)
                </h3>
                <p className="text-sm text-yellow-800">{data.recommendations.cycle_count.reason}</p>
              </div>
            )}
          </div>
        </div>

        {/* Confidence Details */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Confidence Score Breakdown</h2>
          <p className="text-sm text-gray-600 mb-4">
            How much we trust that the on-hand number matches what’s on the shelf. Low score = schedule a physical count (cycle count).
          </p>
          <div className="space-y-2">
            {data.confidence_details.deductions.map((deduction, idx) => (
              <div key={idx} className="flex items-center text-sm">
                <span className="text-red-600 mr-2">−</span>
                <span className="text-gray-700">{deduction}</span>
              </div>
            ))}
          </div>
          {data.confidence_details.days_since_count !== null && (
            <p className="mt-4 text-sm text-gray-600">
              Last cycle count: {data.confidence_details.days_since_count} days ago
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
