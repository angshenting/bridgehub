'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

export function DashboardStats() {
  const { data: players, isLoading: playersLoading } = useQuery({
    queryKey: ['players'],
    queryFn: () => apiClient.getPlayers({ limit: 1000 }),
  })

  const { data: events, isLoading: eventsLoading } = useQuery({
    queryKey: ['events'],
    queryFn: () => apiClient.getEvents({ limit: 1000 }),
  })

  const { data: recentEvents, isLoading: recentLoading } = useQuery({
    queryKey: ['recent-events'],
    queryFn: () => apiClient.getRecentEvents(30),
  })

  if (playersLoading || eventsLoading || recentLoading) {
    return <LoadingSpinner />
  }

  const totalPlayers = players?.data?.length || 0
  const totalEvents = events?.data?.length || 0
  const recentEventsCount = recentEvents?.data?.length || 0
  const activePlayers = players?.data?.filter((p: any) => p.status === 'active').length || 0

  const stats = [
    {
      name: 'Total Players',
      value: totalPlayers,
      description: `${activePlayers} active`,
      icon: '👥',
    },
    {
      name: 'Total Events',
      value: totalEvents,
      description: 'All time',
      icon: '🏆',
    },
    {
      name: 'Recent Events',
      value: recentEventsCount,
      description: 'Last 30 days',
      icon: '📅',
    },
    {
      name: 'Activity Rate',
      value: totalEvents > 0 ? Math.round((recentEventsCount / totalEvents) * 100) : 0,
      description: 'Recent activity %',
      icon: '📊',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => (
        <div key={stat.name} className="card hover:shadow-card-hover transition-shadow">
          <div className="card-body">
            <div className="flex items-center">
              <div className="text-3xl mr-4">{stat.icon}</div>
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.description}</p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}