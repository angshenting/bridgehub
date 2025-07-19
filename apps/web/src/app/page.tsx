import { Suspense } from 'react'
import { DashboardStats } from '@/components/dashboard/dashboard-stats'
import { RecentEvents } from '@/components/dashboard/recent-events'
import { TopPlayers } from '@/components/dashboard/top-players'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

export default function HomePage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Bridge Platform
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Comprehensive tournament management for bridge players and clubs
        </p>
      </div>

      {/* Dashboard Stats */}
      <Suspense fallback={<LoadingSpinner />}>
        <DashboardStats />
      </Suspense>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Events */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold">Recent Events</h2>
          </div>
          <div className="card-body">
            <Suspense fallback={<LoadingSpinner />}>
              <RecentEvents />
            </Suspense>
          </div>
        </div>

        {/* Top Players */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold">Top Players</h2>
          </div>
          <div className="card-body">
            <Suspense fallback={<LoadingSpinner />}>
              <TopPlayers />
            </Suspense>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card hover:shadow-card-hover transition-shadow cursor-pointer">
          <div className="card-body text-center">
            <div className="text-3xl mb-4">🏆</div>
            <h3 className="text-lg font-semibold mb-2">Create Event</h3>
            <p className="text-gray-600">Set up a new tournament or club game</p>
          </div>
        </div>

        <div className="card hover:shadow-card-hover transition-shadow cursor-pointer">
          <div className="card-body text-center">
            <div className="text-3xl mb-4">👥</div>
            <h3 className="text-lg font-semibold mb-2">Manage Players</h3>
            <p className="text-gray-600">Add and update player information</p>
          </div>
        </div>

        <div className="card hover:shadow-card-hover transition-shadow cursor-pointer">
          <div className="card-body text-center">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="text-lg font-semibold mb-2">View Results</h3>
            <p className="text-gray-600">Browse tournament results and rankings</p>
          </div>
        </div>
      </div>
    </div>
  )
}